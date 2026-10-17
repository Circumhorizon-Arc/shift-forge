"""Unit tests for Pydantic schema validation."""

# pyrefly: ignore[missing-import]
import pytest
# pyrefly: ignore[missing-import]
from pydantic import ValidationError
# pyrefly: ignore[missing-import]
from app.schemas import (
    # pyrefly: ignore[missing-import]
    ExtractedFinding,
    # pyrefly: ignore[missing-import]
    MedicalTermExplanation,
    # pyrefly: ignore[missing-import]
    ReportAnalysis,
    # pyrefly: ignore[missing-import]
    ExtractionMethod,
    # pyrefly: ignore[missing-import]
    ErrorResponse,
)


def test_extracted_finding_valid_complete():
    """Verify finding model with all fields populated."""
    finding = ExtractedFinding(
        test_name="Hemoglobin",
        value="14.2",
        unit="g/dL",
        reference_range="13.5 - 17.5",
        reported_flag="NORMAL",
        page_number=1,
        source_text="Hemoglobin 14.2 g/dL 13.5-17.5 NORMAL",
    )
    assert finding.test_name == "Hemoglobin"
    assert finding.value == "14.2"
    assert finding.unit == "g/dL"
    assert finding.reference_range == "13.5 - 17.5"
    assert finding.reported_flag == "NORMAL"
    assert finding.page_number == 1


def test_extracted_finding_nullable_fields():
    """Verify that unit, reference_range, and reported_flag are properly optional/nullable."""
    finding = ExtractedFinding(
        test_name="Blood Pressure",
        value="120/80",
        source_text="Blood Pressure: 120/80",
    )
    assert finding.unit is None
    assert finding.reference_range is None
    assert finding.reported_flag is None
    assert finding.page_number == 1


def test_extracted_finding_requires_mandatory_fields():
    """Verify validation errors when test_name or value or source_text are missing."""
    with pytest.raises(ValidationError):
        ExtractedFinding(test_name="Glucose", source_text="Glucose")  # type: ignore[call-arg]  # Missing value

    with pytest.raises(ValidationError):
        ExtractedFinding(value="105", source_text="105")  # type: ignore[call-arg]  # Missing test_name


def test_report_analysis_schema_complete():
    """Test full ReportAnalysis construction and serialization."""
    analysis = ReportAnalysis(
        status="success",
        document_type="laboratory_report",
        extraction_method="pdf_text",
        extracted_text="Hemoglobin: 14.2 g/dL",
        findings=[
            ExtractedFinding(
                test_name="Hemoglobin",
                value="14.2",
                unit="g/dL",
                reference_range="13.5-17.5",
                reported_flag=None,
                page_number=1,
                source_text="Hemoglobin: 14.2 g/dL (13.5-17.5)",
            )
        ],
        summary="A laboratory report testing hemoglobin levels.",
        explanations=[
            MedicalTermExplanation(
                term="Hemoglobin",
                explanation="An oxygen-carrying protein in red blood cells.",
            )
        ],
        doctor_questions=["Are my hemoglobin levels appropriate?"],
        limitations=["Only one test result provided."],
        metadata={"filename": "sample.pdf", "page_count": 1},
    )

    dumped = analysis.model_dump()
    assert dumped["status"] == "success"
    assert dumped["extraction_method"] == "pdf_text"
    assert len(dumped["findings"]) == 1
    assert dumped["findings"][0]["test_name"] == "Hemoglobin"
    assert "disclaimer" in dumped
    assert "Informational only" in dumped["disclaimer"]


def test_error_response_schema():
    """Test ErrorResponse schema creation."""
    err = ErrorResponse(
        error_code="INVALID_FILE_TYPE",
        message="Only PDF, PNG, JPG files are supported",
        details={"extension": ".docx"},
    )
    assert err.status == "error"
    assert err.error_code == "INVALID_FILE_TYPE"
    assert err.details is not None and err.details["extension"] == ".docx"
