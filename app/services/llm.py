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

        answer = self._answer_common_question(question, context)
        if answer is None:
            answer = self._extract_relevant_excerpt(question, context)
        return answer

    @staticmethod
    def _answer_common_question(question: str, context: list[RetrievedChunk]) -> str | None:
        question_lower = question.lower()
        all_text = "\n".join(item.text for item in context)
        source_names = {item.source for item in context}
        normalized_question = re.sub(r"[^a-zA-Z0-9\s]", " ", question_lower)
        words = set(normalized_question.split())

        if words & {"hi", "hello", "hey", "hola"}:
            return (
                "Hi. I can help you search indexed documents, answer RAG questions, "
                "or explain Python basics."
            )
        if any(phrase in question_lower for phrase in ("thank you", "thanks", "gracias")):
            return "You are welcome. Ask me anything about the indexed knowledge."
        if any(phrase in question_lower for phrase in ("who are you", "what are you")):
            return "I am the demo assistant for this AI RAG Backend System."
        if any(
            phrase in question_lower
            for phrase in ("what can you do", "what do you do", "how can you help")
        ):
            return (
                "I can ingest documents, retrieve relevant chunks, answer questions with "
                "citations, explain Python basics, and describe this RAG project."
            )
        if any(phrase in question_lower for phrase in ("how does it work", "how does this work", "how it works")):
            if "rag pipeline" in all_text.lower() or "retrieves similar context" in all_text.lower():
                return (
                    "It works by splitting documents into chunks, creating embeddings for those "
                    "chunks, storing them in SQLite, retrieving the most relevant context for a "
                    "question, and generating an answer with citations."
                )

        if "project-readme" in source_names:
            if any(phrase in question_lower for phrase in ("what is this", "what is it", "what does this do")):
                return (
                    "AI RAG Backend System is a FastAPI Retrieval-Augmented Generation "
                    "backend for ingesting documents, storing searchable embeddings, "
                    "retrieving relevant context, and answering questions with citations."
                )
            if "endpoint" in question_lower or "api" in question_lower:
                return (
                    "The API includes GET /health, POST /documents, POST /documents/file, "
                    "GET /search, POST /chat, and DELETE /documents/{source}."
                )
            if any(phrase in question_lower for phrase in ("how do i use", "how to use", "use it")):
                return (
                    "Use POST /documents to ingest text, GET /search to retrieve relevant "
                    "chunks, and POST /chat to ask questions grounded in the indexed context."
                )
            if "openai" in question_lower:
                return (
                    "OpenAI mode is optional. Set EMBEDDING_PROVIDER=openai, "
                    "LLM_PROVIDER=openai, OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL, "
                    "and OPENAI_CHAT_MODEL in your environment."
                )

        if "python-basics" in source_names and "virtual environment" in question_lower:
            return (
                "A Python virtual environment isolates a project's dependencies. "
                "Create one with python -m venv .venv, activate it on Windows with "
                ".\\.venv\\Scripts\\activate, then install packages with pip."
            )

        if "common beginner mistakes" in all_text and "mistake" in question_lower:
            return (
                "Common Python beginner mistakes include forgetting indentation, mixing tabs "
                "and spaces, mutating a list while looping over it, using mutable default "
                "arguments, forgetting to activate the virtual environment, and not closing "
                "files or database connections."
            )

        return None

    @staticmethod
    def _extract_relevant_excerpt(question: str, context: list[RetrievedChunk]) -> str:
        query_terms = {
            token
            for token in re.findall(r"[a-zA-Z0-9_]+", question.lower())
            if len(token) > 2
        }
        candidates: list[tuple[int, str]] = []
        for item in context:
            cleaned = LocalExtractiveLLMProvider._strip_markdown_noise(item.text)
            parts = re.split(r"(?<=[.!?])\s+|\n+", cleaned)
            for part in parts:
                sentence = part.strip(" -")
                if not sentence or LocalExtractiveLLMProvider._is_noisy_excerpt(sentence):
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

    @staticmethod
    def _strip_markdown_noise(text: str) -> str:
        text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
        text = re.sub(r"\|.*\|", " ", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        return text

    @staticmethod
    def _is_noisy_excerpt(sentence: str) -> bool:
        noisy_markers = ("OPENAI_API_KEY", "LLM_PROVIDER", "EMBEDDING_PROVIDER", "```", "| ---")
        return any(marker in sentence for marker in noisy_markers)


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
