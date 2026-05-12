from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.services.chunker import TextChunker
from app.services.embeddings import LocalHashingEmbeddingProvider
from app.services.llm import LocalExtractiveLLMProvider
from app.services.rag import RAGService
from app.services.app_store import AppStore
from app.services.vector_store import SQLiteVectorStore


def auth_headers(client: TestClient, email: str = "user@example.com") -> dict[str, str]:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "password123",
            "display_name": "Test User",
        },
    )
    return {"Authorization": f"Bearer {response.json()['token']}"}


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    from app.core.dependencies import (
        get_app_store,
        get_chunker,
        get_embedding_provider,
        get_llm_provider,
        get_rag_service,
        get_vector_store,
    )
    from app.main import app

    store = SQLiteVectorStore(tmp_path / "test.sqlite3")
    app_store = AppStore(tmp_path / "app.sqlite3")
    embedder = LocalHashingEmbeddingProvider(dimensions=128)
    chunker = TextChunker(chunk_size=250, chunk_overlap=40)
    llm = LocalExtractiveLLMProvider()
    rag = RAGService(chunker=chunker, embedder=embedder, store=store, llm=llm)

    app.dependency_overrides[get_vector_store] = lambda: store
    app.dependency_overrides[get_app_store] = lambda: app_store
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
    assert "KnowledgeBase AI" in response.text


def test_authenticated_collection_chat_flow(client: TestClient) -> None:
    auth = client.post(
        "/auth/register",
        json={
            "email": "demo@example.com",
            "password": "password123",
            "display_name": "Demo User",
        },
    )
    assert auth.status_code == 201
    token = auth.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    collection = client.post(
        "/collections",
        json={"name": "Python Notes", "description": "Learning notes"},
        headers=headers,
    )
    assert collection.status_code == 201
    collection_id = collection.json()["id"]

    document = client.post(
        f"/collections/{collection_id}/documents",
        json={"source": "tuple-note", "text": "A Python tuple is immutable."},
        headers=headers,
    )
    assert document.status_code == 201
    assert document.json()["chunks_indexed"] >= 1

    chat = client.post(
        f"/collections/{collection_id}/chat",
        json={"question": "Is a tuple mutable?", "top_k": 2},
        headers=headers,
    )
    assert chat.status_code == 200
    assert chat.json()["session_id"]
    assert chat.json()["citations"]


def test_login_token_can_access_dashboard(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "login-flow@example.com",
            "password": "password123",
            "display_name": "Login Flow",
        },
    )

    login = client.post(
        "/auth/login",
        json={"email": "login-flow@example.com", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['token']}"}
    dashboard = client.get("/dashboard", headers=headers)

    assert login.status_code == 200
    assert dashboard.status_code == 200


def test_invalid_bearer_token_is_rejected(client: TestClient) -> None:
    response = client.get("/dashboard", headers={"Authorization": "Bearer stale-token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid bearer token"


def test_collection_chat_rejects_session_from_other_collection(client: TestClient) -> None:
    auth = client.post(
        "/auth/register",
        json={
            "email": "security@example.com",
            "password": "password123",
            "display_name": "Security User",
        },
    )
    headers = {"Authorization": f"Bearer {auth.json()['token']}"}
    first = client.post("/collections", json={"name": "A"}, headers=headers).json()
    second = client.post("/collections", json={"name": "B"}, headers=headers).json()
    session = client.post(
        f"/collections/{first['id']}/chats",
        json={"title": "Private session"},
        headers=headers,
    ).json()

    response = client.post(
        f"/collections/{second['id']}/chat",
        json={"question": "Can I use this session?", "session_id": session["id"]},
        headers=headers,
    )

    assert response.status_code == 403


def test_feedback_rejects_other_users_session(client: TestClient) -> None:
    first_auth = client.post(
        "/auth/register",
        json={
            "email": "owner@example.com",
            "password": "password123",
            "display_name": "Owner",
        },
    )
    second_auth = client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
            "password": "password123",
            "display_name": "Other",
        },
    )
    first_headers = {"Authorization": f"Bearer {first_auth.json()['token']}"}
    second_headers = {"Authorization": f"Bearer {second_auth.json()['token']}"}
    collection = client.post("/collections", json={"name": "Private"}, headers=first_headers).json()
    session = client.post(
        f"/collections/{collection['id']}/chats",
        json={"title": "Owner chat"},
        headers=first_headers,
    ).json()

    response = client.post(
        "/feedback",
        json={"session_id": session["id"], "rating": 1},
        headers=second_headers,
    )

    assert response.status_code == 404


def test_health_after_ingest(client: TestClient) -> None:
    headers = auth_headers(client, "health@example.com")
    client.post("/documents", json={"source": "doc-a", "text": "Hello world from doc-a."}, headers=headers)
    client.post("/documents", json={"source": "doc-b", "text": "Another document here."}, headers=headers)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["documents"] == 2
    assert response.json()["chunks_indexed"] >= 2


def test_ingest_document_returns_201(client: TestClient) -> None:
    headers = auth_headers(client, "ingest@example.com")
    response = client.post(
        "/documents",
        json={"source": "test-source", "text": "FastAPI makes building APIs easy."},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["source"] == "test-source"
    assert response.json()["chunks_indexed"] >= 1


def test_ingest_document_empty_text_rejected(client: TestClient) -> None:
    headers = auth_headers(client, "empty@example.com")
    response = client.post("/documents", json={"source": "s", "text": ""}, headers=headers)

    assert response.status_code == 422


def test_ingest_file_txt(client: TestClient, tmp_path: Path) -> None:
    headers = auth_headers(client, "file@example.com")
    text_file = tmp_path / "sample.txt"
    text_file.write_text("This is a plain text file with content for RAG indexing.")

    with text_file.open("rb") as file:
        response = client.post(
            "/documents/file",
            files={"file": ("sample.txt", file, "text/plain")},
            headers=headers,
        )

    assert response.status_code == 201
    assert response.json()["source"] == "sample.txt"


def test_ingest_file_unsupported_extension_rejected(
    client: TestClient,
    tmp_path: Path,
) -> None:
    headers = auth_headers(client, "unsupported@example.com")
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake content")

    with pdf.open("rb") as file:
        response = client.post(
            "/documents/file",
            files={"file": ("report.pdf", file, "application/pdf")},
            headers=headers,
        )

    assert response.status_code == 400


def test_search_returns_results(client: TestClient) -> None:
    headers = auth_headers(client, "search@example.com")
    client.post(
        "/documents",
        json={"source": "rag-doc", "text": "RAG stands for Retrieval-Augmented Generation."},
        headers=headers,
    )

    response = client.get("/search", params={"query": "RAG retrieval"})

    assert response.status_code == 200
    assert response.json()["query"] == "RAG retrieval"
    assert len(response.json()["results"]) >= 1


def test_search_query_too_short_rejected(client: TestClient) -> None:
    response = client.get("/search", params={"query": "x"})

    assert response.status_code == 422


def test_search_top_k_respected(client: TestClient) -> None:
    headers = auth_headers(client, "topk@example.com")
    for index in range(5):
        client.post(
            "/documents",
            json={"source": f"doc-{index}", "text": f"Document number {index} about Python."},
            headers=headers,
        )

    response = client.get("/search", params={"query": "Python", "top_k": 2})

    assert response.status_code == 200
    assert len(response.json()["results"]) <= 2


def test_chat_returns_answer(client: TestClient) -> None:
    headers = auth_headers(client, "chat@example.com")
    client.post(
        "/documents",
        json={"source": "chat-doc", "text": "Python is a high-level programming language."},
        headers=headers,
    )

    response = client.post("/chat", json={"question": "What is Python?"})

    assert response.status_code == 200
    assert response.json()["question"] == "What is Python?"
    assert response.json()["answer"]
    assert isinstance(response.json()["citations"], list)
    assert isinstance(response.json()["context"], list)


def test_chat_accepts_conversation_history(client: TestClient) -> None:
    headers = auth_headers(client, "history@example.com")
    client.post(
        "/documents",
        json={"source": "history-doc", "text": "A tuple is immutable in Python."},
        headers=headers,
    )

    response = client.post(
        "/chat",
        json={
            "question": "Is it mutable?",
            "top_k": 2,
            "history": [
                {"role": "user", "content": "Tell me about Python tuples."},
                {"role": "assistant", "content": "Python tuples are ordered collections."},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["citations"]


def test_chat_question_too_short_rejected(client: TestClient) -> None:
    response = client.post("/chat", json={"question": "x"})

    assert response.status_code == 422


def test_delete_source(client: TestClient) -> None:
    headers = auth_headers(client, "delete@example.com")
    client.post(
        "/documents",
        json={"source": "to-delete", "text": "This document will be removed."},
        headers=headers,
    )

    response = client.delete("/documents/to-delete", headers=headers)

    assert response.status_code == 200
    assert response.json()["source"] == "to-delete"
    assert response.json()["chunks_deleted"] >= 1


def test_delete_nonexistent_source_returns_zero(client: TestClient) -> None:
    headers = auth_headers(client, "delete-missing@example.com")
    response = client.delete("/documents/does-not-exist", headers=headers)

    assert response.status_code == 200
    assert response.json()["chunks_deleted"] == 0


def test_delete_source_requires_auth(client: TestClient) -> None:
    response = client.delete("/documents/anything")

    assert response.status_code == 401


def test_ingest_document_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/documents",
        json={"source": "blocked", "text": "This should not be accepted."},
    )

    assert response.status_code == 401


def test_login_rejects_sql_injection_payload(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={
            "email": "sqli@example.com",
            "password": "password123",
            "display_name": "SQLi User",
        },
    )

    response = client.post(
        "/auth/login",
        json={"email": "' OR '1'='1@example.com", "password": "' OR '1'='1"},
    )

    assert response.status_code == 422


def test_collection_id_sql_injection_payload_is_not_executed(client: TestClient) -> None:
    headers = auth_headers(client, "collection-sqli@example.com")
    client.post("/collections", json={"name": "Safe Collection"}, headers=headers)

    response = client.get(
        "/collections/' OR '1'='1/documents",
        headers=headers,
    )

    assert response.status_code == 404
    collections = client.get("/collections", headers=headers)
    assert collections.status_code == 200
    assert len(collections.json()) == 1


def test_document_source_sql_injection_payload_is_stored_as_text(client: TestClient) -> None:
    headers = auth_headers(client, "document-sqli@example.com")
    collection = client.post("/collections", json={"name": "Safe Docs"}, headers=headers).json()
    payload = "note'); DROP TABLE users; --"

    response = client.post(
        f"/collections/{collection['id']}/documents",
        json={"source": payload, "text": "SQL injection strings should be treated as plain text."},
        headers=headers,
    )

    assert response.status_code == 201
    documents = client.get(f"/collections/{collection['id']}/documents", headers=headers)
    assert documents.status_code == 200
    assert documents.json()[0]["source"] == payload


def test_delete_source_sql_injection_payload_does_not_drop_data(client: TestClient) -> None:
    headers = auth_headers(client, "delete-sqli@example.com")
    client.post(
        "/documents",
        json={"source": "safe-source", "text": "Safe content."},
        headers=headers,
    )

    response = client.delete("/documents/safe-source' OR '1'='1", headers=headers)

    assert response.status_code == 200
    assert response.json()["chunks_deleted"] == 0
    health = client.get("/health")
    assert health.json()["chunks_indexed"] >= 1
