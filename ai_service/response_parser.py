"""
Defensive parser for Claude AI responses.

The parser ensures that malformed or unexpected AI output never crashes
the HireLens application.
"""

import json
import logging
from typing import Any


logger = logging.getLogger(__name__)


FALLBACK_RESPONSE = {
    "error": "AI suggestions temporarily unavailable"
}


REQUIRED_KEYS = {
    "overall_feedback",
    "strengths",
    "priority_improvements",
    "skills_to_highlight",
    "tone_notes",
}


def _strip_code_fences(response_text: str) -> str:
    """
    Remove common Markdown code fences from an AI response.
    """

    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()

    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def parse_ai_response(response_text: str) -> dict[str, Any]:
    """
    Parse and validate a Claude response.

    Returns a validated structured dictionary on success.
    Returns a safe fallback dictionary on malformed output.
    """

    if not response_text or not response_text.strip():
        logger.warning("Claude returned an empty response.")
        return FALLBACK_RESPONSE.copy()

    cleaned_response = _strip_code_fences(response_text)

    try:
        parsed = json.loads(cleaned_response)
    except json.JSONDecodeError:
        logger.warning(
            "Claude returned invalid JSON. Raw response length: %s",
            len(response_text),
        )
        return FALLBACK_RESPONSE.copy()

    if not isinstance(parsed, dict):
        logger.warning("Claude response JSON was not an object.")
        return FALLBACK_RESPONSE.copy()

    missing_keys = REQUIRED_KEYS - set(parsed.keys())

    if missing_keys:
        logger.warning(
            "Claude response is missing required keys: %s",
            sorted(missing_keys),
        )
        return FALLBACK_RESPONSE.copy()

    if not isinstance(parsed["overall_feedback"], str):
        logger.warning("Invalid overall_feedback type from Claude.")
        return FALLBACK_RESPONSE.copy()

    if not isinstance(parsed["strengths"], list):
        logger.warning("Invalid strengths type from Claude.")
        return FALLBACK_RESPONSE.copy()

    if not isinstance(parsed["priority_improvements"], list):
        logger.warning(
            "Invalid priority_improvements type from Claude."
        )
        return FALLBACK_RESPONSE.copy()

    if not isinstance(parsed["skills_to_highlight"], list):
        logger.warning(
            "Invalid skills_to_highlight type from Claude."
        )
        return FALLBACK_RESPONSE.copy()

    if not isinstance(parsed["tone_notes"], str):
        logger.warning("Invalid tone_notes type from Claude.")
        return FALLBACK_RESPONSE.copy()

    for item in parsed["priority_improvements"]:
        if not isinstance(item, dict):
            logger.warning(
                "Invalid priority improvement item from Claude."
            )
            return FALLBACK_RESPONSE.copy()

        required_item_keys = {
            "area",
            "suggestion",
            "example",
        }

        if not required_item_keys.issubset(item.keys()):
            logger.warning(
                "Priority improvement is missing required fields."
            )
            return FALLBACK_RESPONSE.copy()

    return parsed