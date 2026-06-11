import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.crud import store_log_entries, get_log_entries
from app.models import LogEntry


def make_entry_dict(**kwargs):
    defaults = {
        "timestamp": datetime(2026, 6, 8, 10, 0, 0),
        "source_ip": "10.0.0.1",
        "log_type": "apache",
        "raw_line": "test line",
        "method": "GET",
        "path": "/index.html",
        "status_code": 200,
        "user": None,
        "event": None,
    }
    defaults.update(kwargs)
    return defaults


class TestStoreLogEntries:
    def test_stores_correct_count(self):
        db = MagicMock()
        entries = [make_entry_dict() for _ in range(5)]
        result = store_log_entries(db, entries)

        assert result == 5
        db.add_all.assert_called_once()
        db.commit.assert_called_once()

    def test_stores_zero_entries(self):
        db = MagicMock()
        result = store_log_entries(db, [])
        assert result == 0

    def test_creates_log_entry_objects(self):
        db = MagicMock()
        entries = [make_entry_dict(source_ip="192.168.1.1")]
        store_log_entries(db, entries)

        stored = db.add_all.call_args[0][0]
        assert len(stored) == 1
        assert isinstance(stored[0], LogEntry)
        assert stored[0].source_ip == "192.168.1.1"


class TestGetLogEntries:
    def _make_mock_db(self, entries, total=None):
        db = MagicMock()
        total = total if total is not None else len(entries)

        execute_results = [
            MagicMock(scalar=MagicMock(return_value=total)),
            MagicMock(scalars=MagicMock(
                return_value=MagicMock(all=MagicMock(return_value=entries))
            )),
        ]
        db.execute.side_effect = execute_results
        return db

    def test_returns_total_and_results(self):
        entry = LogEntry()
        entry.source_ip = "10.0.0.1"
        db = self._make_mock_db([entry], total=1)

        total, results = get_log_entries(db)
        assert total == 1
        assert len(results) == 1

    def test_returns_empty_results(self):
        db = self._make_mock_db([], total=0)
        total, results = get_log_entries(db)
        assert total == 0
        assert results == []