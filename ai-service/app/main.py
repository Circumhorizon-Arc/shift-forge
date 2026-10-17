"""FastAPI application providing standalone HTTP endpoints for HealthSense medical report processing."""

import logging
from typing import Any, Dict
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import (
    CorruptedFileError,
    EmptyFileError,
    FileSizeExceededError,
    InsufficientTextQualityError,
    InvalidFileTypeError,
    LLMServiceError,
    MedicalReportError,
    OCRError,
)
from app.processing.report_pipeline import process_medical_report_async
from app.schemas import ErrorResponse, ReportAnalysis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("healthsense.ai")

app = FastAPI(
    title="HealthSense AI Medical Report Processing API",
    description=(
        "AI/ML service for extracting, structuring, and explaining medical laboratory "
        "reports and clinical documents in patient-friendly plain language."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(InvalidFileTypeError)
async def handle_invalid_file_type(_request, exc: InvalidFileTypeError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error_code=exc.code,
            message=exc.message,
            details={"allowed": exc.allowed, "filename": exc.filename},
        ).model_dump(),
    )


@app.exception_handler(EmptyFileError)
async def handle_empty_file(_request, exc: EmptyFileError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(error_code=exc.code, message=exc.message).model_dump(),
    )


@app.exception_handler(CorruptedFileError)
async def handle_corrupted_file(_request, exc: CorruptedFileError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(error_code=exc.code, message=exc.message).model_dump(),
    )


@app.exception_handler(InsufficientTextQualityError)
async def handle_insufficient_quality(_request, exc: InsufficientTextQualityError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(error_code=exc.code, message=exc.message).model_dump(),
    )


@app.exception_handler(FileSizeExceededError)
async def handle_file_size_exceeded(_request, exc: FileSizeExceededError):
    return JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content=ErrorResponse(
            error_code=exc.code,
            message=exc.message,
            details={"size_bytes": exc.size_bytes, "max_bytes": exc.max_bytes},
        ).model_dump(),
    )


@app.exception_handler(OCRError)
async def handle_ocr_error(_request, exc: OCRError):
    logger.error("OCR Error encountered: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error_code=exc.code, message=exc.message).model_dump(),
    )


@app.exception_handler(MedicalReportError)
async def handle_general_medical_error(_request, exc: MedicalReportError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(error_code=exc.code, message=exc.message).model_dump(),
    )


@app.get(
    "/health",
    tags=["System"],
    summary="Health check & environment diagnostics",
)
async def health_check() -> Dict[str, Any]:
    """Returns service health, OCR engine availability, and configured LLM provider."""
    tess_path = settings.resolve_tesseract_path()
    return {
        "status": "healthy",
        "service": "healthsense-ai-service",
        "llm_provider": settings.LLM_PROVIDER,
        "ocr_available": tess_path is not None,
        "tesseract_path": tess_path,
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
    }


@app.post(
    "/api/v1/report-analysis",
    response_model=ReportAnalysis,
    status_code=status.HTTP_200_OK,
    tags=["Medical Reports"],
    summary="Process medical report PDF or image",
    responses={
        200: {"description": "Structured findings and plain-language explanation"},
        400: {"model": ErrorResponse, "description": "Invalid file format or corrupted file"},
        413: {"model": ErrorResponse, "description": "Uploaded file exceeds maximum size limit"},
        422: {"model": ErrorResponse, "description": "Text quality is unreadable or insufficient"},
        500: {"model": ErrorResponse, "description": "Processing or OCR internal failure"},
    },
)
async def analyze_medical_report(
    file: UploadFile = File(..., description="Medical report file (PDF, PNG, JPEG)"),
) -> ReportAnalysis:
    """Accepts a medical report PDF or image, extracts laboratory/clinical findings,
    and returns a structured, patient-friendly explanation with doctor consultation questions.
    """
    logger.info("Received document upload: filename=%s, content_type=%s", file.filename, file.content_type)
    file_bytes = await file.read()

    return await process_medical_report_async(
        file_bytes=file_bytes,
        filename=file.filename or "unknown_report",
        content_type=file.content_type,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
