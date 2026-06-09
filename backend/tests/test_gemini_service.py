import pytest
from unittest.mock import MagicMock, patch
from app.gemini_service import (
    build_prompt,
    explain_alert,
    _fallback_explanation,
    call_gemini_with_backoff,
)
from app.models import Alert


def make_alert(**kwargs) -> Alert:
    defaults = {
        "id": 1,
        "alert_type": "BRUTE_FORCE_SSH",
        "severity": "HIGH",
        "source_ip": "10.0.0.23",
        "description": "5 failed SSH attempts from 10.0.0.23 within 60 seconds",
        "ai_explanation": None,
    }
    defaults.update(kwargs)
    alert = Alert()
    for key, value in defaults.items():
        setattr(alert, key, value)
    return alert


class TestBuildPrompt:
    def test_prompt_contains_alert_fields(self):
        alert = make_alert()
        prompt = build_prompt(alert)

        assert "BRUTE_FORCE_SSH" in prompt
        assert "HIGH" in prompt
        assert "10.0.0.23" in prompt
        assert "5 failed SSH attempts" in prompt

    def test_prompt_contains_output_format(self):
        alert = make_alert()
        prompt = build_prompt(alert)

        assert "WHAT HAPPENED" in prompt
        assert "WHY IT MATTERS" in prompt
        assert "RECOMMENDED ACTION" in prompt


class TestExplainAlert:
    def test_returns_gemini_response_on_success(self):
        alert = make_alert()

        with patch("app.gemini_service.call_gemini_with_backoff") as mock_call:
            mock_call.return_value = "WHAT HAPPENED: Test\nWHY IT MATTERS: Test\nRECOMMENDED ACTION: Test"
            result = explain_alert(alert)

        assert "WHAT HAPPENED" in result
        mock_call.assert_called_once()

    def test_returns_fallback_when_gemini_fails(self):
        alert = make_alert()

        with patch("app.gemini_service.call_gemini_with_backoff") as mock_call:
            mock_call.side_effect = Exception("API unavailable")
            result = explain_alert(alert)

        assert "WHAT HAPPENED" in result
        assert "brute force" in result.lower()

    def test_fallback_exists_for_all_alert_types(self):
        for alert_type in ["BRUTE_FORCE_SSH", "OFF_HOURS_ACCESS", "PRIVILEGE_ESCALATION", "HTTP_SCANNER"]:
            alert = make_alert(alert_type=alert_type)
            result = _fallback_explanation(alert)
            assert "WHAT HAPPENED" in result
            assert "WHY IT MATTERS" in result
            assert "RECOMMENDED ACTION" in result


class TestExponentialBackoff:
    def test_retries_on_rate_limit(self):
        with patch("app.gemini_service.model") as mock_model:
            with patch("app.gemini_service.time.sleep") as mock_sleep:
                mock_model.generate_content.side_effect = [
                    Exception("429 rate limit exceeded"),
                    Exception("429 rate limit exceeded"),
                    MagicMock(text="success response"),
                ]
                result = call_gemini_with_backoff("test prompt")

        assert result == "success response"
        assert mock_sleep.call_count == 2
        assert mock_model.generate_content.call_count == 3

    def test_sleep_doubles_each_retry(self):
        with patch("app.gemini_service.model") as mock_model:
            with patch("app.gemini_service.time.sleep") as mock_sleep:
                mock_model.generate_content.side_effect = [
                    Exception("429 rate limit exceeded"),
                    Exception("429 rate limit exceeded"),
                    MagicMock(text="success"),
                ]
                call_gemini_with_backoff("test prompt")

        sleep_calls = [call.args[0] for call in mock_sleep.call_args_list]
        assert sleep_calls[1] == sleep_calls[0] * 2