"""
Provider-agnostic AI service interface for HireLens.

Day 6:
Defines the contract that every AI provider must implement.
"""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """
    Abstract interface for AI suggestion providers.

    Keeping this interface provider-agnostic allows HireLens to switch
    AI providers later without changing the Flask route or scoring engine.
    """

    @abstractmethod
    def generate_suggestions(
        self,
        resume_text: str,
        jd_text: str,
        analysis: dict,
    ) -> dict:
        """
        Generate structured resume improvement suggestions.

        Args:
            resume_text: Raw extracted resume text.
            jd_text: Job description text.
            analysis: Rule-based scoring analysis from scoring.engine.analyze().

        Returns:
            A structured dictionary containing AI suggestions or a
            user-friendly error structure.
        """
        raise NotImplementedError