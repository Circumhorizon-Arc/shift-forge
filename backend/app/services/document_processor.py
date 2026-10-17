from pathlib import Path
from typing import Optional
from PIL import Image

try:
    # pyrefly: ignore[missing-import]
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    fitz = None
    HAS_PYMUPDF = False

try:
    # pyrefly: ignore[missing-import]
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    PdfReader = None
    HAS_PYPDF = False


class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extracts text content from a PDF document using PyMuPDF (fast & high fidelity) or pypdf."""
        # 1. Try PyMuPDF first
        if HAS_PYMUPDF and fitz is not None:
            try:
                doc = fitz.open(file_path)
                pages_text = []
                for page_idx in range(len(doc)):
                    page = doc[page_idx]
                    text = page.get_text()
                    if text.strip():
                        pages_text.append(f"--- Page {page_idx + 1} ---\n{text.strip()}")
                doc.close()
                if pages_text:
                    return "\n\n".join(pages_text)
            except Exception:
                pass

        # 2. Fallback to pypdf
        if HAS_PYPDF and PdfReader is not None:
            try:
                reader = PdfReader(file_path)
                extracted_text = []
                for page_idx, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        extracted_text.append(f"--- Page {page_idx + 1} ---\n{text}")
                return "\n\n".join(extracted_text).strip()
            except Exception as e:
                return f"[PDF text extraction failed: {str(e)}]"

        return "[No PDF extraction library available]"

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
            return f"[Medical Image / Scan: {ext.upper()} file ready for clinical inspection]"
        return None


document_processor = DocumentProcessor()
