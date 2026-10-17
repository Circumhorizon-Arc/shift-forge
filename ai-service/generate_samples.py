"""Script to generate realistic synthetic medical reports for testing and demonstrations."""

import os
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw

SAMPLES_DIR = Path(__file__).parent / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_REPORT_PAGE1 = """
HEALTHSENSE DIAGNOSTIC PATHOLOGY LABORATORY
Accredited Medical Diagnostics Facility - ISO 15189
-------------------------------------------------------------------------------------
Patient Name: Jane Doe                       Patient ID: HS-98421
Date of Birth: 1986-04-12                    Age / Sex: 38 Y / Female
Ordering Physician: Dr. Marcus Vance, MD     Collection Date: 2024-10-15
Report Date: 2024-10-16                      Specimen: Whole Blood / Serum
-------------------------------------------------------------------------------------
TEST NAME                     RESULT         UNIT            REFERENCE INTERVAL    FLAG
-------------------------------------------------------------------------------------
COMPLETE BLOOD COUNT (CBC):
Hemoglobin                    14.2           g/dL            12.0 - 16.0           NORMAL
Hematocrit                    42.5           %               36.0 - 46.0           NORMAL
White Blood Cells (WBC)       11.8           10^3/uL         4.5 - 11.0            HIGH
Red Blood Cells (RBC)         4.65           10^6/uL         4.00 - 5.20           NORMAL
Platelet Count                275            10^3/uL         150 - 450             NORMAL
Mean Corpuscular Volume (MCV) 91.4           fL              80.0 - 100.0          NORMAL

COMPREHENSIVE METABOLIC PANEL:
Fasting Glucose               114            mg/dL           70 - 99               HIGH
Hemoglobin A1c (HbA1c)        5.9            %               4.0 - 5.6             HIGH
Blood Urea Nitrogen (BUN)     16             mg/dL           7 - 20                NORMAL
Creatinine                    0.95           mg/dL           0.60 - 1.20           NORMAL
eGFR                          94             mL/min/1.73m2   >= 60                 NORMAL
Sodium                        140            mmol/L          136 - 145             NORMAL
Potassium                     4.4            mmol/L          3.5 - 5.1             NORMAL
Calcium                       9.3            mg/dL           8.5 - 10.2            NORMAL
Total Protein                 7.1            g/dL            6.4 - 8.3             NORMAL
ALT (SGPT)                    28             U/L             7 - 56                NORMAL
AST (SGOT)                    24             U/L             10 - 40               NORMAL
-------------------------------------------------------------------------------------
"""

SAMPLE_REPORT_PAGE2 = """
HEALTHSENSE DIAGNOSTIC PATHOLOGY LABORATORY - PAGE 2
Patient Name: Jane Doe                       Patient ID: HS-98421
-------------------------------------------------------------------------------------
TEST NAME                     RESULT         UNIT            REFERENCE INTERVAL    FLAG
-------------------------------------------------------------------------------------
LIPID PANEL:
Total Cholesterol             238            mg/dL           < 200                 HIGH
Triglycerides                 175            mg/dL           < 150                 HIGH
HDL Cholesterol               46             mg/dL           > 40                  NORMAL
LDL Cholesterol (calculated)  157            mg/dL           < 100                 HIGH

THYROID FUNCTION:
TSH (Thyroid Stimulating)     2.85           uIU/mL          0.40 - 4.50           NORMAL
-------------------------------------------------------------------------------------
CLINICAL NOTES & INTERPRETATION:
- Fasting blood glucose and HbA1c indicate mildly elevated glycemic markers.
- Lipid panel indicates mild hyperlipidemia (elevated total cholesterol, triglycerides, LDL).
- Elevated WBC count may reflect mild physiological response or recent infection.
Please review these findings in clinical consultation with Dr. Marcus Vance.
-------------------------------------------------------------------------------------
"""


def generate_synthetic_fixtures():
    # 1. Multi-page digital PDF
    pdf_doc = pymupdf.open()
    for text in [SAMPLE_REPORT_PAGE1, SAMPLE_REPORT_PAGE2]:
        p = pdf_doc.new_page(width=612, height=792)
        p.insert_text(pymupdf.Point(40, 50), text, fontsize=9.5)
    pdf_path = SAMPLES_DIR / "sample_digital_report.pdf"
    pdf_doc.save(str(pdf_path))
    pdf_doc.close()
    print(f"Generated {pdf_path}")

    # 2. Image scan (PNG)
    img_text = """HEALTHSENSE DIAGNOSTIC PATHOLOGY LABORATORY
TEST NAME           RESULT   UNIT     REFERENCE INTERVAL  FLAG
Hemoglobin          14.2     g/dL     12.0 - 16.0         NORMAL
Fasting Glucose     114      mg/dL    70 - 99             HIGH
HbA1c               5.9      %        4.0 - 5.6           HIGH
Total Cholesterol   238      mg/dL    < 200               HIGH
Triglycerides       175      mg/dL    < 150               HIGH
White Blood Cells   11.8     10^3/uL  4.5 - 11.0          HIGH
TSH                 2.85     uIU/mL   0.40 - 4.50         NORMAL
"""
    img = Image.new("RGB", (1200, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), img_text, fill=(0, 0, 0))
    png_path = SAMPLES_DIR / "sample_scan_report.png"
    img.save(png_path)
    print(f"Generated {png_path}")

    # 3. Scanned PDF (Raster image inside PDF)
    scanned_pdf = pymupdf.open()
    p_scanned = scanned_pdf.new_page(width=612, height=792)
    rect = pymupdf.Rect(20, 20, 592, 772)
    p_scanned.insert_image(rect, filename=str(png_path))
    scanned_pdf_path = SAMPLES_DIR / "sample_scanned_report.pdf"
    scanned_pdf.save(str(scanned_pdf_path))
    scanned_pdf.close()
    print(f"Generated {scanned_pdf_path}")


if __name__ == "__main__":
    generate_synthetic_fixtures()
