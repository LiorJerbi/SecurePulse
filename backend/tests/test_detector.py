import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from app.detector import (
    detect_brute_force_ssh,
    detect_off_hours_access,
    detect_privilege_escalation,
    detect_http_scanner,
)
from app.models import LogEntry


def make_log_entry(**kwargs) -> LogEntry:
    defaults = {
        "id": 1,
        "source_ip": "10.0.0.1",
        "log_type": "auth",
        "raw_line": "",
        "method": None,
        "path": None,
        "status_code": None,
        "user": None,
        "event": None,
        "timestamp": datetime(2026, 6, 8, 10, 0, 0),
    }
    defaults.update(kwargs)
    entry = LogEntry()
    for key, value in defaults.items():
        setattr(entry, key, value)
    return entry


class TestBruteForceDetector:
    def test_fires_on_five_failures_within_window(self):
        base_time = datetime(2026, 6, 8, 8, 10, 0)
        entries = [
            make_log_entry(
                id=i,
                source_ip="10.0.0.23",
                event="Failed password for root from 10.0.0.23 port 22 ssh2",
                timestamp=base_time + timedelta(seconds=i)
            )
            for i in range(5)
        ]

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = entries

        alerts = detect_brute_force_ssh(db)
        assert len(alerts) == 1
        assert alerts[0].alert_type == "BRUTE_FORCE_SSH"
        assert alerts[0].severity == "HIGH"
        assert alerts[0].source_ip == "10.0.0.23"

    def test_does_not_fire_on_four_failures(self):
        base_time = datetime(2026, 6, 8, 8, 10, 0)
        entries = [
            make_log_entry(
                id=i,
                source_ip="10.0.0.23",
                event="Failed password for root from 10.0.0.23 port 22 ssh2",
                timestamp=base_time + timedelta(seconds=i)
            )
            for i in range(4)
        ]

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = entries

        alerts = detect_brute_force_ssh(db)
        assert len(alerts) == 0

    def test_does_not_fire_when_spread_outside_window(self):
        base_time = datetime(2026, 6, 8, 8, 10, 0)
        entries = [
            make_log_entry(
                id=i,
                source_ip="10.0.0.23",
                event="Failed password for root from 10.0.0.23 port 22 ssh2",
                timestamp=base_time + timedelta(seconds=i * 30)
            )
            for i in range(5)
        ]

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = entries

        alerts = detect_brute_force_ssh(db)
        assert len(alerts) == 0


class TestOffHoursDetector:
    def test_fires_on_login_at_2am(self):
        entry = make_log_entry(
            source_ip="172.16.0.55",
            event="Accepted password for admin from 172.16.0.55 port 22 ssh2",
            timestamp=datetime(2026, 6, 8, 2, 30, 0)
        )

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = [entry]

        alerts = detect_off_hours_access(db)
        assert len(alerts) == 1
        assert alerts[0].alert_type == "OFF_HOURS_ACCESS"
        assert alerts[0].severity == "MEDIUM"

    def test_does_not_fire_on_login_at_9am(self):
        entry = make_log_entry(
            source_ip="192.168.1.1",
            event="Accepted password for alice from 192.168.1.1 port 22 ssh2",
            timestamp=datetime(2026, 6, 8, 9, 0, 0)
        )

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = [entry]

        alerts = detect_off_hours_access(db)
        assert len(alerts) == 0

    def test_boundary_midnight_fires(self):
        entry = make_log_entry(
            source_ip="10.0.0.1",
            event="Accepted password for user from 10.0.0.1 port 22 ssh2",
            timestamp=datetime(2026, 6, 8, 0, 0, 1)
        )

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = [entry]

        alerts = detect_off_hours_access(db)
        assert len(alerts) == 1


class TestPrivilegeEscalationDetector:
    def test_fires_on_non_whitelisted_user(self):
        entry = make_log_entry(
            source_ip="127.0.0.1",
            log_type="auth",
            event="hacker : TTY=pts/0 ; PWD=/home/hacker ; USER=root ; COMMAND=/bin/bash"
        )

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = [entry]

        with patch.dict("os.environ", {"WHITELISTED_SUDO_USERS": "alice,deploy,admin"}):
            alerts = detect_privilege_escalation(db)

        assert len(alerts) == 1
        assert alerts[0].alert_type == "PRIVILEGE_ESCALATION"
        assert alerts[0].severity == "CRITICAL"

    def test_does_not_fire_on_whitelisted_user(self):
        entry = make_log_entry(
            source_ip="127.0.0.1",
            log_type="auth",
            event="alice : TTY=pts/0 ; PWD=/home/alice ; USER=root ; COMMAND=/bin/bash"
        )

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = [entry]

        with patch("app.detector.WHITELISTED_SUDO_USERS", {"alice", "deploy", "admin"}):
            alerts = detect_privilege_escalation(db)

        assert len(alerts) == 0


class TestHttpScannerDetector:
    def test_fires_on_ten_404s_within_window(self):
        base_time = datetime(2026, 6, 8, 9, 0, 0)
        entries = [
            make_log_entry(
                id=i,
                source_ip="185.220.101.5",
                log_type="apache",
                status_code=404,
                timestamp=base_time + timedelta(seconds=i)
            )
            for i in range(10)
        ]

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = entries

        alerts = detect_http_scanner(db)
        assert len(alerts) == 1
        assert alerts[0].alert_type == "HTTP_SCANNER"
        assert alerts[0].severity == "MEDIUM"

    def test_does_not_fire_on_nine_404s(self):
        base_time = datetime(2026, 6, 8, 9, 0, 0)
        entries = [
            make_log_entry(
                id=i,
                source_ip="185.220.101.5",
                log_type="apache",
                status_code=404,
                timestamp=base_time + timedelta(seconds=i)
            )
            for i in range(9)
        ]

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = entries

        alerts = detect_http_scanner(db)
        assert len(alerts) == 0