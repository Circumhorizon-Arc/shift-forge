"""Tests for upload tracker: persistence, pagination, ordering, isolation, and error handling."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.tracker import (
    AbstractTracker,
    InMemoryTracker,
    JsonFileTracker,
    NoOpTracker,
    UploadRecord,
    record_upload,
    get_all_uploads,
    get_upload_count,
)


def _make_record(**kwargs) -> UploadRecord:
    defaults = dict(label="upload-abc123.pdf", file_size_bytes=1024)
    defaults.update(kwargs)
    return UploadRecord(**defaults)


# ---------------------------------------------------------------------------
# NoOpTracker
# ---------------------------------------------------------------------------

class TestNoOpTracker:
    def test_record_does_nothing(self):
        t = NoOpTracker()
        t.record(_make_record())
        assert t.count() == 0

    def test_get_all_returns_empty(self):
        t = NoOpTracker()
        assert t.get_all() == []

    def test_count_returns_zero(self):
        assert NoOpTracker().count() == 0


# ---------------------------------------------------------------------------
# InMemoryTracker
# ---------------------------------------------------------------------------

class TestInMemoryTracker:
    def test_record_and_count(self):
        t = InMemoryTracker()
        t.record(_make_record(label="a.pdf", file_size_bytes=100))
        t.record(_make_record(label="b.pdf", file_size_bytes=200))
        assert t.count() == 2

    def test_get_all_most_recent_first(self):
        import time
        t = InMemoryTracker()
        t.record(_make_record(label="first.pdf", file_size_bytes=1))
        time.sleep(0.01)
        t.record(_make_record(label="second.pdf", file_size_bytes=2))
        records = t.get_all()
        assert records[0].label == "second.pdf"
        assert records[1].label == "first.pdf"

    def test_pagination_limit(self):
        t = InMemoryTracker()
        for i in range(10):
            t.record(_make_record(label=f"r{i}.pdf", file_size_bytes=i))
        assert len(t.get_all(limit=5)) == 5

    def test_pagination_offset(self):
        t = InMemoryTracker()
        for i in range(10):
            t.record(_make_record(label=f"r{i}.pdf", file_size_bytes=i))
        all_records = t.get_all(limit=100)
        page2 = t.get_all(limit=5, offset=5)
        assert page2 == all_records[5:10]


# ---------------------------------------------------------------------------
# JsonFileTracker
# ---------------------------------------------------------------------------

class TestJsonFileTracker:
    def test_persists_to_disk(self, tmp_path: Path):
        storage = tmp_path / "history.json"
        t = JsonFileTracker(storage)
        t.record(_make_record(label="report.pdf", file_size_bytes=512))
        assert storage.exists()
        data = json.loads(storage.read_text())
        assert len(data) == 1
        assert data[0]["label"] == "report.pdf"

    def test_appends_multiple_records(self, tmp_path: Path):
        storage = tmp_path / "history.json"
        t = JsonFileTracker(storage)
        t.record(_make_record(label="a.pdf", file_size_bytes=1))
        t.record(_make_record(label="b.pdf", file_size_bytes=2))
        data = json.loads(storage.read_text())
        assert len(data) == 2

    def test_get_all_most_recent_first(self, tmp_path: Path):
        import time
        storage = tmp_path / "history.json"
        t = JsonFileTracker(storage)
        t.record(_make_record(label="older.pdf", file_size_bytes=1))
        time.sleep(0.01)
        t.record(_make_record(label="newer.pdf", file_size_bytes=2))
        records = t.get_all()
        assert records[0].label == "newer.pdf"

    def test_count_matches_stored_records(self, tmp_path: Path):
        storage = tmp_path / "history.json"
        t = JsonFileTracker(storage)
        for i in range(7):
            t.record(_make_record(label=f"r{i}.pdf", file_size_bytes=i))
        assert t.count() == 7

    def test_corrupted_file_returns_empty_list(self, tmp_path: Path):
        storage = tmp_path / "history.json"
        storage.write_text("this is not valid json", encoding="utf-8")
        t = JsonFileTracker(storage)
        assert t.get_all() == []
        assert t.count() == 0

    def test_record_survives_corrupted_file(self, tmp_path: Path):
        """A corrupted existing file should not prevent new records being saved."""
        storage = tmp_path / "history.json"
        storage.write_text("CORRUPT", encoding="utf-8")
        t = JsonFileTracker(storage)
        t.record(_make_record(label="after_corrupt.pdf", file_size_bytes=1))
        # File should now contain a valid single-item list
        data = json.loads(storage.read_text())
        assert len(data) == 1

    def test_missing_directory_is_created(self, tmp_path: Path):
        storage = tmp_path / "subdir" / "history.json"
        t = JsonFileTracker(storage)
        t.record(_make_record(label="r.pdf", file_size_bytes=1))
        assert storage.exists()


# ---------------------------------------------------------------------------
# Module-level convenience functions & isolation
# ---------------------------------------------------------------------------

class TestModuleLevelFunctions:
    def test_record_upload_uses_active_tracker(self, isolated_tracker: InMemoryTracker):
        """record_upload() must delegate to the module-level tracker (patched to InMemoryTracker)."""
        record_upload(_make_record(label="module-test.pdf", file_size_bytes=999))
        assert isolated_tracker.count() == 1

    def test_get_all_uploads_delegates(self, isolated_tracker: InMemoryTracker):
        isolated_tracker.record(_make_record(label="x.pdf", file_size_bytes=1))
        result = get_all_uploads()
        assert len(result) == 1

    def test_get_upload_count_delegates(self, isolated_tracker: InMemoryTracker):
        isolated_tracker.record(_make_record(label="y.pdf", file_size_bytes=1))
        assert get_upload_count() == 1

    def test_record_upload_swallows_tracker_exception(self, isolated_tracker: InMemoryTracker):
        """Tracker failure must not propagate — it should be logged and swallowed."""
        class BrokenTracker(AbstractTracker):
            def record(self, r): raise RuntimeError("storage down")
            def get_all(self, limit=100, offset=0): return []
            def count(self): return 0

        with patch("app.tracker._tracker", BrokenTracker()):
            # Should not raise
            record_upload(_make_record(label="broken.pdf", file_size_bytes=1))


# ---------------------------------------------------------------------------
# Verify tests do NOT write to operational storage
# ---------------------------------------------------------------------------

class TestOperationalStorageNotPolluted:
    def test_pipeline_test_does_not_touch_operational_file(
        self, tmp_path: Path, isolated_tracker: InMemoryTracker
    ):
        """Prove that the isolated_tracker autouse fixture prevents disk writes."""
        from app.tracker import _DEFAULT_STORAGE_FILE

        operational_existed_before = _DEFAULT_STORAGE_FILE.exists()
        record_upload(_make_record(label="isolation-check.pdf", file_size_bytes=1))
        operational_existed_after = _DEFAULT_STORAGE_FILE.exists()

        # The operational file should not have been created/modified by this call
        if not operational_existed_before:
            assert not operational_existed_after, (
                "record_upload() wrote to operational storage despite isolated_tracker patch"
            )
        # In-memory tracker should have the record
        assert isolated_tracker.count() == 1
