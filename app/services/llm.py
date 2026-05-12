import re
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

        sources = ", ".join(dict.fromkeys(item.source for item in context))
        answer = self._extract_relevant_excerpt(question, context)
        return f"Based on the best matching source ({sources}), the answer is: {answer}"

    @staticmethod
    def _extract_relevant_excerpt(question: str, context: list[RetrievedChunk]) -> str:
        query_terms = {
            token
            for token in re.findall(r"[a-zA-Z0-9_]+", question.lower())
            if len(token) > 2
        }
        candidates: list[tuple[int, str]] = []
        for item in context:
            parts = re.split(r"(?<=[.!?])\s+|\n+", item.text)
            for part in parts:
                sentence = part.strip(" -")
                if not sentence:
                    continue
                sentence_terms = set(re.findall(r"[a-zA-Z0-9_]+", sentence.lower()))
                score = len(query_terms & sentence_terms)
                if score:
                    candidates.append((score, sentence))

        if candidates:
            candidates.sort(key=lambda candidate: (candidate[0], len(candidate[1])), reverse=True)
            answer = candidates[0][1][:700].strip()
        else:
            answer = context[0].text[:700].strip()

        if answer and answer[-1] not in ".!?":
            answer = f"{answer}."
        return answer


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
