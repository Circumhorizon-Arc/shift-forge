"""LLM client implementations for medical report plain-language explanations."""

import abc
import json
import logging
import re
from typing import List, Optional
import httpx
from pydantic import ValidationError

from app.config import settings
from app.exceptions import LLMServiceError, LLMTimeoutError, LLMValidationError
from app.llm.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.schemas import ExtractedFinding, LLMExplanationPayload, MedicalTermExplanation

logger = logging.getLogger(__name__)


def extract_json_from_llm_response(text: str) -> dict:
    """Extracts and parses JSON object from LLM response text, stripping markdown codeblocks."""
    cleaned = text.strip()
    # Check for markdown json block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Fall back to finding the outermost braces
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = cleaned[start : end + 1]
        else:
            json_str = cleaned

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise LLMValidationError(f"Failed to parse JSON from LLM response: {exc}")


class BaseLLMClient(abc.ABC):
    """Abstract interface for LLM report explanation clients."""

    @abc.abstractmethod
    def generate_explanation(
        self,
        report_text: str,
        findings: List[ExtractedFinding],
    ) -> LLMExplanationPayload:
        """Synchronously generates a structured explanation."""
        pass

    @abc.abstractmethod
    async def generate_explanation_async(
        self,
        report_text: str,
        findings: List[ExtractedFinding],
    ) -> LLMExplanationPayload:
        """Asynchronously generates a structured explanation."""
        pass


class MockLLMClient(BaseLLMClient):
    """Deterministic, local mock LLM client.

    Generates realistic, medically cautious explanations and relevant questions
    without requiring API keys or external network connections. Ideal for testing and CI.
    """

    # Knowledge dictionary for standard medical laboratory tests
    TERM_GLOSSARY = {
        "hemoglobin": "A protein in your red blood cells that carries oxygen from your lungs to the rest of your body.",
        "glucose": "The main type of sugar in the blood and the primary source of energy for your body's cells.",
        "fasting glucose": "Blood sugar measured after an overnight fast, commonly evaluated for diabetes screening.",
        "wbc": "White blood cells, which help the immune system fight infections and diseases.",
        "white blood cells": "Cells produced in bone marrow that help defend the body against infections.",
        "platelet": "Small cell fragments essential for normal blood clotting and stopping bleeding.",
        "creatinine": "A waste product from muscle breakdown that is filtered out by healthy kidneys.",
        "bun": "Blood Urea Nitrogen, a measurement of urea nitrogen waste in blood indicating kidney function.",
        "cholesterol": "A fat-like substance found in your blood used to build cells and hormones.",
        "total cholesterol": "The total amount of cholesterol in your blood, including HDL, LDL, and VLDL.",
        "hdl": "High-density lipoprotein, often called 'good' cholesterol because it helps remove other forms of cholesterol.",
        "ldl": "Low-density lipoprotein, often called 'bad' cholesterol because high levels can cause plaque buildup.",
        "triglycerides": "A type of fat found in your blood stored in fat cells for future energy.",
        "tsh": "Thyroid Stimulating Hormone, produced by the pituitary gland to regulate thyroid activity.",
        "alt": "Alanine aminotransferase, an enzyme found mainly in the liver that assists in liver health evaluation.",
        "ast": "Aspartate aminotransferase, an enzyme in liver and heart cells evaluated alongside ALT.",
        "hba1c": "Glycated hemoglobin, reflecting average blood sugar levels over the past 2 to 3 months.",
        "sodium": "An essential electrolyte that maintains proper water balance and nerve function.",
        "potassium": "An essential electrolyte crucial for normal heart rhythm and muscle contraction.",
    }

    def _build_payload(self, report_text: str, findings: List[ExtractedFinding]) -> LLMExplanationPayload:
        flagged_findings = [f for f in findings if f.reported_flag and f.reported_flag.upper() not in ("NORMAL",)]

        # Construct explanations for terms encountered
        explanations: List[MedicalTermExplanation] = []
        seen_terms = set()

        for finding in findings:
            name_lower = finding.test_name.lower()
            matched = False
            for key, desc in self.TERM_GLOSSARY.items():
                if key in name_lower and key not in seen_terms:
                    seen_terms.add(key)
                    explanations.append(MedicalTermExplanation(term=finding.test_name, explanation=desc))
                    matched = True
                    break
            if not matched and finding.test_name not in seen_terms and len(explanations) < 6:
                seen_terms.add(finding.test_name)
                explanations.append(
                    MedicalTermExplanation(
                        term=finding.test_name,
                        explanation=f"A laboratory measurement reported with value {finding.value} {finding.unit or ''}.",
                    )
                )

        # Generate targeted consultation questions
        questions: List[str] = [
            "What do these overall results mean in the context of my symptoms, medical history, and daily routine?",
        ]

        if flagged_findings:
            flag_names = ", ".join([f.test_name for f in flagged_findings[:3]])
            questions.append(
                f"The report notes flags for {flag_names}. What might be contributing to these values?"
            )
            questions.append(
                "Are there any follow-up tests, dietary adjustments, or lifestyle factors we should review?"
            )
        else:
            questions.append(
                "Do any of these values indicate areas where repeat testing or monitoring is recommended?"
            )
            questions.append(
                "Are there specific reference ranges for my age and demographic that we should consider?"
            )

        # Document limitations
        limitations: List[str] = []
        missing_refs = [f.test_name for f in findings if not f.reference_range]
        if missing_refs:
            limitations.append(
                f"Reference ranges were not explicitly stated for: {', '.join(missing_refs[:4])}."
            )
        if not findings:
            limitations.append(
                "No individual numerical test findings could be matched using standard laboratory tables."
            )

        summary = (
            f"This medical report contains {len(findings)} identified test measurements. "
            f"Key parameters include {', '.join([f.test_name for f in findings[:4]]) if findings else 'clinical text'}. "
            "Please review all values and reference intervals directly with your healthcare provider."
        )

        return LLMExplanationPayload(
            document_type="laboratory_report",
            summary=summary,
            explanations=explanations[:8],
            doctor_questions=questions[:5],
            limitations=limitations,
        )

    def generate_explanation(
        self,
        report_text: str,
        findings: List[ExtractedFinding],
    ) -> LLMExplanationPayload:
        return self._build_payload(report_text, findings)

    async def generate_explanation_async(
        self,
        report_text: str,
        findings: List[ExtractedFinding],
    ) -> LLMExplanationPayload:
        return self._build_payload(report_text, findings)


class OpenAILLMClient(BaseLLMClient):
    """Client for OpenAI and OpenAI-compatible API providers (Ollama, Groq, Azure, vLLM)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = (base_url or settings.OPENAI_BASE_URL).rstrip("/")
        self.model = model or settings.OPENAI_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

        if not self.api_key:
            raise LLMServiceError("OPENAI_API_KEY is not configured.", provider="openai")

    def _prepare_messages(self, report_text: str, findings: List[ExtractedFinding]) -> List[dict]:
        findings_summary = "\n".join(
            [
                f"- {f.test_name}: {f.value} {f.unit or ''} (Ref: {f.reference_range or 'N/A'}, Flag: {f.reported_flag or 'None'})"
                for f in findings
            ]
        ) or "None structured."

        user_content = USER_PROMPT_TEMPLATE.format(
            report_text=report_text,
            findings_summary=findings_summary,
        )

        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

    def generate_explanation(
        self,
        report_text: str,
        findings: List[ExtractedFinding],
    ) -> LLMExplanationPayload:
        messages = self._prepare_messages(report_text, findings)
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": settings.LLM_TEMPERATURE,
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=body, headers=headers)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = extract_json_from_llm_response(content)
                return LLMExplanationPayload.model_validate(parsed)
        except httpx.TimeoutException:
            raise LLMTimeoutError(self.timeout)
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            raise LLMServiceError(f"OpenAI API request failed: {exc}", provider="openai")
        except ValidationError as exc:
            raise LLMValidationError(f"OpenAI response schema invalid: {exc}")

    async def generate_explanation_async(
        self,
        report_text: str,
        findings: List[ExtractedFinding],
    ) -> LLMExplanationPayload:
        messages = self._prepare_messages(report_text, findings)
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": settings.LLM_TEMPERATURE,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=body, headers=headers)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = extract_json_from_llm_response(content)
                return LLMExplanationPayload.model_validate(parsed)
        except httpx.TimeoutException:
            raise LLMTimeoutError(self.timeout)
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            raise LLMServiceError(f"OpenAI API async request failed: {exc}", provider="openai")
        except ValidationError as exc:
            raise LLMValidationError(f"OpenAI response schema invalid: {exc}")


class GeminiLLMClient(BaseLLMClient):
    """Client for Google Gemini API via official REST endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

        if not self.api_key:
            raise LLMServiceError("GEMINI_API_KEY is not configured.", provider="gemini")

    def _prepare_prompt(self, report_text: str, findings: List[ExtractedFinding]) -> str:
        findings_summary = "\n".join(
            [
                f"- {f.test_name}: {f.value} {f.unit or ''} (Ref: {f.reference_range or 'N/A'}, Flag: {f.reported_flag or 'None'})"
                for f in findings
            ]
        ) or "None structured."

        user_content = USER_PROMPT_TEMPLATE.format(
            report_text=report_text,
            findings_summary=findings_summary,
        )
        return f"{SYSTEM_PROMPT}\n\n{user_content}"

    def generate_explanation(
        self,
        report_text: str,
        findings: List[ExtractedFinding],
    ) -> LLMExplanationPayload:
        prompt = self._prepare_prompt(report_text, findings)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": settings.LLM_TEMPERATURE,
                "response_mime_type": "application/json",
            },
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=body)
                response.raise_for_status()
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = extract_json_from_llm_response(text)
                return LLMExplanationPayload.model_validate(parsed)
        except httpx.TimeoutException:
            raise LLMTimeoutError(self.timeout)
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            raise LLMServiceError(f"Gemini API request failed: {exc}", provider="gemini")
        except ValidationError as exc:
            raise LLMValidationError(f"Gemini response schema invalid: {exc}")

    async def generate_explanation_async(
        self,
        report_text: str,
        findings: List[ExtractedFinding],
    ) -> LLMExplanationPayload:
        prompt = self._prepare_prompt(report_text, findings)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": settings.LLM_TEMPERATURE,
                "response_mime_type": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=body)
                response.raise_for_status()
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = extract_json_from_llm_response(text)
                return LLMExplanationPayload.model_validate(parsed)
        except httpx.TimeoutException:
            raise LLMTimeoutError(self.timeout)
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            raise LLMServiceError(f"Gemini API async request failed: {exc}", provider="gemini")
        except ValidationError as exc:
            raise LLMValidationError(f"Gemini response schema invalid: {exc}")


def get_llm_client() -> BaseLLMClient:
    """Factory function returning the configured LLM client instance."""
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openai":
        return OpenAILLMClient()
    elif provider == "gemini":
        return GeminiLLMClient()
    return MockLLMClient()
