"""Tests for image OCR extraction and preprocessing."""

import pytest
from app.exceptions import CorruptedFileError, EmptyFileError
from app.extraction.image_ocr import extract_text_from_image, sanitize_extracted_text
from app.extraction.preprocessing import preprocess_image_for_ocr
from tests.conftest import create_synthetic_image


def test_sanitize_extracted_text():
    """Verify null bytes, control chars, and erratic whitespace are cleaned."""
    raw = "Hemoglobin\x00\x07 14.2 g/dL\r\n\n\n\nReference: 13.5-17.5"
    cleaned = sanitize_extracted_text(raw)
    assert "\x00" not in cleaned
    assert "\x07" not in cleaned
    assert "\n\n\n" not in cleaned
    assert "Hemoglobin 14.2 g/dL" in cleaned


def test_preprocess_image_returns_grayscale():
    """Verify image preprocessing converts to grayscale and enhances readability."""
    img_bytes = create_synthetic_image("Test Lab Results", "PNG")
    processed = preprocess_image_for_ocr(img_bytes)
    assert processed.mode == "L"
    assert processed.width >= 800


def test_extract_text_from_valid_png_image():
    """Verify OCR extracts text from a valid PNG image."""
    text_content = "Fasting Glucose 105 mg/dL 70-99 HIGH"
    img_bytes = create_synthetic_image(text_content, "PNG")

    res = extract_text_from_image(img_bytes, filename="lab_scan.png")
    assert res["page_count"] == 1
    assert res["method"] == "ocr_image"
    assert "Glucose" in res["text"] or "105" in res["text"]


def test_extract_text_from_valid_jpeg_image():
    """Verify OCR extracts text from a valid JPEG image."""
    text_content = "Hemoglobin 14.5 g/dL"
    img_bytes = create_synthetic_image(text_content, "JPEG")

    res = extract_text_from_image(img_bytes, filename="lab_scan.jpg")
    assert res["page_count"] == 1
    assert res["method"] == "ocr_image"
    assert "Hemoglobin" in res["text"] or "14.5" in res["text"]


def test_empty_image_bytes_raises_empty_error():
    """Verify zero-byte image raises EmptyFileError."""
    with pytest.raises(EmptyFileError):
        extract_text_from_image(b"", filename="empty.png")


def test_corrupted_image_bytes_raises_corrupted_error():
    """Verify invalid bytes raise CorruptedFileError."""
    with pytest.raises(CorruptedFileError):
        extract_text_from_image(b"not an image", filename="corrupted.png")
