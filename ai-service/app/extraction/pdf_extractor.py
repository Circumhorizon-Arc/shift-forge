"""PDF extraction engine using PyMuPDF (fitz) with automatic OCR fallback for scanned pages."""

import io
from typing import Any, Dict, List
import pymupdf
from PIL import Image

from app.config import settings
from app.exceptions import CorruptedFileError, EmptyFileError, OCRError
from app.extraction.image_ocr import configure_tesseract, sanitize_extracted_text
from app.extraction.preprocessing import preprocess_image_for_ocr
import pytesseract


def extract_text_from_scanned_page(page: pymupdf.Page, page_num: int) -> str:
    """Renders a PDF page to a high-resolution pixmap and extracts text via Tesseract OCR."""
    configure_tesseract()
    try:
        # Render page at 200 DPI for high fidelity character recognition
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        preprocessed = preprocess_image_for_ocr(img)

        text = pytesseract.image_to_string(preprocessed, config=r"--oem 3 --psm 6")
        if len(text.strip()) < settings.MIN_EXTRACTABLE_TEXT_CHARS:
            text = pytesseract.image_to_string(preprocessed, config=r"--oem 3 --psm 3")
        return sanitize_extracted_text(text)
    except pytesseract.TesseractNotFoundError:
        raise OCRError(
            "Tesseract OCR is not installed or not in PATH. Required to extract scanned PDF documents."
        )
    except Exception as exc:
        raise OCRError(f"Failed OCR on PDF page {page_num}: {exc}")


def extract_text_from_pdf(
    pdf_bytes: bytes,
    filename: str = "document.pdf",
) -> Dict[str, Any]:
    """Extracts text from a PDF document, preserving page numbers and falling back to OCR when scanned.

    Args:
        pdf_bytes: Raw bytes of the PDF.
        filename: Name of the PDF file for error logging.

    Returns:
        Dictionary containing combined text, per-page breakdown, total pages, and primary extraction method.

    Raises:
        EmptyFileError: When file is 0 bytes.
        CorruptedFileError: When PDF cannot be opened or is password encrypted.
    """
    if not pdf_bytes or len(pdf_bytes) == 0:
        raise EmptyFileError(filename)

    # Validate PDF magic header
    if not pdf_bytes.startswith(b"%PDF-"):
        raise CorruptedFileError(f"File '{filename}' does not have a valid PDF header.")

    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise CorruptedFileError(f"Failed to open PDF document '{filename}': {exc}")

    if doc.is_encrypted:
        doc.close()
        raise CorruptedFileError(f"PDF document '{filename}' is password-protected or encrypted.")

    page_count = len(doc)
    if page_count == 0:
        doc.close()
        raise CorruptedFileError(f"PDF document '{filename}' has 0 pages.")

    pages_info: List[Dict[str, Any]] = []
    full_text_segments: List[str] = []
    methods_used = set()

    try:
        for page_index in range(page_count):
            page_num = page_index + 1
            page = doc[page_index]

            # Attempt direct digital text extraction first
            page_text = page.get_text("text") or ""
            cleaned_page_text = sanitize_extracted_text(page_text)

            # Determine if this page is scanned (negligible digital text)
            if len(cleaned_page_text) < settings.MIN_EXTRACTABLE_TEXT_CHARS:
                # Page has very little digital text; attempt OCR fallback
                ocr_text = extract_text_from_scanned_page(page, page_num)
                if len(ocr_text) > len(cleaned_page_text):
                    cleaned_page_text = ocr_text
                    method = "ocr_scanned_pdf"
                else:
                    method = "pdf_text"
            else:
                method = "pdf_text"

            methods_used.add(method)
            pages_info.append({
                "page_number": page_num,
                "text": cleaned_page_text,
                "method": method,
            })
            if cleaned_page_text:
                full_text_segments.append(f"--- Page {page_num} ---\n{cleaned_page_text}")

    finally:
        doc.close()

    if "pdf_text" in methods_used and "ocr_scanned_pdf" in methods_used:
        overall_method = "hybrid"
    elif "ocr_scanned_pdf" in methods_used:
        overall_method = "ocr_scanned_pdf"
    else:
        overall_method = "pdf_text"

    combined_text = "\n\n".join(full_text_segments).strip()

    return {
        "text": combined_text,
        "page_count": page_count,
        "pages": pages_info,
        "method": overall_method,
    }
