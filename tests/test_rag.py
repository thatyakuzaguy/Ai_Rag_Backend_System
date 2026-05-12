from pathlib import Path

from app.services.chunker import TextChunker
from app.services.embeddings import LocalHashingEmbeddingProvider
from app.services.llm import LocalExtractiveLLMProvider
from app.services.rag import RAGService
from app.services.vector_store import SQLiteVectorStore


def build_service(database_path: Path) -> RAGService:
    return RAGService(
        chunker=TextChunker(chunk_size=250, chunk_overlap=40),
        embedder=LocalHashingEmbeddingProvider(dimensions=128),
        store=SQLiteVectorStore(database_path),
        llm=LocalExtractiveLLMProvider(),
    )


def test_rag_ingests_and_retrieves_relevant_context(tmp_path: Path) -> None:
    service = build_service(tmp_path / "rag.sqlite3")
    service.ingest_text(
        "FastAPI is a Python framework for building APIs. It supports type hints.",
        source="fastapi-note",
    )
    service.ingest_text(
        "Vector search retrieves semantically relevant chunks for RAG systems.",
        source="rag-note",
    )

    results = service.search("How does vector search help RAG?", top_k=1)

    assert len(results) == 1
    assert results[0].source == "rag-note"


def test_rag_answer_contains_citations(tmp_path: Path) -> None:
    service = build_service(tmp_path / "rag.sqlite3")
    service.ingest_text("RAG answers should be grounded in retrieved context.", source="rag-note")

    response = service.answer("What should RAG answers use?", top_k=1)

    assert response.citations
    assert response.context
    assert "retrieved context" in response.answer
