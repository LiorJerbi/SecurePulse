import re
from datetime import datetime
from typing import Optional

APACHE_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" '
    r'(?P<status>\d{3}) '
    r'(?P<size>\d+|-)'
)

AUTH_PATTERN = re.compile(
    r'(?P<month>\w+)\s+(?P<day>\d+) (?P<time>\S+) \S+ \S+\[\d+\]: '
    r'(?P<event>.+)'
)

AUTH_IP_PATTERN = re.compile(r'from (\d+\.\d+\.\d+\.\d+)')
AUTH_USER_PATTERN = re.compile(r'for (\S+) from|: (\S+) :')


def parse_apache_line(line: str) -> Optional[dict]:
    match = APACHE_PATTERN.match(line.strip())
    if not match:
        return None

    timestamp_str = match.group("timestamp")
    timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")

    return {
        "timestamp": timestamp,
        "source_ip": match.group("ip"),
        "log_type": "apache",
        "raw_line": line.strip(),
        "method": match.group("method"),
        "path": match.group("path"),
        "status_code": int(match.group("status")),
        "user": None,
        "event": None,
    }


def parse_auth_line(line: str, year: int = 2026) -> Optional[dict]:
    match = AUTH_PATTERN.match(line.strip())
    if not match:
        return None

    time_str = f"{match.group('month')} {match.group('day')} {match.group('time')} {year}"
    try:
        timestamp = datetime.strptime(time_str, "%b %d %H:%M:%S %Y")
    except ValueError:
        return None

    event_str = match.group("event")

    ip_match = AUTH_IP_PATTERN.search(event_str)
    source_ip = ip_match.group(1) if ip_match else "127.0.0.1"

    user_match = AUTH_USER_PATTERN.search(event_str)
    if user_match:
        user = user_match.group(1) or user_match.group(2)
    else:
        user = None

    return {
        "timestamp": timestamp,
        "source_ip": source_ip,
        "log_type": "auth",
        "raw_line": line.strip(),
        "method": None,
        "path": None,
        "status_code": None,
        "user": user,
        "event": event_str.strip(),
    }


def parse_log_file(filepath: str, log_type: str) -> list[dict]:
    results = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if log_type == "apache":
                parsed = parse_apache_line(line)
            elif log_type == "auth":
                parsed = parse_auth_line(line)
            else:
                parsed = None

            if parsed:
                results.append(parsed)

    return results