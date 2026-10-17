"""Application configuration and environment settings."""

import shutil
from pathlib import Path
from typing import List, Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for HealthSense AI report processing module."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Document upload & validation constraints
    MAX_FILE_SIZE_MB: int = Field(default=25, description="Maximum allowed file size in megabytes")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".png", ".jpg", ".jpeg"],
        description="Allowed file extensions for medical documents",
    )
    MIN_EXTRACTABLE_TEXT_CHARS: int = Field(
        default=20,
        description="Minimum characters of text required to consider extraction successful",
    )

    # OCR Configuration
    TESSERACT_CMD: Optional[str] = Field(
        default=None,
        description="Explicit path to tesseract binary if not in PATH",
    )

    # LLM Provider Configuration
    LLM_PROVIDER: Literal["mock", "openai", "gemini"] = Field(
        default="mock",
        description="Provider to use for LLM explanations: 'mock', 'openai', or 'gemini'",
    )
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="API key for OpenAI-compatible endpoint")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", description="Base URL for OpenAI-compatible API")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="Model identifier for OpenAI")

    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API key")
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash", description="Google Gemini model identifier")

    LLM_TIMEOUT_SECONDS: float = Field(default=30.0, description="Timeout for LLM API requests in seconds")
    LLM_TEMPERATURE: float = Field(default=0.1, description="Sampling temperature for LLM generation")

    # Standalone FastAPI Server Settings
    HOST: str = Field(default="0.0.0.0", description="Server bind host")
    PORT: int = Field(default=8001, description="Server port")
    DEBUG: bool = Field(default=False, description="Debug mode")

    @property
    def max_file_size_bytes(self) -> int:
        """Returns max file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    def resolve_tesseract_path(self) -> Optional[str]:
        """Resolves the executable path for Tesseract OCR."""
        if self.TESSERACT_CMD and Path(self.TESSERACT_CMD).is_file():
            return self.TESSERACT_CMD

        # Search standard paths on macOS / Linux
        candidate_paths = [
            "/opt/homebrew/bin/tesseract",
            "/usr/local/bin/tesseract",
            "/usr/bin/tesseract",
        ]
        for path_str in candidate_paths:
            if Path(path_str).is_file():
                return path_str

        # Fall back to shutil.which in PATH
        found = shutil.which("tesseract")
        return found if found else None


settings = Settings()
