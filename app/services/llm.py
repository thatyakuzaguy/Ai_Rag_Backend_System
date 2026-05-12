from abc import ABC, abstractmethod

from openai import OpenAI

from app.core.settings import Settings
from app.models.schemas import RetrievedChunk


class LLMProvider(ABC):
    @abstractmethod
    def answer(self, question: str, context: list[RetrievedChunk]) -> str:
        """Generate an answer grounded in retrieved context."""


class LocalExtractiveLLMProvider(LLMProvider):
    def answer(self, question: str, context: list[RetrievedChunk]) -> str:
        if not context:
            return "I do not have enough indexed context to answer that yet."

        strongest = context[0]
        sources = ", ".join(dict.fromkeys(item.source for item in context))
        return (
            f"Based on the retrieved context from {sources}: "
            f"{strongest.text[:700].strip()}"
        )


class OpenAIChatProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def answer(self, question: str, context: list[RetrievedChunk]) -> str:
        context_text = "\n\n".join(
            f"[{index + 1}] source={item.source} chunk={item.id}\n{item.text}"
            for index, item in enumerate(context)
        )
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer using only the supplied context. "
                        "If the context is insufficient, say so clearly. "
                        "Keep the answer concise and cite sources by bracket number."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context_text}\n\nQuestion: {question}",
                },
            ],
        )
        return response.choices[0].message.content or ""


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        return OpenAIChatProvider(api_key=settings.openai_api_key, model=settings.openai_chat_model)
    return LocalExtractiveLLMProvider()
