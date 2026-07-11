from abc import ABC, abstractmethod


class TemporaryAIError(Exception):
    pass


class AIProvider(ABC):
    @abstractmethod
    def generate_response(
        self,
        *,
        message: str,
        conversation_history: list[dict[str, str]],
        curriculum_context: list[dict[str, str]],
    ) -> str:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    def generate_response(
        self,
        *,
        message: str,
        conversation_history: list[dict[str, str]],
        curriculum_context: list[dict[str, str]],
    ) -> str:
        if message.strip().lower() == "simulate-ai-failure":
            raise TemporaryAIError(
                "Mock AI provider is temporarily unavailable"
            )

        if not curriculum_context:
            return (
                "I could not find relevant curriculum content for that "
                "question. Please ask your instructor for clarification."
            )

        context = "\n\n".join(
            f"{item['topic']}: {item['body']}"
            for item in curriculum_context
        )

        return (
            f"Based on the curriculum:\n\n{context}\n\n"
            f"Answer to your question: {message.strip()}"
        )


def get_ai_provider() -> AIProvider:
    return MockAIProvider()
