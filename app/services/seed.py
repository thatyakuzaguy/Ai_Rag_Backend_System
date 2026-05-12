from pathlib import Path

from app.services.rag import RAGService


PYTHON_BASICS = """
Python Basics Knowledge Pack

Python is a high-level, interpreted programming language known for readable syntax, fast development, and a large ecosystem of libraries. It is widely used for web development, automation, data science, artificial intelligence, scripting, backend APIs, testing, and DevOps.

Variables and Types
- Variables are names that reference values.
- Python is dynamically typed, so you do not need to declare a variable type before assigning a value.
- Common built-in types include int, float, str, bool, list, tuple, dict, set, and NoneType.
- Example: name = "Alice", age = 30, active = True.

Strings
- Strings store text and can be created with single quotes or double quotes.
- f-strings are used for readable interpolation, for example: f"Hello {name}".
- Common string methods include lower(), upper(), strip(), split(), replace(), and join().

Lists, Tuples, Dictionaries, and Sets
- A list is an ordered, mutable collection: numbers = [1, 2, 3].
- A tuple is an ordered, immutable collection: point = (10, 20).
- A dictionary stores key-value pairs: user = {"name": "Alice", "age": 30}.
- A set stores unique values: tags = {"python", "api", "backend"}.

Conditionals and Loops
- if, elif, and else are used for branching logic.
- Python uses indentation to define code blocks.
- for loops iterate over collections or ranges.
- while loops repeat while a condition is true.
- break exits a loop, and continue skips to the next iteration.

Functions
- Functions are reusable blocks of code defined with def.
- Parameters receive inputs, and return sends a value back to the caller.
- Example: def add(a, b): return a + b.

Modules and Imports
- A module is a Python file that can be imported.
- import math imports the full module.
- from pathlib import Path imports a specific object.
- Good projects organize code into packages and modules.

Error Handling
- try and except handle errors gracefully.
- finally runs cleanup code whether an error happened or not.
- raise is used to throw an exception.
- Common exceptions include ValueError, TypeError, KeyError, IndexError, and FileNotFoundError.

Files and SQLite
- Use pathlib.Path for modern file handling.
- with open(...) as file ensures files are closed properly.
- sqlite3 is Python's built-in SQLite library.
- SQLite connections should be closed after use.
- Parameterized SQL queries help prevent SQL injection.
- Context managers can commit or roll back transactions safely.

Classes and Objects
- Classes define reusable object blueprints.
- __init__ initializes object state.
- self refers to the current instance.

Virtual Environments and Packages
- A virtual environment isolates project dependencies.
- Create one with python -m venv .venv.
- Activate on Windows with .\\.venv\\Scripts\\activate.
- Install packages with pip install package-name.
- pyproject.toml or requirements.txt can describe dependencies.

Type Hints
- Type hints document expected types and help editors catch mistakes.
- Example: def greet(name: str) -> str: return f"Hello {name}".
- Type hints are optional at runtime but useful for maintainability.

Testing and FastAPI
- pytest is a popular testing framework.
- Test functions usually start with test_.
- assert checks expected behavior.
- FastAPI is a Python framework for building APIs.
- Pydantic models validate request and response data.
- Uvicorn runs FastAPI apps locally.

Common Beginner Mistakes
- Forgetting indentation after if, for, def, or class.
- Mixing tabs and spaces.
- Mutating a list while looping over it.
- Using mutable default arguments like def add_item(item, items=[]).
- Forgetting to activate the virtual environment.
- Forgetting to close files or database connections.
""".strip()


CONVERSATION_BASICS = """
Conversation Basics Knowledge Pack

The assistant should behave like a helpful portfolio chatbot for the AI RAG Backend System. It can answer questions about indexed documents, explain Python basics, describe the project, and hold a simple friendly conversation.

Conversation Style
- Be concise, friendly, and clear.
- If the user greets the assistant, greet them back and ask how you can help.
- If the user says thanks, respond politely.
- If the user asks what you can do, explain that you can answer questions using indexed documents, search context, explain Python basics, and describe this RAG project.
- If the user asks who you are, say you are a RAG demo assistant connected to this backend.
- If the user asks a follow-up question using words like it, that, this, or the previous thing, use the recent conversation history to understand the reference.
- If the answer is not in the indexed context, say that there is not enough indexed information yet and suggest ingesting a document.

Useful Example Replies
- Greeting: Hi. I can help you search indexed documents, answer RAG questions, or explain Python basics.
- Identity: I am the demo assistant for this AI RAG Backend System.
- Capability: I can ingest documents, retrieve relevant chunks, answer questions with citations, and explain the knowledge that has been indexed.
- Unknown answer: I do not have enough indexed context to answer that yet. Try ingesting a document with the information you want me to use.
""".strip()


ADVANCED_PYTHON_FASTAPI_SQL = """
Advanced Python, FastAPI, SQL, and Conversation Knowledge Pack

Advanced Conversation Behavior
- For technical questions, answer with a clear explanation, a practical example, and a short warning about common mistakes.
- For debugging questions, ask for the error message, stack trace, input data, and the smallest reproducible example when needed.
- For architecture questions, compare tradeoffs instead of pretending there is only one correct answer.
- For follow-up questions, use the previous chat context to resolve references such as "that function", "this endpoint", "the previous query", or "it".
- If the user asks for code, prefer small, runnable examples.
- If the user asks for security advice, mention input validation, authentication, authorization, logging, rate limiting, secrets management, and least privilege.
- If the indexed context is insufficient, say what is missing and suggest what document should be ingested.

Advanced Python
- Prefer simple, explicit code over clever code.
- Use pathlib.Path for filesystem paths instead of manual string joins.
- Use context managers for resources such as files, database connections, locks, and temporary directories.
- Avoid mutable default arguments such as def add_item(item, items=[]). Use None and create the list inside the function.
- Use dataclasses for lightweight data containers when behavior is minimal.
- Use Pydantic models when validating external input or API data.
- Use generators when streaming large data or avoiding memory-heavy lists.
- Use list comprehensions for simple transformations, but use normal loops when logic becomes complex.
- Use exceptions for exceptional cases, not normal control flow.
- Catch specific exceptions instead of broad except Exception unless you are translating errors at an application boundary.
- Type hints improve maintainability: def get_user(user_id: str) -> User | None.
- Dependency injection makes code easier to test because real services can be replaced with fakes.
- Good tests focus on behavior, edge cases, permissions, and regressions.

FastAPI Architecture
- FastAPI routes should stay thin: parse input, call services, return response models.
- Business logic belongs in service classes or functions, not directly inside route handlers.
- Pydantic request models validate incoming data and response models control what leaves the API.
- Use Depends for dependencies such as authenticated users, database stores, and service objects.
- Raise HTTPException for expected client errors such as 400, 401, 403, 404, and 409.
- Avoid leaking internal exception details to API clients.
- Use status codes intentionally: 201 for created resources, 401 for missing/invalid auth, 403 for forbidden access, 404 for missing resources, 409 for conflicts, 422 for validation errors.
- Use TestClient for integration tests against route behavior.
- For production APIs, add CORS intentionally, rate limiting, structured logging, request IDs, and health checks.
- File upload endpoints should validate file extension, content type, and size.
- Long-running ingestion should eventually move to a background worker or queue.

Authentication and Authorization
- Authentication answers "who are you?" Authorization answers "are you allowed to access this resource?"
- Bearer tokens should be random, high entropy, stored securely, and ideally expire.
- Passwords should never be stored in plain text. Use a password hashing algorithm with salt.
- Every user-scoped query should filter by user_id.
- Collection-scoped chat should verify both user ownership and collection ownership.
- Feedback should verify that the chat session belongs to the authenticated user.
- Public write endpoints can be abused for spam or data poisoning; require authentication for writes.

SQL and SQLite
- SQL injection happens when user input is concatenated into SQL strings.
- Use parameterized queries: conn.execute("SELECT * FROM users WHERE email = ?", (email,)).
- Never build SQL like f"SELECT * FROM users WHERE email = '{email}'".
- Use transactions so related writes succeed or fail together.
- Use indexes on columns used for filtering and joins, such as user_id, collection_id, and session_id.
- Use UNIQUE constraints for fields such as email when duplicates are invalid.
- Use foreign keys to model relationships between users, collections, documents, chat sessions, and messages.
- SQLite is good for demos and small apps. For production multi-user workloads, PostgreSQL is usually a better choice.
- For vector search at larger scale, use pgvector, Qdrant, Weaviate, Pinecone, or another vector database.
- Avoid SELECT * in large production systems when you only need a few columns.
- Store timestamps for auditing and sorting.
- Use migrations such as Alembic when schemas evolve in production.

SQL Query Examples
- Get a user by email safely: SELECT * FROM users WHERE email = ?.
- Count documents per collection with a join and group by.
- Delete by source safely: DELETE FROM chunks WHERE source = ?.
- Search by ownership safely by including WHERE user_id = ?.

RAG Architecture
- RAG means Retrieval-Augmented Generation.
- Ingestion usually includes loading documents, normalizing text, chunking, embedding chunks, and storing vectors with metadata.
- Retrieval embeds the user query and finds the most similar chunks.
- Generation uses retrieved chunks as context for the answer.
- Citations help users understand which sources supported an answer.
- Metadata filters are important for multi-tenant systems because they prevent one user's documents from appearing in another user's answers.
- Chunk size and overlap affect retrieval quality. Small chunks can miss context; large chunks can add noise.
- RAG systems should handle "not enough context" honestly instead of guessing.

Security Checklist for This Project
- Require authentication for write endpoints.
- Use parameterized SQL queries.
- Validate request sizes and field lengths.
- Do not expose real API keys in code, README files, logs, or frontend JavaScript.
- Do not return raw provider exceptions to users.
- Verify user ownership for collections, sessions, documents, and feedback.
- Add rate limiting before exposing login or ingestion endpoints at scale.
- Prefer PostgreSQL with migrations for production.
""".strip()


def seed_default_knowledge(rag: RAGService) -> int:
    chunks = rag.ingest_text(
        text=PYTHON_BASICS,
        source="python-basics",
        metadata={"topic": "python", "level": "beginner", "seeded": True},
    )
    chunks += rag.ingest_text(
        text=CONVERSATION_BASICS,
        source="conversation-basics",
        metadata={"topic": "conversation", "seeded": True},
    )
    chunks += rag.ingest_text(
        text=ADVANCED_PYTHON_FASTAPI_SQL,
        source="advanced-python-fastapi-sql",
        metadata={"topic": "python-fastapi-sql", "level": "advanced", "seeded": True},
    )

    readme = Path("README.md")
    if readme.exists():
        chunks += rag.ingest_text(
            text=readme.read_text(encoding="utf-8"),
            source="project-readme",
            metadata={"topic": "project", "seeded": True},
        )

    return chunks
