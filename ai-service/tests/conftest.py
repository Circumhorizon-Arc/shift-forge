"""Test fixtures and synthetic document generators for HealthSense AI service."""

import io
import pytest
import pymupdf
from PIL import Image, ImageDraw, ImageFont


SAMPLE_LAB_REPORT_TEXT = """
HEALTHSENSE DIAGNOSTIC LABORATORY
Patient: Jane Doe (ID: 98765)
Collection Date: 2024-10-15
Ordering Physician: Dr. Sarah Smith, MD
--------------------------------------------------------------------
Test Name               Result      Units       Reference Range   Flag
--------------------------------------------------------------------
Hemoglobin              14.2        g/dL        13.5 - 17.5       NORMAL
Fasting Glucose         112         mg/dL       70 - 99           HIGH
Total Cholesterol       235         mg/dL       < 200             HIGH
HDL Cholesterol         48          mg/dL       > 40              NORMAL
LDL Cholesterol         152         mg/dL       < 100             HIGH
Triglycerides           168         mg/dL       < 150             HIGH
White Blood Cells       7.5         10^3/uL     4.5 - 11.0        NORMAL
Platelet Count          260         10^3/uL     150 - 450         NORMAL
Creatinine              1.1         mg/dL       0.7 - 1.3         NORMAL
Blood Urea Nitrogen     16          mg/dL       7 - 20            NORMAL
TSH                     3.45        uIU/mL      0.40 - 4.50       NORMAL
--------------------------------------------------------------------
Comments: Elevated fasting blood glucose and lipid panel parameters noted.
Please consult ordering physician.
"""


def create_synthetic_digital_pdf(pages_text: list[str]) -> bytes:
    """Generates an in-memory digital PDF with selectable vector text across multiple pages."""
    doc = pymupdf.open()
    for text in pages_text:
        page = doc.new_page(width=612, height=792)  # Standard 8.5x11 inches
        # Insert text onto page
        page.insert_text(pymupdf.Point(50, 60), text, fontsize=11)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_synthetic_image(text: str, img_format: str = "PNG") -> bytes:
    """Draws text onto a PIL image and returns raw bytes in PNG or JPEG format."""
    # Use standard document resolution (800x600 for synthetic test)
    img = Image.new("RGB", (900, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Default font
    draw.text((30, 30), text, fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format=img_format)
    return buf.getvalue()


def create_synthetic_scanned_pdf(text: str) -> bytes:
    """Creates a PDF containing an embedded rasterized image (simulating a scanned paper document)."""
    # 1. Generate image with text
    img = Image.new("RGB", (1200, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((40, 40), text, fill=(0, 0, 0))

    img_buf = io.BytesIO()
    img.save(img_buf, format="PNG")
    img_bytes = img_buf.getvalue()

    # 2. Embed image into PDF page
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    rect = pymupdf.Rect(20, 20, 592, 772)
    page.insert_image(rect, stream=img_bytes)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def sample_report_text() -> str:
    return SAMPLE_LAB_REPORT_TEXT


@pytest.fixture
def digital_pdf_bytes(sample_report_text: str) -> bytes:
    return create_synthetic_digital_pdf([sample_report_text])


@pytest.fixture
def multipage_pdf_bytes() -> bytes:
    page1 = """
    HEALTHSENSE DIAGNOSTIC LABORATORY - Page 1
    Collection Date: 2024-10-15
    Test Name               Result      Units       Reference Range   Flag
    Hemoglobin              14.2        g/dL        13.5 - 17.5       NORMAL
    White Blood Cells       7.5         10^3/uL     4.5 - 11.0        NORMAL
    Platelet Count          260         10^3/uL     150 - 450         NORMAL
    """
    page2 = """
    HEALTHSENSE DIAGNOSTIC LABORATORY - Page 2
    Test Name               Result      Units       Reference Range   Flag
    Fasting Glucose         112         mg/dL       70 - 99           HIGH
    Creatinine              1.1         mg/dL       0.7 - 1.3         NORMAL
    Total Cholesterol       235         mg/dL       < 200             HIGH
    """
    return create_synthetic_digital_pdf([page1, page2])


@pytest.fixture
def sample_image_bytes() -> bytes:
    ocr_text = "Fasting Glucose 105 mg/dL 70-99 HIGH\nHemoglobin 14.5 g/dL 13.5-17.5 NORMAL"
    return create_synthetic_image(ocr_text, "PNG")
