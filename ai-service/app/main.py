"""FastAPI application for HealthSense medical report processing."""

import logging
import secrets
from typing import Any

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    Security,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.exceptions import (
    CorruptedFileError,
    EmptyFileError,
    FileSizeExceededError,
    InsufficientTextQualityError,
    InvalidFileTypeError,
    MedicalReportError,
    OCRError,
)
from app.processing.report_pipeline import process_medical_report_async
from app.schemas import ErrorResponse, ReportAnalysis
from app.tracker import UploadRecord, get_all_uploads, get_upload_count

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("healthsense.ai")

app = FastAPI(
    title="HealthSense AI Medical Report Processing API",
    description=(
        "AI/ML service for extracting, structuring, and explaining medical "
        "laboratory reports and clinical documents in patient-friendly language."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(InvalidFileTypeError)
async def handle_invalid_file_type(_request, exc: InvalidFileTypeError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error_code=exc.code,
            message=exc.message,
            details={"allowed": exc.allowed},
        ).model_dump(),
    )


@app.exception_handler(EmptyFileError)
async def handle_empty_file(_request, exc: EmptyFileError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error_code=exc.code,
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(CorruptedFileError)
async def handle_corrupted_file(_request, exc: CorruptedFileError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error_code=exc.code,
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(InsufficientTextQualityError)
async def handle_insufficient_quality(
    _request, exc: InsufficientTextQualityError
):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error_code=exc.code,
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(FileSizeExceededError)
async def handle_file_size_exceeded(
    _request, exc: FileSizeExceededError
):
    return JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content=ErrorResponse(
            error_code=exc.code,
            message=exc.message,
            details={
                "size_bytes": exc.size_bytes,
                "max_bytes": exc.max_bytes,
            },
        ).model_dump(),
    )


@app.exception_handler(OCRError)
async def handle_ocr_error(_request, exc: OCRError):
    # Do not log raw exception messages, which may contain sensitive paths
    # or document-related information.
    logger.error("OCR processing failed.")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error_code=exc.code,
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(MedicalReportError)
async def handle_general_medical_error(
    _request, exc: MedicalReportError
):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error_code=exc.code,
            message=exc.message,
        ).model_dump(),
    )


# ---------------------------------------------------------------------------
# Service-to-service authentication
# ---------------------------------------------------------------------------

_bearer = HTTPBearer(auto_error=False)


def _require_service_token(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> None:
    """Protect internal upload-history access with a bearer token."""
    configured_token = settings.INTERNAL_SERVICE_TOKEN

    if not configured_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Upload history endpoint is disabled.",
        )

    supplied = credentials.credentials if credentials else None

    if not supplied or not secrets.compare_digest(
        supplied, configured_token
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing service token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get(
    "/health",
    tags=["System"],
    summary="Health check and service diagnostics",
)
async def health_check() -> dict[str, Any]:
    """Return service health without exposing internal filesystem paths."""
    tess_path = settings.resolve_tesseract_path()

    return {
        "status": "healthy",
        "service": "healthsense-ai-service",
        "llm_provider": settings.LLM_PROVIDER,
        "ocr_available": tess_path is not None,
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
    }


@app.post(
    "/api/v1/report-analysis",
    response_model=ReportAnalysis,
    status_code=status.HTTP_200_OK,
    tags=["Medical Reports"],
    summary="Process a medical report PDF or image",
    responses={
        200: {
            "description": "Structured findings and plain-language explanation"
        },
        400: {
            "model": ErrorResponse,
            "description": "Invalid file format or corrupted file",
        },
        413: {
            "model": ErrorResponse,
            "description": "Uploaded file exceeds the maximum size limit",
        },
        422: {
            "model": ErrorResponse,
            "description": "Text quality is unreadable or insufficient",
        },
        500: {
            "model": ErrorResponse,
            "description": "Processing or OCR internal failure",
        },
    },
)
async def analyze_medical_report(
    file: UploadFile = File(
        ...,
        description="Medical report file (PDF, PNG, JPEG)",
    ),
) -> ReportAnalysis:
    """Extract and explain a medical report in patient-friendly language."""
    max_bytes = settings.max_file_size_bytes

    # Reject uploads already known to exceed the limit.
    if file.size is not None and file.size > max_bytes:
        raise FileSizeExceededError(
            size_bytes=file.size,
            max_bytes=max_bytes,
        )

    logger.info(
        "Report upload received: content_type=%s",
        file.content_type,
    )

    # Read no more than the configured limit plus one byte.
    file_bytes = await file.read(max_bytes + 1)

    if len(file_bytes) > max_bytes:
        raise FileSizeExceededError(
            size_bytes=len(file_bytes),
            max_bytes=max_bytes,
        )

    if not file_bytes:
        raise EmptyFileError()

    return await process_medical_report_async(
        file_bytes=file_bytes,
        filename=file.filename or "unknown_report",
        content_type=file.content_type,
    )


@app.get(
    "/api/v1/uploads",
    response_model=dict[str, Any],
    tags=["Internal"],
    summary="List tracked upload operational metadata",
    responses={
        200: {"description": "Paginated upload metadata records"},
        401: {"description": "Missing or invalid service token"},
        503: {
            "description": "Endpoint disabled because the service token is unset"
        },
    },
)
async def list_uploads(
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
        description="Maximum records to return",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip",
    ),
    _: None = Depends(_require_service_token),
) -> dict[str, Any]:
    """Return paginated operational metadata for authorized internal services."""
    uploads: list[UploadRecord] = get_all_uploads(
        limit=limit,
        offset=offset,
    )
    total = get_upload_count()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "uploads": [upload.model_dump() for upload in uploads],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )