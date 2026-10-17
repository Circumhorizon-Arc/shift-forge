"""Tests for LLM client error handling and pipeline fallback behavior."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from pydantic import ValidationError

from app.exceptions import LLMServiceError, LLMTimeoutError, LLMValidationError
from app.llm.client import (
    GeminiLLMClient,
    MockLLMClient,
    OpenAILLMClient,
    extract_json_from_llm_response,
    get_llm_client,
)
from app.processing.report_pipeline import process_medical_report, process_medical_report_async
from app.tracker import NoOpTracker
from tests.conftest import create_synthetic_digital_pdf, SAMPLE_LAB_REPORT_TEXT


# ---------------------------------------------------------------------------
# JSON extraction helper
# ---------------------------------------------------------------------------

def test_extract_json_plain():
    raw = '{"summary": "ok", "document_type": "x", "explanations": [], "doctor_questions": [], "limitations": []}'
    assert extract_json_from_llm_response(raw)["summary"] == "ok"


def test_extract_json_markdown_fence():
    raw = '```json\n{"summary": "fenced", "document_type": "x", "explanations": [], "doctor_questions": [], "limitations": []}\n```'
    assert extract_json_from_llm_response(raw)["summary"] == "fenced"


def test_extract_json_invalid_raises():
    with pytest.raises(LLMValidationError):
        extract_json_from_llm_response("not json at all")


# ---------------------------------------------------------------------------
# MockLLMClient
# ---------------------------------------------------------------------------

class TestMockLLMClient:
    def test_generate_explanation_returns_payload(self):
        from app.schemas import ExtractedFinding
        client = MockLLMClient()
        findings = [
            ExtractedFinding(
                test_name="Hemoglobin",
                value="14.2",
                unit="g/dL",
                reference_range="13.5-17.5",
                reported_flag="NORMAL",
                source_text="Hemoglobin 14.2 g/dL",
            )
        ]
        payload = client.generate_explanation("some report text", findings)
        assert payload.summary
        assert len(payload.doctor_questions) >= 1

    @pytest.mark.asyncio
    async def test_generate_explanation_async_returns_payload(self):
        from app.schemas import ExtractedFinding
        client = MockLLMClient()
        findings = [
            ExtractedFinding(
                test_name="Glucose",
                value="112",
                unit="mg/dL",
                reference_range="70-99",
                reported_flag="HIGH",
                source_text="Glucose 112 mg/dL HIGH",
            )
        ]
        payload = await client.generate_explanation_async("report text", findings)
        assert payload.summary
        assert isinstance(payload.limitations, list)


# ---------------------------------------------------------------------------
# get_llm_client factory
# ---------------------------------------------------------------------------

def test_get_llm_client_mock():
    with patch("app.llm.client.settings") as s:
        s.LLM_PROVIDER = "mock"
        assert isinstance(get_llm_client(), MockLLMClient)


def test_get_llm_client_gemini_missing_key():
    with patch("app.llm.client.settings") as s:
        s.LLM_PROVIDER = "gemini"
        s.GEMINI_API_KEY = None
        s.GEMINI_MODEL = "gemini-1.5-flash"
        s.LLM_TIMEOUT_SECONDS = 30.0
        with pytest.raises(LLMServiceError, match="GEMINI_API_KEY"):
            get_llm_client()


def test_get_llm_client_openai_missing_key():
    with patch("app.llm.client.settings") as s:
        s.LLM_PROVIDER = "openai"
        s.OPENAI_API_KEY = None
        s.OPENAI_BASE_URL = "https://api.openai.com/v1"
        s.OPENAI_MODEL = "gpt-4o-mini"
        s.LLM_TIMEOUT_SECONDS = 30.0
        with pytest.raises(LLMServiceError, match="OPENAI_API_KEY"):
            get_llm_client()


# ---------------------------------------------------------------------------
# GeminiLLMClient — mocked HTTP
# ---------------------------------------------------------------------------

_VALID_GEMINI_RESPONSE = {
    "candidates": [{
        "content": {
            "parts": [{
                "text": '{"document_type":"laboratory_report","summary":"All looks normal","explanations":[],"doctor_questions":["Ask your doctor."],"limitations":[]}'
            }]
        }
    }]
}


class TestGeminiLLMClientErrors:
    """Unit tests that mock httpx — no real network calls are made."""

    def _make_client(self):
        with patch("app.llm.client.settings") as s:
            s.GEMINI_API_KEY = "test-api-key"
            s.GEMINI_MODEL = "gemini-1.5-flash"
            s.LLM_TIMEOUT_SECONDS = 5.0
            s.LLM_TEMPERATURE = 0.1
            return GeminiLLMClient(api_key="test-api-key", model="gemini-1.5-flash", timeout=5.0)

    def test_timeout_raises_llm_timeout_error(self):
        client = self._make_client()
        with patch("httpx.Client") as MockClient:
            mock_instance = MockClient.return_value.__enter__.return_value
            mock_instance.post.side_effect = httpx.TimeoutException("timed out")
            with pytest.raises(LLMTimeoutError):
                client.generate_explanation("text", [])

    def test_http_status_error_raises_llm_service_error(self):
        client = self._make_client()
        with patch("httpx.Client") as MockClient:
            mock_instance = MockClient.return_value.__enter__.return_value
            resp = MagicMock()
            resp.status_code = 429
            mock_instance.post.side_effect = httpx.HTTPStatusError(
                "rate limited", request=MagicMock(), response=resp
            )
            exc = None
            try:
                client.generate_explanation("text", [])
            except LLMServiceError as e:
                exc = e
            assert exc is not None
            # Error message must NOT contain the API key
            assert "test-api-key" not in str(exc)
            assert "429" in str(exc)

    def test_network_error_raises_llm_service_error(self):
        client = self._make_client()
        with patch("httpx.Client") as MockClient:
            mock_instance = MockClient.return_value.__enter__.return_value
            mock_instance.post.side_effect = httpx.ConnectError("connection refused")
            with pytest.raises(LLMServiceError):
                client.generate_explanation("text", [])

    def test_gemini_api_key_not_in_request_url(self):
        """Verify the API key is sent in a header, not the URL query string."""
        client = self._make_client()
        captured_kwargs = {}

        def capture_post(url, **kwargs):
            captured_kwargs["url"] = url
            captured_kwargs["headers"] = kwargs.get("headers", {})
            mock_resp = MagicMock()
            mock_resp.json.return_value = _VALID_GEMINI_RESPONSE
            mock_resp.raise_for_status = lambda: None
            return mock_resp

        with patch("httpx.Client") as MockClient:
            mock_instance = MockClient.return_value.__enter__.return_value
            mock_instance.post.side_effect = capture_post
            client.generate_explanation("text", [])

        assert "test-api-key" not in captured_kwargs.get("url", "")
        assert captured_kwargs.get("headers", {}).get("x-goog-api-key") == "test-api-key"

    @pytest.mark.asyncio
    async def test_async_timeout_raises_llm_timeout_error(self):
        client = self._make_client()
        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_instance
            mock_instance.post.side_effect = httpx.TimeoutException("async timeout")
            with pytest.raises(LLMTimeoutError):
                await client.generate_explanation_async("text", [])

    @pytest.mark.asyncio
    async def test_async_http_error_raises_llm_service_error(self):
        client = self._make_client()
        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_instance
            resp = MagicMock()
            resp.status_code = 503
            mock_instance.post.side_effect = httpx.HTTPStatusError(
                "service unavailable", request=MagicMock(), response=resp
            )
            with pytest.raises(LLMServiceError):
                await client.generate_explanation_async("text", [])


# ---------------------------------------------------------------------------
# Pipeline fallback behavior
# ---------------------------------------------------------------------------

_PDF_BYTES = create_synthetic_digital_pdf([SAMPLE_LAB_REPORT_TEXT])
_NOOP = NoOpTracker()


def test_pipeline_partial_on_llm_timeout():
    """LLM timeout → status=partial, findings preserved, limitations explain fallback."""
    with patch("app.processing.report_pipeline.get_llm_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.generate_explanation.side_effect = LLMTimeoutError(30.0)
        mock_factory.return_value = mock_client

        result = process_medical_report(
            _PDF_BYTES, filename="timeout-test.pdf", tracker=_NOOP
        )

    assert result.status == "partial"
    assert len(result.findings) >= 5
    assert any("unavailable" in lim for lim in result.limitations)
    assert "Informational only" in result.disclaimer
    # Provider identity is preserved in metadata
    assert "llm_provider" in result.metadata


def test_pipeline_partial_on_llm_service_error():
    """LLM service error → status=partial, extraction results intact."""
    with patch("app.processing.report_pipeline.get_llm_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.generate_explanation.side_effect = LLMServiceError(
            "rate limited", provider="gemini"
        )
        mock_factory.return_value = mock_client

        result = process_medical_report(
            _PDF_BYTES, filename="rate-limited.pdf", tracker=_NOOP
        )

    assert result.status == "partial"
    assert len(result.findings) >= 5


def test_pipeline_partial_on_unexpected_llm_exception():
    """Unexpected LLM exception → status=partial (never crashes the pipeline)."""
    with patch("app.processing.report_pipeline.get_llm_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.generate_explanation.side_effect = RuntimeError("unexpected crash")
        mock_factory.return_value = mock_client

        result = process_medical_report(
            _PDF_BYTES, filename="unexpected-error.pdf", tracker=_NOOP
        )

    assert result.status == "partial"


def test_pipeline_success_status_not_faked():
    """When LLM succeeds, status must be 'success', not 'partial'."""
    with patch("app.processing.report_pipeline.get_llm_client", return_value=MockLLMClient()):
        result = process_medical_report(
            _PDF_BYTES, filename="success.pdf", tracker=_NOOP
        )
    assert result.status == "success"
    assert result.metadata["llm_provider"] is not None


@pytest.mark.asyncio
async def test_async_pipeline_partial_on_llm_timeout():
    """Async pipeline: LLM timeout → status=partial."""
    with patch("app.processing.report_pipeline.get_llm_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.generate_explanation_async = AsyncMock(
            side_effect=LLMTimeoutError(30.0)
        )
        mock_factory.return_value = mock_client

        result = await process_medical_report_async(
            _PDF_BYTES, filename="async-timeout.pdf", tracker=_NOOP
        )

    assert result.status == "partial"
    assert len(result.findings) >= 5


def test_fallback_summary_does_not_claim_llm_success():
    """Fallback summary must not claim that AI explanation was generated."""
    with patch("app.processing.report_pipeline.get_llm_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.generate_explanation.side_effect = LLMServiceError(
            "unavailable", provider="gemini"
        )
        mock_factory.return_value = mock_client

        result = process_medical_report(
            _PDF_BYTES, filename="fallback-summary-check.pdf", tracker=_NOOP
        )

    # The fallback summary must explicitly indicate offline/fallback mode
    assert "fallback" in result.summary.lower() or "offline" in result.summary.lower()


def test_extraction_succeeds_independently_of_llm():
    """Deterministic extraction (findings) must complete regardless of LLM outcome."""
    with patch("app.processing.report_pipeline.get_llm_client") as mock_factory:
        mock_client = MagicMock()
        mock_client.generate_explanation.side_effect = LLMServiceError(
            "down", provider="gemini"
        )
        mock_factory.return_value = mock_client

        result = process_medical_report(
            _PDF_BYTES, filename="extraction-independence.pdf", tracker=_NOOP
        )

    # Findings from PDF text extraction must survive LLM failure
    assert len(result.findings) >= 5
    assert result.extraction_method == "pdf_text"
