import pytest
from app.parser import parse_apache_line, parse_auth_line, parse_log_file


class TestApacheParser:
    def test_valid_get_request(self):
        line = '192.168.1.105 - - [08/Jun/2026:08:12:01 +0000] "GET /index.html HTTP/1.1" 200 1024'
        result = parse_apache_line(line)

        assert result is not None
        assert result["source_ip"] == "192.168.1.105"
        assert result["method"] == "GET"
        assert result["path"] == "/index.html"
        assert result["status_code"] == 200
        assert result["log_type"] == "apache"

    def test_failed_login_returns_401(self):
        line = '10.0.0.23 - - [08/Jun/2026:08:12:45 +0000] "POST /login HTTP/1.1" 401 256'
        result = parse_apache_line(line)

        assert result is not None
        assert result["status_code"] == 401
        assert result["method"] == "POST"
        assert result["path"] == "/login"

    def test_invalid_line_returns_none(self):
        result = parse_apache_line("this is not a log line")
        assert result is None

    def test_empty_line_returns_none(self):
        result = parse_apache_line("")
        assert result is None

    def test_user_and_event_are_none_for_apache(self):
        line = '192.168.1.105 - - [08/Jun/2026:08:12:01 +0000] "GET /index.html HTTP/1.1" 200 1024'
        result = parse_apache_line(line)
        assert result["user"] is None
        assert result["event"] is None


class TestAuthParser:
    def test_failed_ssh_login(self):
        line = "Jun  8 08:10:01 server sshd[1234]: Failed password for root from 10.0.0.23 port 54321 ssh2"
        result = parse_auth_line(line)

        assert result is not None
        assert result["source_ip"] == "10.0.0.23"
        assert result["user"] == "root"
        assert result["log_type"] == "auth"
        assert "Failed password" in result["event"]

    def test_successful_ssh_login(self):
        line = "Jun  8 08:10:06 server sshd[1235]: Accepted password for deploy from 192.168.1.105 port 60001 ssh2"
        result = parse_auth_line(line)

        assert result is not None
        assert result["source_ip"] == "192.168.1.105"
        assert result["user"] == "deploy"
        assert "Accepted password" in result["event"]

    def test_sudo_event_uses_loopback_ip(self):
        line = "Jun  8 08:15:00 server sudo[5678]: alice : TTY=pts/0 ; PWD=/home/alice ; USER=root ; COMMAND=/bin/bash"
        result = parse_auth_line(line)

        assert result is not None
        assert result["source_ip"] == "127.0.0.1"

    def test_invalid_line_returns_none(self):
        result = parse_auth_line("not a real log line")
        assert result is None

    def test_method_and_status_are_none_for_auth(self):
        line = "Jun  8 08:10:01 server sshd[1234]: Failed password for root from 10.0.0.23 port 54321 ssh2"
        result = parse_auth_line(line)
        assert result["method"] is None
        assert result["status_code"] is None


class TestParseLogFile:
    def test_apache_file_parses_all_lines(self):
        results = parse_log_file("app/sample_logs/apache_access.log", "apache")
        assert len(results) == 10

    def test_auth_file_parses_all_lines(self):
        results = parse_log_file("app/sample_logs/auth.log", "auth")
        assert len(results) == 10

    def test_unknown_log_type_returns_empty(self):
        results = parse_log_file("app/sample_logs/apache_access.log", "unknown")
        assert results == []