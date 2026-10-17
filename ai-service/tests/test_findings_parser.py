"""Tests for deterministic medical findings parser."""

from app.processing.findings_parser import (
    extract_findings_from_pages,
    extract_report_date,
    parse_finding_from_line,
)


def test_parse_finding_standard_columnar():
    """Test standard lab test line with name, value, unit, range, and flag."""
    line = "Hemoglobin 14.2 g/dL 13.5 - 17.5 NORMAL"
    finding = parse_finding_from_line(line, page_number=1)
    assert finding is not None
    assert finding.test_name == "Hemoglobin"
    assert finding.value == "14.2"
    assert finding.unit == "g/dL"
    assert finding.reference_range is not None
    assert "13.5" in finding.reference_range and "17.5" in finding.reference_range
    assert finding.reported_flag == "NORMAL"
    assert finding.source_text == line


def test_parse_finding_high_flag():
    """Test line with HIGH / H flag."""
    line = "Fasting Glucose    112    mg/dL    70 - 99    HIGH"
    finding = parse_finding_from_line(line, page_number=1)
    assert finding is not None
    assert finding.test_name == "Fasting Glucose"
    assert finding.value == "112"
    assert finding.unit == "mg/dL"
    assert finding.reported_flag == "HIGH"


def test_parse_finding_less_than_reference_range():
    """Test reference range with '< 200' notation."""
    line = "Total Cholesterol 235 mg/dL < 200 HIGH"
    finding = parse_finding_from_line(line, page_number=1)
    assert finding is not None
    assert finding.test_name == "Total Cholesterol"
    assert finding.value == "235"
    assert finding.unit == "mg/dL"
    assert finding.reference_range is not None
    assert "<" in finding.reference_range
    assert finding.reported_flag == "HIGH"


def test_parse_finding_pipe_delimited():
    """Test pipe-separated report formatting."""
    line = "TSH | 3.45 | uIU/mL | 0.40 - 4.50 | NORMAL"
    finding = parse_finding_from_line(line, page_number=1)
    assert finding is not None
    assert finding.test_name == "TSH"
    assert finding.value == "3.45"
    assert finding.unit == "uIU/mL"
    assert finding.reported_flag == "NORMAL"


def test_parse_finding_without_unit_or_range():
    """Test that missing units and ranges are preserved as None without hallucinating values."""
    line = "Blood Pressure 120/80"
    finding = parse_finding_from_line(line, page_number=1)
    if finding:
        assert finding.unit is None
        assert finding.reference_range is None
        assert finding.reported_flag is None


def test_ignore_header_and_metadata_lines():
    """Verify headers, patient metadata, and page numbers are not parsed as findings."""
    assert parse_finding_from_line("Page 1 of 2") is None
    assert parse_finding_from_line("Patient Name: John Doe") is None
    assert parse_finding_from_line("Ordering Physician: Dr. Smith") is None
    assert parse_finding_from_line("Laboratory Report") is None


def test_extract_report_date():
    """Verify detection of various clinical date formats."""
    text1 = "Collection Date: 2024-10-15\nTest Name Result"
    assert extract_report_date(text1) == "2024-10-15"

    text2 = "Report Date: October 14, 2024\nHemoglobin 14.0"
    assert extract_report_date(text2) == "October 14, 2024"

    text3 = "Date of Collection: 15/10/2024"
    assert extract_report_date(text3) == "15/10/2024"


def test_extract_findings_from_pages(multipage_pdf_bytes: bytes):
    """Test multi-page findings extraction and page attribution."""
    pages = [
        {"page_number": 1, "text": "Hemoglobin 14.2 g/dL 13.5 - 17.5 NORMAL\nWhite Blood Cells 7.5 10^3/uL 4.5-11.0 NORMAL"},
        {"page_number": 2, "text": "Fasting Glucose 112 mg/dL 70-99 HIGH\nCreatinine 1.1 mg/dL 0.7-1.3 NORMAL"},
    ]
    findings = extract_findings_from_pages(pages)
    assert len(findings) == 4
    p1_findings = [f for f in findings if f.page_number == 1]
    p2_findings = [f for f in findings if f.page_number == 2]
    assert len(p1_findings) == 2
    assert len(p2_findings) == 2
    assert any(f.test_name == "Hemoglobin" for f in p1_findings)
    assert any(f.test_name == "Fasting Glucose" for f in p2_findings)
