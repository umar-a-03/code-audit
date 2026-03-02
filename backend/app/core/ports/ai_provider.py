"""AI Provider protocol (abstract interface).

Defines the contract that all AI provider implementations must follow.
Supports OpenAI, Anthropic, Google Gemini, and others.
"""

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """AI Provider protocol.

    All AI providers (OpenAI, Anthropic, etc.) must implement this interface.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name.

        Returns:
            Provider name (e.g., 'openai', 'anthropic').
        """
        pass

    @abstractmethod
    async def analyze_code(
        self,
        code: str,
        file_path: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze code and return insights.

        Args:
            code: Source code to analyze.
            file_path: Path to the file (for context).
            context: Additional context (language, framework, etc.).

        Returns:
            Analysis results with:
            - issues: List of found issues
            - suggestions: Improvement suggestions
            - complexity: Code complexity metrics
            - security: Security concerns
        """
        pass

    @abstractmethod
    async def generate_report(
        self,
        audit_data: dict[str, Any],
        format_type: str = "markdown",
    ) -> str:
        """Generate a comprehensive audit report.

        Args:
            audit_data: All audit data including metrics and findings.
            format_type: Output format (markdown, html, json).

        Returns:
            Generated report as string.
        """
        pass

    @abstractmethod
    async def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Send a chat message and get response.

        Args:
            message: User message.
            history: Conversation history.

        Returns:
            AI response.
        """
        pass

    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Validate that the API key is working.

        Returns:
            True if API key is valid.
        """
        pass

    def get_model_info(self) -> dict[str, str]:
        """Get information about the AI model being used.

        Returns:
            Model information (name, version, capabilities).
        """
        return {
            "provider": self.provider_name,
        }
