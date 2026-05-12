# AI RAG Backend System

[![CI](https://github.com/thatyakuzaguy/Ai_Rag_Backend_System/actions/workflows/ci.yml/badge.svg)](https://github.com/thatyakuzaguy/Ai_Rag_Backend_System/actions/workflows/ci.yml)

A deployed FastAPI backend for Retrieval-Augmented Generation workflows. It includes authentication, user-scoped collections, document ingestion, vector retrieval, cited answers, chat history, feedback storage, security checks, and a polished public showcase page for recruiters.

Live demo: [https://ai-rag-backend-system.onrender.com](https://ai-rag-backend-system.onrender.com)

API docs: [https://ai-rag-backend-system.onrender.com/docs](https://ai-rag-backend-system.onrender.com/docs)

## Recruiter Review

1. Open the live demo to see the project overview.
2. Open Swagger Docs to inspect and test the API contract.
3. Review the tests for auth, RAG behavior, SQL injection safety, and collection isolation.

This is a portfolio demo, so the homepage focuses on communicating the backend system clearly. The working API remains available through Swagger and the source code.

## What This Demonstrates

- FastAPI REST API design with Pydantic validation
- User registration, login, bearer tokens, and hashed credentials
- User-scoped collections to isolate private document context
- Text ingestion, chunking, embedding, and vector retrieval
- SQLite-backed persistence for users, collections, documents, chats, feedback, and vectors
- Local no-cost AI provider mode for demos
- Optional OpenAI provider mode for stronger generation
- Conversation-aware RAG endpoint with citations
- SQL injection regression tests and parameterized queries
- Docker and Render deployment readiness
- CI checks with Pytest and Ruff

## Architecture

```text
Client / Swagger / Showcase Page
    |
    v
FastAPI routes
    |
    +-- Auth service
    |      -> register, login, bearer token validation
    |
    +-- App store
    |      -> users, collections, documents, sessions, feedback
    |
    +-- RAG service
    |      -> chunk text, embed content, retrieve context, answer with citations
    |
    +-- Vector store
           -> SQLite chunks, metadata filters, cosine similarity search
```

## Main Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Public showcase page |
| `GET` | `/health` | Service status and indexed document count |
| `POST` | `/auth/register` | Create a user account |
| `POST` | `/auth/login` | Sign in and receive a bearer token |
| `GET` | `/dashboard` | Authenticated workspace metrics |
| `POST` | `/collections` | Create a document collection |
| `GET` | `/collections` | List user collections |
| `POST` | `/collections/{id}/documents` | Ingest text into a collection |
| `GET` | `/collections/{id}/documents` | List collection documents |
| `POST` | `/collections/{id}/chat` | Ask a collection-scoped RAG question |
| `GET` | `/collections/{id}/chats` | List chat sessions |
| `POST` | `/feedback` | Store answer feedback |
| `GET` | `/search` | Public semantic search over indexed chunks |
| `POST` | `/chat` | Public RAG answer endpoint |

Write endpoints require authentication unless marked public.

## Tech Stack

| Area | Technology |
| --- | --- |
| API | FastAPI |
| Runtime | Python 3.10+ |
| Validation | Pydantic |
| Storage | SQLite |
| Retrieval | Local hashing embeddings + cosine similarity |
| Optional AI | OpenAI embeddings and chat completions |
| Testing | Pytest |
| Linting | Ruff |
| Deployment | Docker, Render |

## Run Locally

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
uvicorn app.main:app --reload
```

Open:

- Showcase: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## Example API Flow

Register:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"demo@example.com\",\"password\":\"password123\",\"display_name\":\"Demo User\"}"
```

Create a collection:

```bash
curl -X POST http://127.0.0.1:8000/collections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Python Notes\",\"description\":\"Learning notes\"}"
```

Ingest text:

```bash
curl -X POST http://127.0.0.1:8000/collections/COLLECTION_ID/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source\":\"tuple-note\",\"text\":\"A Python tuple is immutable.\"}"
```

Ask a collection-scoped question:

```bash
curl -X POST http://127.0.0.1:8000/collections/COLLECTION_ID/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Is a tuple mutable?\",\"top_k\":3}"
```

## Configuration

The default configuration uses local providers, so the demo can run without paid API calls.

```env
EMBEDDING_PROVIDER=local
LLM_PROVIDER=local
DATABASE_PATH=data/rag.sqlite3
AUTO_SEED_KNOWLEDGE=true
```

Optional OpenAI mode:

```env
EMBEDDING_PROVIDER=openai
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini
```

Never commit a real API key. The `.env` file is ignored by Git.

## Docker

```bash
copy .env.example .env
docker compose up --build
```

The Dockerfile uses Render's `PORT` environment variable in production and falls back to port `8000` locally.

## Tests

```bash
pytest
ruff check
```

Test coverage includes:

- API health and validation
- authentication and bearer token access
- authenticated collection chat flow
- collection ownership isolation
- SQL injection regression cases
- RAG retrieval and local answer extraction
- chat history handling
- settings validation

## Project Structure

```text
app/
  api/          FastAPI route modules
  core/         settings and dependency wiring
  models/       Pydantic request and response schemas
  services/     auth store, chunking, embeddings, vector search, RAG, seeding
  web.py        public showcase homepage
tests/          pytest suite
```

## Production Notes

SQLite keeps this demo simple and deployable on free infrastructure. For a production version, I would move vectors to a dedicated vector database, run ingestion in background jobs, add refresh tokens, rate limiting, observability, and stronger model evaluation.
