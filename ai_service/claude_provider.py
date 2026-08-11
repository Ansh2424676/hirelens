"""
Claude AI provider for HireLens.

This module is responsible only for communicating with Claude and converting
the response into HireLens's structured AI suggestion format.
"""

import logging
import os

import anthropic

from ai_service.base import AIProvider
from ai_service.prompts import SYSTEM_PROMPT, build_user_prompt
from ai_service.response_parser import (
    FALLBACK_RESPONSE,
    parse_ai_response,
)


logger = logging.getLogger(__name__)


class ClaudeProvider(AIProvider):
    """
    Claude implementation of the HireLens AIProvider interface.
    """

    DEFAULT_MODEL = "claude-haiku-4-5-20251001"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_TOKENS = 1500

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize the Claude provider.

        API key is read from ANTHROPIC_API_KEY unless explicitly supplied.
        """

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        self.model = model or os.getenv(
            "ANTHROPIC_MODEL",
            self.DEFAULT_MODEL,
        )

        self.timeout = timeout

    def generate_suggestions(
        self,
        resume_text: str,
        jd_text: str,
        analysis: dict,
    ) -> dict:
        """
        Send resume, JD, and rule-based analysis to Claude.

        Any external API failure is converted into a safe fallback response
        so the core HireLens scoring workflow continues working.
        """

        if not self.api_key:
            logger.error(
                "ANTHROPIC_API_KEY is not configured."
            )
            return FALLBACK_RESPONSE.copy()

        try:
            client = anthropic.Anthropic(
                api_key=self.api_key,
                timeout=self.timeout,
            )

            response = client.messages.create(
                model=self.model,
                max_tokens=self.DEFAULT_MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": build_user_prompt(
                            resume_text=resume_text,
                            jd_text=jd_text,
                            analysis=analysis,
                        ),
                    }
                ],
            )

            response_text = self._extract_text(response)

            return parse_ai_response(response_text)

        except anthropic.AuthenticationError:
            logger.error(
                "Claude authentication failed. "
                "Check the configured API key."
            )
            return FALLBACK_RESPONSE.copy()

        except anthropic.RateLimitError:
            logger.error(
                "Claude API rate limit reached."
            )
            return FALLBACK_RESPONSE.copy()

        except anthropic.APITimeoutError:
            logger.error(
                "Claude API request timed out."
            )
            return FALLBACK_RESPONSE.copy()

        except anthropic.APIConnectionError:
            logger.error(
                "Could not connect to Claude API."
            )
            return FALLBACK_RESPONSE.copy()

        except anthropic.BadRequestError:
            logger.error(
                "Claude request was rejected. "
                "The account may have insufficient credits "
                "or the request configuration may be invalid."
            )
            return FALLBACK_RESPONSE.copy()

        except anthropic.APIError:
            logger.exception(
                "Claude API returned an API error."
            )
            return FALLBACK_RESPONSE.copy()

        except Exception:
            logger.exception(
                "Unexpected error while generating Claude suggestions."
            )
            return FALLBACK_RESPONSE.copy()

    @staticmethod
    def _extract_text(response) -> str:
        """
        Extract text content from an Anthropic Messages API response.
        """

        text_parts = []

        for block in response.content:
            if getattr(block, "type", None) == "text":
                text_parts.append(block.text)

        return "\n".join(text_parts).strip()