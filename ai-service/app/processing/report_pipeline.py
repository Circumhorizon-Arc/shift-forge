"""Core orchestration pipeline for medical report extraction, parsing, and LLM explanation."""

import logging
import os
import time
# pyrefly: ignore[missing-import]
import uuid
from typing import Any, Literal, Optional

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
from app.processing.findings_parser import (
    extract_findings_from_pages,
    extract_report_date,
)
from app.schemas import LLMExplanationPayload, ReportAnalysis
from app.tracker import AbstractTracker, UploadRecord, record_upload

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "Informational only; not a substitute for professional medical advice. "
    "Always consult a qualified healthcare professional."
)

INSUFFICIENT_TEXT_MESSAGE = (
    "The document contains insufficient readable text for clinical "
    "interpretation. Please upload a clearer, readable PDF or image."
)

SAFE_LLM_FALLBACK_REASON = (
    "The AI explanation service is temporarily unavailable. "
    "Extracted numerical findings are preserved verbatim."
)


def validate_file_input(
    file_bytes: bytes,
    filename: str,
    content_type: Optional[str] = None,
) -> str:
    """Validate file existence, size, and supported file type.

    Returns:
        The normalized extension, such as '.pdf' or '.png'.

    Raises:
        EmptyFileError: If the file is empty.
        FileSizeExceededError: If the file exceeds the configured limit.
        InvalidFileTypeError: If its extension or MIME type is unsupported.
    """
    if not file_bytes:
        # Avoid placing the caller-provided filename in the error.
        raise EmptyFileError()

    file_size = len(file_bytes)
    if file_size > settings.max_file_size_bytes:
        raise FileSizeExceededError(
            file_size,
            settings.max_file_size_bytes,
        )

    _, ext = os.path.splitext(filename.lower())

    # Infer the extension from the MIME type only if no extension exists.
    if not ext and content_type:
        mime_map = {
            "application/pdf": ".pdf",
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
        }
        ext = mime_map.get(content_type.lower(), "")

    if ext not in settings.ALLOWED_EXTENSIONS:
        # Do not pass the original filename into the public-facing error.
        raise InvalidFileTypeError(
            "uploaded file",
            settings.ALLOWED_EXTENSIONS,
        )

    return ext


def _create_fallback_explanation(
    findings_count: int,
) -> LLMExplanationPayload:
    """Create a safe fallback when AI-generated explanation is unavailable."""
    return LLMExplanationPayload(
        document_type="laboratory_report",
        summary=(
            f"Extraction completed successfully with {findings_count} "
            "test findings extracted directly from the report. "
            "Automated clinical explanation is currently in offline "
            "fallback mode."
        ),
        explanations=[],
        doctor_questions=[
            "Please review the extracted laboratory values directly "
            "with your physician.",
            "Ask your doctor if any repeated or confirmatory testing "
            "is needed.",
        ],
        limitations=[SAFE_LLM_FALLBACK_REASON],
    )


def _make_label(filename: str) -> str:
    """Return a non-identifying upload label without the original filename."""
    _, ext = os.path.splitext(filename.lower())

    # Retain only a supported extension; never retain filename components.
    allowed_extensions = {
        extension.lower() for extension in settings.ALLOWED_EXTENSIONS
    }
    safe_ext = ext if ext in allowed_extensions else ""

    return f"upload-{uuid.uuid4().hex[:12]}{safe_ext}"


def _check_text_quality(extracted_text: str) -> None:
    """Raise a generic error when extraction produces too little readable text."""
    if len(extracted_text.strip()) < settings.MIN_EXTRACTABLE_TEXT_CHARS:
        raise InsufficientTextQualityError(INSUFFICIENT_TEXT_MESSAGE)


def _generate_explanation(
    extracted_text: str,
    findings: list,
) -> tuple[LLMExplanationPayload, Literal["success", "partial", "error"]]:
    """Generate an explanation synchronously with a safe fallback."""
    try:
        explanation = get_llm_client().generate_explanation(
            extracted_text,
            findings,
        )
        return explanation, "success"
    except LLMServiceError:
        # Do not log provider exceptions; they can contain sensitive data.
        logger.warning(
            "LLM service unavailable; using extraction-only fallback."
        )
    except Exception:
        # Do not log raw unexpected exception messages.
        logger.exception(
            "Unexpected LLM processing failure; using extraction-only fallback."
        )

    return _create_fallback_explanation(len(findings)), "partial"


async def _generate_explanation_async(
    extracted_text: str,
    findings: list,
) -> tuple[LLMExplanationPayload, Literal["success", "partial", "error"]]:
    """Generate an explanation asynchronously with a safe fallback."""
    try:
        explanation = await get_llm_client().generate_explanation_async(
            extracted_text,
            findings,
        )
        return explanation, "success"
    except LLMServiceError:
        logger.warning(
            "LLM service unavailable during async processing; "
            "using extraction-only fallback."
        )
    except Exception:
        logger.exception(
            "Unexpected async LLM processing failure; "
            "using extraction-only fallback."
        )

    return _create_fallback_explanation(len(findings)), "partial"


def _build_result(
    *,
    extraction_res: dict[str, Any],
    extracted_text: str,
    findings: list,
    report_date: Optional[str],
    explanation: LLMExplanationPayload,
    pipeline_status: Literal["success", "partial", "error"],
    duration_ms: float,
    upload_label: str,
) -> ReportAnalysis:
    """Build the API response without returning the original filename."""
    return ReportAnalysis(
        status=pipeline_status,
        document_type=explanation.document_type or "laboratory_report",
        extraction_method=extraction_res["method"],
        extracted_text=extracted_text,
        findings=findings,
        summary=explanation.summary,
        explanations=explanation.explanations,
        doctor_questions=explanation.doctor_questions,
        limitations=explanation.limitations,
        disclaimer=DISCLAIMER,
        metadata={
            "upload_label": upload_label,
            "page_count": extraction_res.get("page_count", 1),
            "report_date": report_date,
            "findings_count": len(findings),
            "processing_time_ms": duration_ms,
            "llm_provider": settings.LLM_PROVIDER,
        },
    )


def _record_to_tracker(
    *,
    tracker: Optional[AbstractTracker],
    upload_label: str,
    content_type: Optional[str],
    file_bytes: bytes,
    extraction_res: dict[str, Any],
    result: ReportAnalysis,
    findings: list,
    pipeline_status: Literal["success", "partial", "error"],
    duration_ms: float,
    report_date: Optional[str],
) -> None:
    """Persist operational metadata without extracted report contents."""
    upload = UploadRecord(
        label=upload_label,
        content_type=content_type,
        file_size_bytes=len(file_bytes),
        extraction_method=extraction_res["method"],
        document_type=result.document_type,
        findings_count=len(findings),
        status=pipeline_status,
        processing_time_ms=duration_ms,
        page_count=extraction_res.get("page_count", 1),
        report_date=report_date,
        llm_provider=settings.LLM_PROVIDER,
    )

    try:
        if tracker is not None:
            tracker.record(upload)
        else:
            record_upload(upload)
    except Exception:
        # Tracker failures must not fail an otherwise successful analysis.
        logger.error("Failed to record upload metadata in tracker.")


def process_medical_report(
    file_bytes: bytes,
    filename: str,
    content_type: Optional[str] = None,
    *,
    tracker: Optional[AbstractTracker] = None,
) -> ReportAnalysis:
    """Synchronously process a medical report PDF or image."""
    start_time = time.perf_counter()

    # Keep the original filename only for internal validation/extraction.
    ext = validate_file_input(file_bytes, filename, content_type)
    upload_label = _make_label(filename)

    if ext == ".pdf":
        extraction_res = extract_text_from_pdf(
            file_bytes,
            filename=filename,
        )
    else:
        extraction_res = extract_text_from_image(
            file_bytes,
            filename=filename,
        )

    extracted_text = extraction_res["text"]
    _check_text_quality(extracted_text)

    findings = extract_findings_from_pages(extraction_res["pages"])
    report_date = extract_report_date(extracted_text)

    explanation, pipeline_status = _generate_explanation(
        extracted_text,
        findings,
    )

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    result = _build_result(
        extraction_res=extraction_res,
        extracted_text=extracted_text,
        findings=findings,
        report_date=report_date,
        explanation=explanation,
        pipeline_status=pipeline_status,
        duration_ms=duration_ms,
        upload_label=upload_label,
    )

    _record_to_tracker(
        tracker=tracker,
        upload_label=upload_label,
        content_type=content_type,
        file_bytes=file_bytes,
        extraction_res=extraction_res,
        result=result,
        findings=findings,
        pipeline_status=pipeline_status,
        duration_ms=duration_ms,
        report_date=report_date,
    )

    return result


async def process_medical_report_async(
    file_bytes: bytes,
    filename: str,
    content_type: Optional[str] = None,
    *,
    tracker: Optional[AbstractTracker] = None,
) -> ReportAnalysis:
    """Asynchronously process a medical report PDF or image."""
    start_time = time.perf_counter()

    ext = validate_file_input(file_bytes, filename, content_type)
    upload_label = _make_label(filename)

    if ext == ".pdf":
        extraction_res = extract_text_from_pdf(
            file_bytes,
            filename=filename,
        )
    else:
        extraction_res = extract_text_from_image(
            file_bytes,
            filename=filename,
        )

    extracted_text = extraction_res["text"]
    _check_text_quality(extracted_text)

    findings = extract_findings_from_pages(extraction_res["pages"])
    report_date = extract_report_date(extracted_text)

    explanation, pipeline_status = await _generate_explanation_async(
        extracted_text,
        findings,
    )

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    result = _build_result(
        extraction_res=extraction_res,
        extracted_text=extracted_text,
        findings=findings,
        report_date=report_date,
        explanation=explanation,
        pipeline_status=pipeline_status,
        duration_ms=duration_ms,
        upload_label=upload_label,
    )

    _record_to_tracker(
        tracker=tracker,
        upload_label=upload_label,
        content_type=content_type,
        file_bytes=file_bytes,
        extraction_res=extraction_res,
        result=result,
        findings=findings,
        pipeline_status=pipeline_status,
        duration_ms=duration_ms,
        report_date=report_date,
    )

    return result