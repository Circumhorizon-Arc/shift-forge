from pathlib import Path
from typing import Optional
from pypdf import PdfReader
from PIL import Image


class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extracts text content from a PDF document."""
        extracted_text = []
        try:
            reader = PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    extracted_text.append(f"--- Page {page_idx + 1} ---\n{text}")
            return "\n\n".join(extracted_text).strip()
        except Exception as e:
            return f"[PDF text extraction failed: {str(e)}]"

    @staticmethod
    def inspect_image(file_path: str) -> dict:
        """Inspects image dimensions and format."""
        try:
            with Image.open(file_path) as img:
                return {
                    "format": img.format,
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                }
        except Exception as e:
            return {"error": str(e)}

    @classmethod
    def process_document(cls, file_path: str, mime_type: str) -> Optional[str]:
        """Processes document and extracts readable text where possible."""
        p = Path(file_path)
        ext = p.suffix.lower().replace(".", "")

        if ext == "pdf":
            return cls.extract_text_from_pdf(file_path)
        elif ext in ["png", "jpg", "jpeg"]:
            # For images, image OCR or Gemini Vision will process raw image bytes
            return f"[Image document: {ext.upper()} file ready for AI Vision inspection]"
        return None


document_processor = DocumentProcessor()
