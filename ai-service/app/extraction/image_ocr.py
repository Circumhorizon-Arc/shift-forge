"""OCR extraction engine using Tesseract for medical document images."""

import io
import re
from typing import Dict, Any, Optional
from PIL import Image, UnidentifiedImageError
import pytesseract

from app.config import settings
from app.exceptions import CorruptedFileError, EmptyFileError, OCRError
from app.extraction.preprocessing import preprocess_image_for_ocr


def sanitize_extracted_text(text: str) -> str:
    """Sanitize raw OCR or PDF text to prevent control character injection and normalize spacing.

    Args:
        text: Raw extracted string.

    Returns:
        Cleaned text with normalized whitespace and stripped dangerous control chars.
    """
    if not text:
        return ""
    # Strip null bytes and non-printable control characters (except newline, carriage return, tab)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    # Replace multiple consecutive blank lines with two newlines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def configure_tesseract() -> None:
    """Configures pytesseract with the resolved tesseract executable path."""
    tess_path = settings.resolve_tesseract_path()
    if tess_path:
        pytesseract.pytesseract.tesseract_cmd = tess_path


def extract_text_from_image(
    image_bytes: bytes,
    filename: str = "image",
) -> Dict[str, Any]:
    """Extracts text from an image (PNG, JPEG, etc.) using Tesseract OCR with preprocessing.

    Args:
        image_bytes: Raw bytes of the image file.
        filename: Original file name for logging and context.

    Returns:
        Dictionary containing extracted text, page count, and metadata.

    Raises:
        EmptyFileError: If file is empty.
        CorruptedFileError: If image bytes cannot be opened or decoded.
        OCRError: If Tesseract fails or is not installed.
    """
    if not image_bytes or len(image_bytes) == 0:
        raise EmptyFileError(filename)

    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
        pil_image.verify()  # Fast check for file format integrity
        # Re-open because verify() closes the file in PIL
        pil_image = Image.open(io.BytesIO(image_bytes))
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise CorruptedFileError(f"File '{filename}' is not a valid or readable image: {exc}")

    configure_tesseract()

    try:
        preprocessed = preprocess_image_for_ocr(pil_image)
    except Exception as exc:
        raise CorruptedFileError(f"Failed to preprocess image '{filename}': {exc}")

    try:
        # PSM 6 is optimal for uniform text/tabular laboratory reports
        custom_config = r"--oem 3 --psm 6"
        extracted = pytesseract.image_to_string(preprocessed, config=custom_config)

        # If PSM 6 yielded very little text, fallback to PSM 3 (auto segmentation)
        if len(extracted.strip()) < settings.MIN_EXTRACTABLE_TEXT_CHARS:
            extracted = pytesseract.image_to_string(preprocessed, config=r"--oem 3 --psm 3")

    except pytesseract.TesseractNotFoundError:
        raise OCRError(
            "Tesseract OCR is not installed or not found in system PATH. "
            "Please install tesseract (e.g. 'brew install tesseract' or 'apt-get install tesseract-ocr') "
            "or configure TESSERACT_CMD."
        )
    except pytesseract.TesseractError as exc:
        raise OCRError(f"Tesseract OCR error while processing '{filename}': {exc}")
    except Exception as exc:
        raise OCRError(f"Unexpected error during OCR processing for '{filename}': {exc}")

    cleaned = sanitize_extracted_text(extracted)

    return {
        "text": cleaned,
        "page_count": 1,
        "pages": [{"page_number": 1, "text": cleaned, "method": "ocr_image"}],
        "method": "ocr_image",
    }
