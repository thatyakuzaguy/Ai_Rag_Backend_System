from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.services.chunker import TextChunker
from app.services.embeddings import LocalHashingEmbeddingProvider
from app.services.llm import LocalExtractiveLLMProvider
from app.services.rag import RAGService
from app.services.vector_store import SQLiteVectorStore


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    from app.core.dependencies import (
        get_chunker,
        get_embedding_provider,
        get_llm_provider,
        get_rag_service,
        get_vector_store,
    )
    from app.main import app

    store = SQLiteVectorStore(tmp_path / "test.sqlite3")
    embedder = LocalHashingEmbeddingProvider(dimensions=128)
    chunker = TextChunker(chunk_size=250, chunk_overlap=40)
    llm = LocalExtractiveLLMProvider()
    rag = RAGService(chunker=chunker, embedder=embedder, store=store, llm=llm)

    app.dependency_overrides[get_vector_store] = lambda: store
    app.dependency_overrides[get_embedding_provider] = lambda: embedder
    app.dependency_overrides[get_chunker] = lambda: chunker
    app.dependency_overrides[get_llm_provider] = lambda: llm
    app.dependency_overrides[get_rag_service] = lambda: rag

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_health_empty_store(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "documents": 0, "chunks_indexed": 0}


def test_home_page_returns_ui(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AI RAG Backend System" in response.text


def test_health_after_ingest(client: TestClient) -> None:
    client.post("/documents", json={"source": "doc-a", "text": "Hello world from doc-a."})
    client.post("/documents", json={"source": "doc-b", "text": "Another document here."})

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["documents"] == 2
    assert response.json()["chunks_indexed"] >= 2


def test_ingest_document_returns_201(client: TestClient) -> None:
    response = client.post(
        "/documents",
        json={"source": "test-source", "text": "FastAPI makes building APIs easy."},
    )

    assert response.status_code == 201
    assert response.json()["source"] == "test-source"
    assert response.json()["chunks_indexed"] >= 1


def test_ingest_document_empty_text_rejected(client: TestClient) -> None:
    response = client.post("/documents", json={"source": "s", "text": ""})

    assert response.status_code == 422


def test_ingest_file_txt(client: TestClient, tmp_path: Path) -> None:
    text_file = tmp_path / "sample.txt"
    text_file.write_text("This is a plain text file with content for RAG indexing.")

    with text_file.open("rb") as file:
        response = client.post(
            "/documents/file",
            files={"file": ("sample.txt", file, "text/plain")},
        )

    assert response.status_code == 201
    assert response.json()["source"] == "sample.txt"


def test_ingest_file_unsupported_extension_rejected(
    client: TestClient,
    tmp_path: Path,
) -> None:
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake content")

    with pdf.open("rb") as file:
        response = client.post(
            "/documents/file",
            files={"file": ("report.pdf", file, "application/pdf")},
        )

    assert response.status_code == 400


def test_search_returns_results(client: TestClient) -> None:
    client.post(
        "/documents",
        json={"source": "rag-doc", "text": "RAG stands for Retrieval-Augmented Generation."},
    )

    response = client.get("/search", params={"query": "RAG retrieval"})

    assert response.status_code == 200
    assert response.json()["query"] == "RAG retrieval"
    assert len(response.json()["results"]) >= 1


def test_search_query_too_short_rejected(client: TestClient) -> None:
    response = client.get("/search", params={"query": "x"})

    assert response.status_code == 422


def test_search_top_k_respected(client: TestClient) -> None:
    for index in range(5):
        client.post(
            "/documents",
            json={"source": f"doc-{index}", "text": f"Document number {index} about Python."},
        )

    response = client.get("/search", params={"query": "Python", "top_k": 2})

    assert response.status_code == 200
    assert len(response.json()["results"]) <= 2


def test_chat_returns_answer(client: TestClient) -> None:
    client.post(
        "/documents",
        json={"source": "chat-doc", "text": "Python is a high-level programming language."},
    )

    response = client.post("/chat", json={"question": "What is Python?"})

    assert response.status_code == 200
    assert response.json()["question"] == "What is Python?"
    assert response.json()["answer"]
    assert isinstance(response.json()["citations"], list)
    assert isinstance(response.json()["context"], list)


def test_chat_question_too_short_rejected(client: TestClient) -> None:
    response = client.post("/chat", json={"question": "x"})

    assert response.status_code == 422


def test_delete_source(client: TestClient) -> None:
    client.post(
        "/documents",
        json={"source": "to-delete", "text": "This document will be removed."},
    )

    response = client.delete("/documents/to-delete")

    assert response.status_code == 200
    assert response.json()["source"] == "to-delete"
    assert response.json()["chunks_deleted"] >= 1


def test_delete_nonexistent_source_returns_zero(client: TestClient) -> None:
    response = client.delete("/documents/does-not-exist")

    assert response.status_code == 200
    assert response.json()["chunks_deleted"] == 0
