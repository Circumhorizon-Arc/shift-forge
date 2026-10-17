
"""Upload tracker for lightweight operational metadata.

This JSON file stores operational metadata only; it is not the source of
truth for reports. Permanent report storage and user ownership belong to
the main backend.

The threading lock provides safety within a single process. It does not
protect against concurrent writes from multiple processes. Multi-worker
deployments should use a shared, concurrency-safe storage backend.

Callers should provide a generated, non-identifying upload label rather
than an original filename or patient-identifying information.

Extracted text, findings details, prompts, LLM output, and API keys are
intentionally excluded from the upload record.
"""

import abc
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class UploadRecord(BaseModel):
    """Operational metadata for a processed report upload."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    uploaded_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    label: str = Field(
        description=(
            "Non-identifying upload label, preferably a generated request ID"
        )
    )
    content_type: Optional[str] = None
    file_size_bytes: int
    extraction_method: Optional[str] = None
    document_type: Optional[str] = None
    findings_count: int = 0
    status: Literal["success", "partial", "error"] = "success"
    processing_time_ms: Optional[float] = None
    page_count: int = 1
    report_date: Optional[str] = None
    llm_provider: Optional[str] = None


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------

class AbstractTracker(abc.ABC):
    """Interface implemented by upload trackers."""

    @abc.abstractmethod
    def record(self, record: UploadRecord) -> None:
        """Persist one upload record."""

    @abc.abstractmethod
    def get_all(
        self, limit: int = 100, offset: int = 0
    ) -> List[UploadRecord]:
        """Return paginated records, most recent first."""

    @abc.abstractmethod
    def count(self) -> int:
        """Return the total number of tracked records."""


# ---------------------------------------------------------------------------
# JSON file implementation
# ---------------------------------------------------------------------------

class JsonFileTracker(AbstractTracker):
    """Persist upload records to a local JSON file.

    Thread-safe within a single process. Not safe for concurrent writes
    from multiple OS processes.
    """

    def __init__(self, storage_file: Path) -> None:
        self._storage_file = Path(storage_file)
        self._lock = Lock()

    def _load(self) -> List[dict]:
        """Load stored records, returning an empty list on read/parse failure."""
        try:
            if not self._storage_file.exists():
                return []

            data = json.loads(
                self._storage_file.read_text(encoding="utf-8")
            )

            if not isinstance(data, list):
                logger.warning(
                    "Upload history has an invalid format; ignoring stored data."
                )
                return []

            return data

        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            # Do not log raw exceptions or filesystem paths.
            logger.warning("Failed to load upload history.")
            return []

    def _save(self, records: List[dict]) -> bool:
        """Atomically replace the JSON file; return whether saving succeeded."""
        tmp = self._storage_file.with_suffix(".tmp")

        try:
            self._storage_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            tmp.write_text(
                json.dumps(records, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            tmp.replace(self._storage_file)
            return True

        except (OSError, TypeError, ValueError):
            # Do not log raw exceptions or filesystem paths.
            logger.error("Failed to persist upload history.")

            # Best-effort cleanup of a temporary file.
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                logger.warning("Could not clean up a temporary upload-history file.")

            return False

    def record(self, record: UploadRecord) -> None:
        """Append a record and persist it."""
        with self._lock:
            records = self._load()
            records.append(record.model_dump())
            saved = self._save(records)

        if saved:
            # Do not log the label: callers might accidentally provide
            # an original filename or other identifying information.
            logger.info(
                "Upload tracked: id=%s status=%s",
                record.id,
                record.status,
            )

    def get_all(
        self, limit: int = 100, offset: int = 0
    ) -> List[UploadRecord]:
        """Return records in descending upload-time order."""
        if limit < 0 or offset < 0:
            raise ValueError("limit and offset must be non-negative")

        with self._lock:
            raw = self._load()

        raw.sort(
            key=lambda item: item.get("uploaded_at", ""),
            reverse=True,
        )

        page = raw[offset: offset + limit]
        return [UploadRecord(**item) for item in page]

    def count(self) -> int:
        """Return the number of readable stored records."""
        with self._lock:
            return len(self._load())


# ---------------------------------------------------------------------------
# No-op implementation
# ---------------------------------------------------------------------------

class NoOpTracker(AbstractTracker):
    """Discard records, useful for test isolation."""

    def record(self, record: UploadRecord) -> None:
        pass

    def get_all(
        self, limit: int = 100, offset: int = 0
    ) -> List[UploadRecord]:
        return []

    def count(self) -> int:
        return 0


# ---------------------------------------------------------------------------
# In-memory implementation
# ---------------------------------------------------------------------------

class InMemoryTracker(AbstractTracker):
    """Store records in memory without disk I/O."""

    def __init__(self) -> None:
        self._records: List[UploadRecord] = []
        self._lock = Lock()

    def record(self, record: UploadRecord) -> None:
        with self._lock:
            self._records.append(record)

    def get_all(
        self, limit: int = 100, offset: int = 0
    ) -> List[UploadRecord]:
        if limit < 0 or offset < 0:
            raise ValueError("limit and offset must be non-negative")

        with self._lock:
            sorted_records = sorted(
                self._records,
                key=lambda item: item.uploaded_at,
                reverse=True,
            )
            return sorted_records[offset: offset + limit]

    def count(self) -> int:
        with self._lock:
            return len(self._records)


# ---------------------------------------------------------------------------
# Default operational tracker
# ---------------------------------------------------------------------------

_DEFAULT_STORAGE_FILE = (
    Path(__file__).parent.parent / "data" / "upload_history.json"
)

_tracker: AbstractTracker = JsonFileTracker(_DEFAULT_STORAGE_FILE)


def configure_tracker(tracker: AbstractTracker) -> None:
    """Replace the active tracker."""
    global _tracker
    _tracker = tracker


def get_tracker() -> AbstractTracker:
    """Return the active tracker."""
    return _tracker


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def record_upload(record: UploadRecord) -> None:
    """Record an upload without allowing tracker failures to break processing."""
    try:
        _tracker.record(record)
    except Exception:  # noqa: BLE001
        # Intentionally omit exception details to avoid leaking sensitive data.
        logger.error("Upload tracking failed.")


def get_all_uploads(
    limit: int = 100, offset: int = 0
) -> List[UploadRecord]:
    """Return paginated upload records from the active tracker."""
    return _tracker.get_all(limit=limit, offset=offset)


def get_upload_count() -> int:
    """Return the number of records in the active tracker."""
    return _tracker.count()
