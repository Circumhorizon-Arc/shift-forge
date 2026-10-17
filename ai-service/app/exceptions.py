"""Custom exceptions for HealthSense medical report processing."""

from typing import List, Optional


class MedicalReportError(Exception):
    """Base exception for all medical report processing errors."""

    def __init__(self, message: str, code: str = "PROCESSING_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class InvalidFileTypeError(MedicalReportError):
    """Raised when an unsupported file extension or MIME type is uploaded."""

    def __init__(self, filename: str, allowed: List[str]):
        msg = f"Invalid file type for '{filename}'. Allowed formats: {', '.join(allowed)}"
        super().__init__(msg, code="INVALID_FILE_TYPE")
        self.filename = filename
        self.allowed = allowed


class FileSizeExceededError(MedicalReportError):
    """Raised when uploaded file exceeds the configured size limit."""

    def __init__(self, size_bytes: int, max_bytes: int):
        size_mb = size_bytes / (1024 * 1024)
        max_mb = max_bytes / (1024 * 1024)
        msg = f"File size ({size_mb:.2f} MB) exceeds maximum allowed size ({max_mb:.1f} MB)"
        super().__init__(msg, code="FILE_SIZE_EXCEEDED")
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes


class EmptyFileError(MedicalReportError):
    """Raised when the uploaded file is zero bytes."""

    def __init__(self, filename: str = "Uploaded file"):
        super().__init__(f"{filename} is empty (0 bytes).", code="EMPTY_FILE")


class CorruptedFileError(MedicalReportError):
    """Raised when a PDF or image cannot be read/parsed due to corruption."""

    def __init__(self, reason: str = "File is corrupted or damaged and cannot be opened"):
        super().__init__(reason, code="CORRUPTED_FILE")


class TextExtractionError(MedicalReportError):
    """Raised when no text can be extracted from the document."""

    def __init__(self, message: str = "Failed to extract text from document"):
        super().__init__(message, code="TEXT_EXTRACTION_FAILED")


class InsufficientTextQualityError(MedicalReportError):
    """Raised when extracted text is unreadable, too brief, or low confidence."""

    def __init__(
        self,
        message: str = "Extracted text quality is insufficient for clinical interpretation. Please provide a clearer, higher-resolution document or digital PDF.",
    ):
        super().__init__(message, code="INSUFFICIENT_TEXT_QUALITY")


class OCRError(MedicalReportError):
    """Raised when optical character recognition fails or tesseract is unavailable."""

    def __init__(self, message: str = "OCR processing failed"):
        super().__init__(message, code="OCR_FAILED")


class LLMServiceError(MedicalReportError):
    """Raised when LLM API call fails or encounters an error."""

    def __init__(self, message: str = "LLM explanation service encountered an error", provider: Optional[str] = None):
        super().__init__(message, code="LLM_SERVICE_ERROR")
        self.provider = provider


class LLMTimeoutError(LLMServiceError):
    """Raised when LLM request times out."""

    def __init__(self, timeout_seconds: float):
        super().__init__(f"LLM request timed out after {timeout_seconds}s", provider="timeout")
        self.code = "LLM_TIMEOUT"


class LLMValidationError(MedicalReportError):
    """Raised when LLM output does not conform to expected schema."""

    def __init__(self, details: str):
        super().__init__(f"LLM response failed schema validation: {details}", code="LLM_VALIDATION_ERROR")
