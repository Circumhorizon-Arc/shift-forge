"""Tests for PDF text extraction engine."""

import pytest
import pymupdf
from app.exceptions import CorruptedFileError, EmptyFileError
from app.extraction.pdf_extractor import extract_text_from_pdf
from tests.conftest import create_synthetic_scanned_pdf


def test_digital_pdf_extraction_single_page(digital_pdf_bytes: bytes):
    """Test extracting text from a single-page digital PDF."""
    res = extract_text_from_pdf(digital_pdf_bytes, filename="lab_report.pdf")
    assert res["page_count"] == 1
    assert res["method"] == "pdf_text"
    assert "Hemoglobin" in res["text"]
    assert "Fasting Glucose" in res["text"]
    assert len(res["pages"]) == 1
    assert res["pages"][0]["page_number"] == 1


def test_digital_pdf_extraction_multipage(multipage_pdf_bytes: bytes):
    """Test extracting text across multiple pages with page number tracking."""
    res = extract_text_from_pdf(multipage_pdf_bytes, filename="multipage.pdf")
    assert res["page_count"] == 2
    assert res["method"] == "pdf_text"
    assert len(res["pages"]) == 2
    assert res["pages"][0]["page_number"] == 1
    assert "Hemoglobin" in res["pages"][0]["text"]
    assert res["pages"][1]["page_number"] == 2
    assert "Fasting Glucose" in res["pages"][1]["text"]


def test_empty_pdf_bytes_raises_empty_error():
    """Test that zero-byte PDF input raises EmptyFileError."""
    with pytest.raises(EmptyFileError):
        extract_text_from_pdf(b"", filename="empty.pdf")


def test_corrupted_pdf_raises_corrupted_error():
    """Test that random bytes pretending to be a PDF raise CorruptedFileError."""
    with pytest.raises(CorruptedFileError):
        extract_text_from_pdf(b"This is not a PDF file", filename="invalid.pdf")


def test_partially_corrupted_pdf_header():
    """Test PDF missing valid %PDF- header."""
    with pytest.raises(CorruptedFileError):
        extract_text_from_pdf(b"%NOT_A_PDF header content here", filename="bad_header.pdf")


def test_scanned_pdf_ocr_fallback():
    """Test that a scanned PDF (image only) falls back to OCR."""
    scanned_text = "Fasting Glucose 105 mg/dL 70-99 HIGH"
    pdf_bytes = create_synthetic_scanned_pdf(scanned_text)
    res = extract_text_from_pdf(pdf_bytes, filename="scanned.pdf")
    assert res["page_count"] == 1
    assert res["method"] in ("ocr_scanned_pdf", "hybrid")
    # Should find glucose from OCR
    assert "Glucose" in res["text"] or "105" in res["text"]
