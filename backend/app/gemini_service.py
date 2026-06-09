import os
import time
import logging
import google.generativeai as genai
from app.models import Alert

logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

PROMPT_TEMPLATE = """
You are a cybersecurity analyst reviewing a security alert.
Analyze the following alert and provide a clear, concise explanation.

Alert Type: {alert_type}
Severity: {severity}
Source IP: {source_ip}
Description: {description}

Respond in exactly this format:
WHAT HAPPENED: (1-2 sentences explaining what the alert means in plain English)
WHY IT MATTERS: (1 sentence on the potential risk)
RECOMMENDED ACTION: (1-2 sentences on what to do next)
"""

MAX_RETRIES = 3
BASE_DELAY = 1.0


def build_prompt(alert: Alert) -> str:
    return PROMPT_TEMPLATE.format(
        alert_type=alert.alert_type,
        severity=alert.severity,
        source_ip=alert.source_ip,
        description=alert.description,
    )


def call_gemini_with_backoff(prompt: str) -> str:
    delay = BASE_DELAY

    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            error_msg = str(e).lower()

            if "quota" in error_msg or "rate" in error_msg or "429" in error_msg:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(
                        f"Gemini rate limit hit, retrying in {delay}s "
                        f"(attempt {attempt + 1}/{MAX_RETRIES})"
                    )
                    time.sleep(delay)
                    delay *= 2
                else:
                    logger.error("Gemini rate limit exceeded after all retries")
                    raise

            elif "api_key" in error_msg or "401" in error_msg or "403" in error_msg:
                logger.error("Gemini API key invalid or missing")
                raise

            else:
                logger.error(f"Unexpected Gemini error: {e}")
                raise

    raise RuntimeError("Gemini call failed after all retries")


def explain_alert(alert: Alert) -> str:
    """
    Generate an AI explanation for a security alert using Gemini.
    Falls back to a static explanation if the API is unavailable.

    Args:
        alert: Alert model instance to explain

    Returns:
        Plain-English explanation string with WHAT HAPPENED,
        WHY IT MATTERS, and RECOMMENDED ACTION sections
    """
    try:
        prompt = build_prompt(alert)
        explanation = call_gemini_with_backoff(prompt)
        return explanation

    except Exception as e:
        logger.warning(f"Gemini unavailable for alert {alert.id}, using fallback: {e}")
        return _fallback_explanation(alert)


def _fallback_explanation(alert: Alert) -> str:
    fallbacks = {
        "BRUTE_FORCE_SSH": (
            "WHAT HAPPENED: Multiple failed SSH login attempts were detected from this IP in a short time window.\n"
            "WHY IT MATTERS: This pattern is consistent with an automated brute force attack trying to guess credentials.\n"
            "RECOMMENDED ACTION: Block this IP at the firewall and review SSH configuration to disable password authentication."
        ),
        "OFF_HOURS_ACCESS": (
            "WHAT HAPPENED: A successful login occurred during off-hours (midnight to 5am).\n"
            "WHY IT MATTERS: Legitimate users rarely log in at this time, suggesting possible unauthorized access.\n"
            "RECOMMENDED ACTION: Verify with the account owner whether this login was expected and review session activity."
        ),
        "PRIVILEGE_ESCALATION": (
            "WHAT HAPPENED: A user executed a sudo command without being on the approved whitelist.\n"
            "WHY IT MATTERS: Unauthorized privilege escalation can indicate an attacker gaining root access.\n"
            "RECOMMENDED ACTION: Immediately revoke sudo access for this user and audit what commands were run."
        ),
        "HTTP_SCANNER": (
            "WHAT HAPPENED: A high volume of 404 responses were returned to this IP in a short time window.\n"
            "WHY IT MATTERS: This pattern is typical of automated scanners probing for vulnerable endpoints.\n"
            "RECOMMENDED ACTION: Block this IP and review web server logs for any successful hits on sensitive paths."
        ),
    }
    return fallbacks.get(
        alert.alert_type,
        f"Alert type {alert.alert_type} detected from {alert.source_ip}. Review logs manually."
    )