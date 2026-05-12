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

    readme = Path("README.md")
    if readme.exists():
        chunks += rag.ingest_text(
            text=readme.read_text(encoding="utf-8"),
            source="project-readme",
            metadata={"topic": "project", "seeded": True},
        )

    return chunks
