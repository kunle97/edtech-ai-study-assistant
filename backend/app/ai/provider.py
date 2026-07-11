from abc import ABC, abstractmethod


class TemporaryAIError(Exception):
    """Raised when the AI provider is temporarily unavailable."""


class AIProvider(ABC):
    @abstractmethod
    def generate_response(
        self,
        *,
        message: str,
        conversation_history: list[dict[str, str]],
    ) -> str:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    def generate_response(
        self,
        *,
        message: str,
        conversation_history: list[dict[str, str]],
    ) -> str:
        normalized_message = message.strip()

        # Useful for manually testing retry behavior.
        if normalized_message.lower() == "simulate-ai-failure":
            raise TemporaryAIError("Mock AI provider is temporarily unavailable")

        return (
            "Here is a study-focused response to your question: "
            f"{normalized_message}"
        )


def get_ai_provider() -> AIProvider:
    return MockAIProvider()
