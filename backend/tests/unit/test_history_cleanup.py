"""History cleanup + 상세 조회 테스트"""

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from app.core.history import cleanup_old_history, get_recent_history, save_generation_record


class TestCleanupOldHistory:
    def test_deletes_old_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir)
            old_date = (datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%d")
            recent_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            (history_dir / f"{old_date}.jsonl").write_text('{"metrics":{}}')
            (history_dir / f"{recent_date}.jsonl").write_text('{"metrics":{}}')

            with patch("app.core.history.HISTORY_DIR", history_dir):
                deleted = cleanup_old_history(retention_days=30)

            assert deleted == 1
            assert not (history_dir / f"{old_date}.jsonl").exists()
            assert (history_dir / f"{recent_date}.jsonl").exists()

    def test_no_dir(self):
        with patch("app.core.history.HISTORY_DIR", Path("/nonexistent/path")):
            deleted = cleanup_old_history()
        assert deleted == 0

    def test_nothing_to_delete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir)
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            (history_dir / f"{today}.jsonl").write_text('{"metrics":{}}')

            with patch("app.core.history.HISTORY_DIR", history_dir):
                deleted = cleanup_old_history(retention_days=30)
            assert deleted == 0


class TestGetRecentHistoryAdvanced:
    def test_respects_limit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir)
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            filepath = history_dir / f"{today}.jsonl"

            lines = [json.dumps({"metrics": {"i": i}}) for i in range(20)]
            filepath.write_text("\n".join(lines))

            with patch("app.core.history.HISTORY_DIR", history_dir):
                result = get_recent_history(days=7, limit=5)
            assert len(result) == 5

    def test_multiple_days(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            history_dir = Path(tmpdir)

            for i in range(3):
                day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
                filepath = history_dir / f"{day}.jsonl"
                filepath.write_text(json.dumps({"metrics": {"day": i}}) + "\n")

            with patch("app.core.history.HISTORY_DIR", history_dir):
                result = get_recent_history(days=7, limit=50)
            assert len(result) == 3


class TestSaveGenerationRecordEdgeCases:
    def test_returns_none_on_permission_error(self):
        with patch("app.core.history.HISTORY_DIR", Path("/root/no_permission/history")):
            result = save_generation_record({"status": "test"})
        assert result is None

    def test_saves_without_blueprint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.core.history.HISTORY_DIR", Path(tmpdir)):
                path = save_generation_record({"total_time": 2.0, "status": "success"})
                assert path is not None
                content = json.loads(path.read_text().strip())
                assert "blueprint_meta" not in content
