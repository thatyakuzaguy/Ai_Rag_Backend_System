# AI RAG Backend System

[![CI](https://github.com/thatyakuzaguy/Ai_Rag_Backend_System/actions/workflows/ci.yml/badge.svg)](https://github.com/thatyakuzaguy/Ai_Rag_Backend_System/actions/workflows/ci.yml)

A full-stack Retrieval-Augmented Generation workspace built with FastAPI. Users can create an account, organize documents into collections, ingest knowledge, chat with collection-specific context, and review citations through a modern browser dashboard.

Live demo: [https://ai-rag-backend-system.onrender.com](https://ai-rag-backend-system.onrender.com)

## Recruiter Quick Demo

1. Open the live demo.
2. Click **Start guided demo**.
3. Ask the suggested question or try: `How does this project prevent SQL injection?`

The guided demo creates a temporary reviewer account, a sample collection, and a starter document so the chat is usable immediately.

## Why I Built This

This project was built to demonstrate the backend pieces behind a practical RAG workflow without depending on expensive infrastructure. It runs in a free local mode by default, but the provider layer can be switched to OpenAI for production-style responses.

The focus is on clean API design, service separation, testability, and deployment readiness.

## Highlights

- FastAPI application with interactive Swagger documentation
- Modern browser dashboard with authentication and workspace metrics
- User accounts with token-based authentication
- Collections for grouping documents and isolating retrieval context
- Persistent document records, chat sessions, chat messages, and feedback
- SQLite-backed vector store with cosine similarity search
- Local hashing embeddings for free demos
- Optional OpenAI embeddings and chat completions
- Chunking pipeline with overlap and source metadata
- Conversation history support for follow-up questions
- Startup seeding for default demo knowledge
- Docker support and Render-compatible deployment
- Pytest and Ruff checks through GitHub Actions

## Architecture

```text
User / Client
    |
    v
Dashboard + REST API
    |
    +-- Auth
    |      -> register / login
    |      -> bearer tokens
    |
    +-- Collections
    |      -> user-scoped workspaces
    |      -> document records
    |
    +-- Document ingestion
    |      -> chunk text
    |      -> create embeddings
    |      -> persist chunks
    |
    +-- Search
    |      -> embed query
    |      -> rank chunks by cosine similarity
    |
    +-- Collection chat
           -> retrieve context
           -> use recent session history
           -> generate grounded answer
           -> return citations
```

## Tech Stack

| Area | Technology |
| --- | --- |
| API | FastAPI |
| Runtime | Python 3.10+ |
| Storage | SQLite |
| Validation | Pydantic |
| AI Providers | Local hashing, optional OpenAI |
| Testing | Pytest |
| Linting | Ruff |
| Deployment | Docker, Render |

## API Overview

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Web demo interface |
| `GET` | `/health` | Service status and indexed chunk count |
| `POST` | `/auth/register` | Create a user account |
| `POST` | `/auth/login` | Sign in and receive a bearer token |
| `GET` | `/dashboard` | Authenticated workspace metrics |
| `POST` | `/collections` | Create a document collection |
| `GET` | `/collections` | List user collections |
| `POST` | `/collections/{id}/documents` | Ingest text into a collection |
| `GET` | `/collections/{id}/documents` | List collection documents |
| `POST` | `/collections/{id}/chat` | Chat with one collection |
| `GET` | `/collections/{id}/chats` | List chat sessions |
| `POST` | `/feedback` | Save answer feedback |
| `POST` | `/documents` | Ingest raw text with authentication |
| `POST` | `/documents/file` | Upload `.txt`, `.md`, or `.csv` files with authentication |
| `GET` | `/search` | Retrieve relevant chunks |
| `POST` | `/chat` | Ask a grounded question with citations |
| `DELETE` | `/documents/{source}` | Delete indexed chunks by source with authentication |

## Running Locally

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
uvicorn app.main:app --reload
```

Open:

- Web interface: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## Example Authenticated Flow

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

Ingest into the collection:

```bash
curl -X POST http://127.0.0.1:8000/collections/COLLECTION_ID/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source\":\"tuple-note\",\"text\":\"A Python tuple is immutable.\"}"
```

Chat with that collection:

```bash
curl -X POST http://127.0.0.1:8000/collections/COLLECTION_ID/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Is a tuple mutable?\",\"top_k\":3}"
```

## Legacy Search and Chat

The project keeps public search and chat endpoints for simple demos and backwards compatibility. Document ingestion and deletion require a bearer token.

Search indexed content:

```bash
curl "http://127.0.0.1:8000/search?query=relevant%20context&top_k=3"
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What does this system demonstrate?\",\"top_k\":3}"
```

Authenticated raw ingestion:

```bash
curl -X POST http://127.0.0.1:8000/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"source\":\"demo-note\",\"text\":\"RAG retrieves relevant context before generating an answer.\"}"
```

## Configuration

The default setup uses local providers so the app can run without paid API calls.

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

The Dockerfile uses Render's `PORT` environment variable when deployed and falls back to port `8000` locally.

## Tests

```bash
pytest
ruff check app tests
```

Current coverage focuses on:

- chunking behavior
- retrieval flow
- API endpoints
- authenticated collection chat flow
- chat history input
- local response extraction
- settings validation

## Project Structure

```text
app/
  api/          HTTP routes
  core/         settings and dependency wiring
  models/       Pydantic schemas
  services/     app store, chunking, embeddings, vector store, RAG, seeding
  web.py        dashboard UI
tests/          pytest suite
```

## Notes

SQLite works well for a portfolio demo and keeps deployment simple. For a larger production system, the vector store would be replaced with a dedicated database or vector search service, and background jobs would handle larger ingestion workloads.
