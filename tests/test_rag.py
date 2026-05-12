from pathlib import Path

from app.services.chunker import TextChunker
from app.services.embeddings import LocalHashingEmbeddingProvider
from app.services.llm import LocalExtractiveLLMProvider
from app.services.rag import RAGService
from app.services.seed import ADVANCED_PYTHON_FASTAPI_SQL
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


def test_local_answer_extracts_relevant_sentence(tmp_path: Path) -> None:
    service = build_service(tmp_path / "rag.sqlite3")
    service.ingest_text(
        "A list is mutable in Python. A tuple is immutable in Python.",
        source="python-note",
    )

    response = service.answer("Is a tuple mutable or immutable?", top_k=1)

    assert "tuple is immutable" in response.answer


def test_project_answer_does_not_dump_openai_config(tmp_path: Path) -> None:
    service = build_service(tmp_path / "rag.sqlite3")
    service.ingest_text(
        """
        # AI RAG Backend System

        A portfolio-ready Retrieval-Augmented Generation backend built with FastAPI.

        ```env
        LLM_PROVIDER=openai
        OPENAI_API_KEY=your_key_here
        ```

        | Method | Path | Purpose |
        | --- | --- | --- |
        | GET | /health | Service status |
        """,
        source="project-readme",
    )

    response = service.answer("What is this project?", top_k=1)

    assert "Retrieval-Augmented Generation backend" in response.answer
    assert "OPENAI_API_KEY" not in response.answer


def test_local_answer_handles_basic_conversation(tmp_path: Path) -> None:
    service = build_service(tmp_path / "rag.sqlite3")
    service.ingest_text(
        "The assistant can answer questions using indexed documents and Python basics.",
        source="conversation-basics",
    )

    greeting = service.answer("hello", top_k=1)
    capability = service.answer("what can you do?", top_k=1)

    assert "Hi" in greeting.answer
    assert "retrieve relevant chunks" in capability.answer


def test_retrieves_advanced_fastapi_sql_training(tmp_path: Path) -> None:
    service = build_service(tmp_path / "rag.sqlite3")
    service.ingest_text(
        ADVANCED_PYTHON_FASTAPI_SQL,
        source="advanced-python-fastapi-sql",
        metadata={"topic": "python-fastapi-sql", "level": "advanced"},
    )

    response = service.answer("How do I prevent SQL injection in FastAPI?", top_k=3)

    assert response.citations
    assert response.citations[0].source == "advanced-python-fastapi-sql"
    assert "parameterized" in response.answer or "SQL injection" in response.answer
