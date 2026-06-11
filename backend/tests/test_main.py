import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "SecurePulse API"

    def test_health_returns_version(self):
        response = client.get("/health")
        assert "version" in response.json()


class TestIngestEndpoint:
    def test_ingest_apache_log(self):
        log_content = b'192.168.1.1 - - [08/Jun/2026:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1024\n'

        with patch("app.main.crud.store_log_entries", return_value=1):
            with patch("app.main.parse_log_file", return_value=[{
                "timestamp": "2026-06-08T10:00:00",
                "source_ip": "192.168.1.1",
                "log_type": "apache",
                "raw_line": "test",
                "method": "GET",
                "path": "/index.html",
                "status_code": 200,
                "user": None,
                "event": None,
            }]):
                response = client.post(
                    "/ingest?log_type=apache",
                    files={"file": ("test.log", log_content, "text/plain")}
                )

        assert response.status_code == 200
        data = response.json()
        assert data["log_type"] == "apache"
        assert data["lines_stored"] == 1

    def test_ingest_rejects_non_log_file(self):
        response = client.post(
            "/ingest?log_type=apache",
            files={"file": ("test.txt", b"some content", "text/plain")}
        )
        assert response.status_code == 400

    def test_ingest_requires_log_type(self):
        response = client.post(
            "/ingest",
            files={"file": ("test.log", b"content", "text/plain")}
        )
        assert response.status_code == 422


class TestLogsEndpoint:
    def test_get_logs_returns_paginated_structure(self):
        with patch("app.main.crud.get_log_entries", return_value=(0, [])):
            response = client.get("/logs")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "results" in data

    def test_get_logs_invalid_page_rejected(self):
        response = client.get("/logs?page=0")
        assert response.status_code == 422


class TestAnalyzeEndpoint:
    def test_analyze_returns_summary(self):
        with patch("app.main.run_all_detectors", return_value={
            "total_alerts": 2,
            "by_severity": {"HIGH": 1, "MEDIUM": 1, "CRITICAL": 0, "LOW": 0},
            "by_type": {"BRUTE_FORCE_SSH": 1, "OFF_HOURS_ACCESS": 1}
        }):
            response = client.post("/analyze")

        assert response.status_code == 200
        data = response.json()
        assert data["total_alerts"] == 2
        assert "by_severity" in data


class TestMetricsEndpoint:
    def test_metrics_returns_expected_keys(self):
        with patch("app.main.crud") as mock_crud:
            mock_execute = MagicMock()
            mock_execute.scalar.return_value = 0
            mock_execute.all.return_value = []

            with patch("app.main.get_db") as mock_db:
                mock_session = MagicMock()
                mock_session.execute.return_value = mock_execute
                mock_db.return_value = iter([mock_session])

                response = client.get("/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "total_logs" in data
        assert "total_alerts" in data
        assert "detection_rate_percent" in data