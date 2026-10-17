"""Pydantic data models and schemas for HealthSense medical report processing."""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExtractionMethod(str, Enum):
    """Method used to extract text from the document."""

    PDF_TEXT = "pdf_text"
    OCR_IMAGE = "ocr_image"
    OCR_SCANNED_PDF = "ocr_scanned_pdf"
    HYBRID = "hybrid"


class DocumentType(str, Enum):
    """Categorized type of the medical document."""

    LABORATORY_REPORT = "laboratory_report"
    RADIOLOGY_REPORT = "radiology_report"
    CLINICAL_NOTE = "clinical_note"
    PRESCRIPTION = "prescription"
    GENERAL_MEDICAL_REPORT = "general_medical_report"
    UNKNOWN = "unknown"


class ExtractedFinding(BaseModel):
    """Individual test result or measurement extracted directly from the report."""

    model_config = ConfigDict(extra="forbid")

    test_name: str = Field(
        ...,
        description="Name of the test, analyte, or measurement (e.g. 'Hemoglobin', 'Creatinine')",
    )
    value: str = Field(
        ...,
        description="Measured or reported value as a string to preserve original formatting",
    )
    unit: Optional[str] = Field(
        default=None,
        description="Unit of measurement if present in the report (e.g. 'g/dL', 'mg/dL')",
    )
    reference_range: Optional[str] = Field(
        default=None,
        description="Laboratory reference range or interval if explicitly stated in report",
    )
    reported_flag: Optional[str] = Field(
        default=None,
        description="Explicit flag from original report (e.g. 'HIGH', 'LOW', 'H', 'L', 'CRITICAL', 'NORMAL')",
    )
    page_number: int = Field(
        default=1,
        ge=1,
        description="Page number where this finding was detected (1-indexed)",
    )
    source_text: str = Field(
        ...,
        description="Original verbatim snippet or line from the report for traceability",
    )


class MedicalTermExplanation(BaseModel):
    """Plain-language explanation of a medical term or finding."""

    model_config = ConfigDict(extra="forbid")

    term: str = Field(..., description="The medical term or test name explained")
    explanation: str = Field(
        ...,
        description="Clear, non-technical explanation suitable for a patient",
    )


class LLMExplanationPayload(BaseModel):
    """Structured response expected from the LLM."""

    model_config = ConfigDict(extra="ignore")

    document_type: str = Field(
        default="laboratory_report",
        description="Classified document type",
    )
    summary: str = Field(
        ...,
        description="Concise, patient-friendly summary of the report contents without diagnosis",
    )
    explanations: List[MedicalTermExplanation] = Field(
        default_factory=list,
        description="Plain-language definitions of medical terms present in the report",
    )
    doctor_questions: List[str] = Field(
        default_factory=list,
        description="3 to 5 thoughtful questions the patient can bring to their healthcare provider",
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Missing information, unreadable sections, or caveats noted in the report",
    )


class ReportAnalysis(BaseModel):
    """Comprehensive, validated response object returned by the report processing pipeline."""

    model_config = ConfigDict(extra="ignore")

    status: Literal["success", "partial", "error"] = Field(
        default="success",
        description="Execution status of the pipeline",
    )
    document_type: str = Field(
        default="laboratory_report",
        description="Identified document category (e.g. laboratory_report, general_medical_report)",
    )
    extraction_method: str = Field(
        ...,
        description="Extraction method utilized: 'pdf_text', 'ocr_image', 'ocr_scanned_pdf', 'hybrid'",
    )
    extracted_text: str = Field(
        ...,
        description="Complete sanitized extracted raw text from the document",
    )
    findings: List[ExtractedFinding] = Field(
        default_factory=list,
        description="List of structured findings extracted from the report",
    )
    summary: str = Field(
        ...,
        description="Plain-language patient-friendly summary of what the report contains",
    )
    explanations: List[MedicalTermExplanation] = Field(
        default_factory=list,
        description="Glossary of medical terms explained simply for the patient",
    )
    doctor_questions: List[str] = Field(
        default_factory=list,
        description="Suggested questions for consultation with a qualified doctor",
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Important uncertainties, unparsed values, or missing information",
    )
    disclaimer: str = Field(
        default="Informational only; not a substitute for professional medical advice. Always consult a qualified healthcare professional.",
        description="Mandatory clinical and legal disclaimer",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Technical processing metadata (filename, page count, processing time, etc.)",
    )


class ErrorResponse(BaseModel):
    """Standardized error response payload for API endpoints."""

    status: Literal["error"] = "error"
    error_code: str = Field(..., description="Unique machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[Any] = Field(default=None, description="Additional context or validation details")
