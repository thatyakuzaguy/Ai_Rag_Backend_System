import hashlib
from typing import Any

from app.models.schemas import ChatMessage, ChatResponse, Citation, RetrievedChunk
from app.services.chunker import TextChunker
from app.services.embeddings import EmbeddingProvider
from app.services.llm import LLMProvider
from app.services.vector_store import SQLiteVectorStore


class RAGService:
    def __init__(
        self,
        chunker: TextChunker,
        embedder: EmbeddingProvider,
        store: SQLiteVectorStore,
        llm: LLMProvider,
        default_top_k: int = 4,
    ) -> None:
        self.chunker = chunker
        self.embedder = embedder
        self.store = store
        self.llm = llm
        self.default_top_k = default_top_k

    def ingest_text(self, text: str, source: str, metadata: dict[str, Any] | None = None) -> int:
        chunks = self.chunker.split(text)
        embeddings = self.embedder.embed([chunk.text for chunk in chunks])
        rows = []
        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = self._chunk_id(source=source, chunk_index=chunk.index, text=chunk.text)
            rows.append(
                {
                    "id": chunk_id,
                    "source": source,
                    "chunk_index": chunk.index,
                    "text": chunk.text,
                    "embedding": embedding,
                    "metadata": {**(metadata or {}), "chunk_index": chunk.index},
                }
            )
        return self.store.add_chunks(rows)

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        [query_embedding] = self.embedder.embed([query])
        return self.store.search(query_embedding=query_embedding, top_k=top_k or self.default_top_k)

    def answer(
        self,
        question: str,
        top_k: int | None = None,
        history: list[ChatMessage] | None = None,
    ) -> ChatResponse:
        retrieval_query = self._build_retrieval_query(question, history or [])
        context = self.search(retrieval_query, top_k=top_k)
        answer = self.llm.answer(self._build_generation_question(question, history or []), context)
        citations = [
            Citation(source=item.source, chunk_id=item.id, score=item.score)
            for item in context
        ]
        return ChatResponse(
            question=question,
            answer=answer,
            citations=citations,
            context=context,
        )

    @staticmethod
    def _chunk_id(source: str, chunk_index: int, text: str) -> str:
        digest = hashlib.sha256(f"{source}:{chunk_index}:{text}".encode("utf-8")).hexdigest()
        return digest[:24]

    @staticmethod
    def _build_retrieval_query(question: str, history: list[ChatMessage]) -> str:
        if not history:
            return question
        recent_history = "\n".join(
            f"{message.role}: {message.content}"
            for message in history[-6:]
        )
        return f"{recent_history}\nuser: {question}"

    @staticmethod
    def _build_generation_question(question: str, history: list[ChatMessage]) -> str:
        if not history:
            return question
        recent_history = "\n".join(
            f"{message.role}: {message.content}"
            for message in history[-6:]
        )
        return (
            "Use this recent conversation to understand references like 'it', "
            "'that', or 'the previous topic'.\n"
            f"{recent_history}\nCurrent question: {question}"
        )
