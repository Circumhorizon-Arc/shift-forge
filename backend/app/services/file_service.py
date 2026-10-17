import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.config import settings

# Common file signatures (magic numbers)
MAGIC_SIGNATURES = {
    "pdf": b"%PDF",
    "png": b"\x89PNG\r\n\x1a\n",
    "jpg": b"\xff\xd8\xff",
    "jpeg": b"\xff\xd8\xff",
}


class FileService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    def validate_file(self, file: UploadFile) -> str:
        """Validates file extension, size and magic bytes. Returns detected extension."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is missing",
            )

        # 1. Extension check
        ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed formats: {settings.ALLOWED_EXTENSIONS}",
            )

        # 2. Read first chunk for magic bytes validation
        header = file.file.read(8)
        file.file.seek(0)  # Reset pointer

        expected_magic = MAGIC_SIGNATURES.get(ext)
        if expected_magic:
            if not header.startswith(expected_magic[: len(expected_magic)]):
                # Allow minor header variation for some JPEGs
                if ext in ["jpg", "jpeg"] and header.startswith(b"\xff\xd8"):
                    pass
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="File content does not match its extension signature",
                    )

        # 3. Size check
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)  # Reset pointer

        if size > self.max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB",
            )
        if size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        return ext

    def save_file(self, file: UploadFile) -> tuple[str, str, int]:
        """Saves file to upload directory. Returns (saved_filename, absolute_path, file_size)."""
        ext = self.validate_file(file)
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        target_path = self.upload_dir / unique_name

        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = target_path.stat().st_size
        return unique_name, str(target_path.resolve()), file_size


file_service = FileService()
