"""Core orchestration pipeline for medical report extraction, parsing, and LLM explanation."""

import logging
import os
import time
from typing import Optional

from app.config import settings
from app.exceptions import (
    EmptyFileError,
    FileSizeExceededError,
    InsufficientTextQualityError,
    InvalidFileTypeError,
    LLMServiceError,
)
from app.extraction.image_ocr import extract_text_from_image
from app.extraction.pdf_extractor import extract_text_from_pdf
from app.llm.client import get_llm_client
from app.processing.findings_parser import extract_findings_from_pages, extract_report_date
from app.schemas import LLMExplanationPayload, MedicalTermExplanation, ReportAnalysis

logger = logging.getLogger(__name__)


def validate_file_input(
    file_bytes: bytes,
    filename: str,
    content_type: Optional[str] = None,
) -> str:
    """Validates file existence, size, and extension.

    Returns:
        Normalized file extension (e.g. '.pdf', '.png').

    Raises:
        EmptyFileError: If file is 0 bytes.
        FileSizeExceededError: If file exceeds maximum allowed limit.
        InvalidFileTypeError: If file extension or content_type is unsupported.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise EmptyFileError(filename)

    file_size = len(file_bytes)
    if file_size > settings.max_file_size_bytes:
        raise FileSizeExceededError(file_size, settings.max_file_size_bytes)

    _, ext = os.path.splitext(filename.lower())

    # Map content_type if filename lacks clear extension
    if not ext and content_type:
        mime_map = {
            "application/pdf": ".pdf",
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
        }
        ext = mime_map.get(content_type.lower(), "")

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise InvalidFileTypeError(filename, settings.ALLOWED_EXTENSIONS)

    return ext


def _create_fallback_explanation(findings_count: int, reason: str) -> LLMExplanationPayload:
    """Creates a safe, structured fallback explanation when LLM service is unavailable."""
    return LLMExplanationPayload(
        document_type="laboratory_report",
        summary=(
            f"Extraction completed successfully with {findings_count} test findings extracted directly from the report. "
            "Automated clinical explanation is currently in offline fallback mode."
        ),
        explanations=[],
        doctor_questions=[
            "Please review the extracted laboratory values directly with your physician.",
            "Ask your doctor if any repeated or confirmatory testing is needed.",
        ],
        limitations=[
            f"AI explanation service unavailable: {reason}. Extracted numerical findings are preserved verbatim."
        ],
    )


def process_medical_report(
    file_bytes: bytes,
    filename: str,
    content_type: Optional[str] = None,
) -> ReportAnalysis:
    """Synchronously processes a medical report file (PDF or image).

    This function is the primary integration contract for Member 2's backend.

    Args:
        file_bytes: Raw binary bytes of uploaded report.
        filename: Name of the uploaded file.
        content_type: Optional MIME content type (e.g. 'application/pdf').

    Returns:
        ReportAnalysis: Validated Pydantic response containing extraction, findings, and explanations.

    Raises:
        EmptyFileError: File is empty.
        FileSizeExceededError: File exceeds size limit.
        InvalidFileTypeError: Unsupported file format.
        CorruptedFileError: Damaged or unparseable file.
        InsufficientTextQualityError: File has no readable text or is illegible.
    """
    start_time = time.perf_counter()

    # 1. Validation
    ext = validate_file_input(file_bytes, filename, content_type)

    # 2. Text Extraction
    if ext == ".pdf":
        extraction_res = extract_text_from_pdf(file_bytes, filename=filename)
    else:
        extraction_res = extract_text_from_image(file_bytes, filename=filename)

    extracted_text = extraction_res["text"]
    if len(extracted_text.strip()) < settings.MIN_EXTRACTABLE_TEXT_CHARS:
        raise InsufficientTextQualityError(
            f"Extracted only {len(extracted_text.strip())} characters from '{filename}'. "
            "Document appears blank, illegible, or contains insufficient text for clinical interpretation."
        )

    # 3. Deterministic Findings Parsing
    findings = extract_findings_from_pages(extraction_res["pages"])
    report_date = extract_report_date(extracted_text)

    # 4. LLM Explanation
    llm_client = get_llm_client()
    status = "success"
    try:
        explanation = llm_client.generate_explanation(extracted_text, findings)
    except LLMServiceError as exc:
        logger.warning("LLM service error, falling back to extraction-only payload: %s", exc)
        explanation = _create_fallback_explanation(len(findings), str(exc))
        status = "partial"
    except Exception as exc:
        logger.warning("Unexpected error during LLM explanation generation: %s", exc)
        explanation = _create_fallback_explanation(len(findings), str(exc))
        status = "partial"

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return ReportAnalysis(
        status=status,
        document_type=explanation.document_type or "laboratory_report",
        extraction_method=extraction_res["method"],
        extracted_text=extracted_text,
        findings=findings,
        summary=explanation.summary,
        explanations=explanation.explanations,
        doctor_questions=explanation.doctor_questions,
        limitations=explanation.limitations,
        disclaimer="Informational only; not a substitute for professional medical advice. Always consult a qualified healthcare professional.",
        metadata={
            "filename": filename,
            "page_count": extraction_res.get("page_count", 1),
            "report_date": report_date,
            "findings_count": len(findings),
            "processing_time_ms": duration_ms,
            "llm_provider": settings.LLM_PROVIDER,
        },
    )


async def process_medical_report_async(
    file_bytes: bytes,
    filename: str,
    content_type: Optional[str] = None,
) -> ReportAnalysis:
    """Asynchronously processes a medical report file (PDF or image).

    Args:
        file_bytes: Raw binary bytes of uploaded report.
        filename: Name of the uploaded file.
        content_type: Optional MIME content type.

    Returns:
        ReportAnalysis: Validated Pydantic response model.
    """
    start_time = time.perf_counter()

    # 1. Validation
    ext = validate_file_input(file_bytes, filename, content_type)

    # 2. Text Extraction (CPU-bound, runs efficiently)
    if ext == ".pdf":
        extraction_res = extract_text_from_pdf(file_bytes, filename=filename)
    else:
        extraction_res = extract_text_from_image(file_bytes, filename=filename)

    extracted_text = extraction_res["text"]
    if len(extracted_text.strip()) < settings.MIN_EXTRACTABLE_TEXT_CHARS:
        raise InsufficientTextQualityError(
            f"Extracted only {len(extracted_text.strip())} characters from '{filename}'. "
            "Document appears blank, illegible, or contains insufficient text for clinical interpretation."
        )

    # 3. Deterministic Findings Parsing
    findings = extract_findings_from_pages(extraction_res["pages"])
    report_date = extract_report_date(extracted_text)

    # 4. Asynchronous LLM Call
    llm_client = get_llm_client()
    status = "success"
    try:
        explanation = await llm_client.generate_explanation_async(extracted_text, findings)
    except LLMServiceError as exc:
        logger.warning("LLM service error (async), falling back: %s", exc)
        explanation = _create_fallback_explanation(len(findings), str(exc))
        status = "partial"
    except Exception as exc:
        logger.warning("Unexpected error during async LLM explanation: %s", exc)
        explanation = _create_fallback_explanation(len(findings), str(exc))
        status = "partial"

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return ReportAnalysis(
        status=status,
        document_type=explanation.document_type or "laboratory_report",
        extraction_method=extraction_res["method"],
        extracted_text=extracted_text,
        findings=findings,
        summary=explanation.summary,
        explanations=explanation.explanations,
        doctor_questions=explanation.doctor_questions,
        limitations=explanation.limitations,
        disclaimer="Informational only; not a substitute for professional medical advice. Always consult a qualified healthcare professional.",
        metadata={
            "filename": filename,
            "page_count": extraction_res.get("page_count", 1),
            "report_date": report_date,
            "findings_count": len(findings),
            "processing_time_ms": duration_ms,
            "llm_provider": settings.LLM_PROVIDER,
        },
    )
