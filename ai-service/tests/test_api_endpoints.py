"""Tests for standalone FastAPI API endpoints."""

import io
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.llm.client import MockLLMClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check_endpoint(client: TestClient):
    """Verify healthcheck endpoint returns healthy status and configuration diagnostics."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "healthsense-ai-service"
    assert "ocr_available" in data
    assert "llm_provider" in data


def test_api_upload_valid_pdf(client: TestClient, digital_pdf_bytes: bytes):
    """Verify POST /api/v1/report-analysis with a valid PDF upload."""
    files = {
        "file": ("jane_doe_lab.pdf", digital_pdf_bytes, "application/pdf")
    }
    with patch(
        "app.processing.report_pipeline.get_llm_client",
        return_value=MockLLMClient(),
    ):
        response = client.post("/api/v1/report-analysis", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["document_type"] == "laboratory_report"
    assert data["extraction_method"] == "pdf_text"
    assert len(data["findings"]) >= 5
    assert len(data["doctor_questions"]) > 0
    assert "disclaimer" in data


def test_api_upload_invalid_extension(client: TestClient):
    """Verify POST /api/v1/report-analysis returns 400 for unsupported extension."""
    files = {
        "file": ("notes.docx", b"some word document content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }
    response = client.post("/api/v1/report-analysis", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["error_code"] == "INVALID_FILE_TYPE"


def test_api_upload_empty_file(client: TestClient):
    """Verify POST /api/v1/report-analysis returns 400 for empty file."""
    files = {
        "file": ("empty.pdf", b"", "application/pdf")
    }
    response = client.post("/api/v1/report-analysis", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["error_code"] == "EMPTY_FILE"


def test_api_upload_corrupted_file(client: TestClient):
    """Verify POST /api/v1/report-analysis returns 400 for corrupted PDF."""
    files = {
        "file": ("corrupted.pdf", b"garbage non-pdf bytes", "application/pdf")
    }
    response = client.post("/api/v1/report-analysis", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["error_code"] == "CORRUPTED_FILE"
