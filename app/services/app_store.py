import hashlib
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class AppStore:
    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def create_user(self, email: str, password: str, display_name: str) -> dict[str, Any]:
        user_id = secrets.token_hex(12)
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO users (id, email, password_hash, display_name)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, email.lower(), self._hash_password(password), display_name),
            )
        return self.get_user_by_id(user_id)

    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        user = self.get_user_by_email(email)
        if not user or not self._verify_password(password, user["password_hash"]):
            return None
        token = secrets.token_urlsafe(32)
        with self._connection() as conn:
            conn.execute("INSERT INTO api_tokens (token, user_id) VALUES (?, ?)", (token, user["id"]))
        public_user = self._public_user(user)
        public_user["token"] = token
        return public_user

    def get_user_by_token(self, token: str) -> dict[str, Any] | None:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT users.* FROM users
                JOIN api_tokens ON api_tokens.user_id = users.id
                WHERE api_tokens.token = ?
                """,
                (token,),
            ).fetchone()
        return self._public_user(dict(row)) if row else None

    def get_user_by_id(self, user_id: str) -> dict[str, Any]:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            raise KeyError("User not found")
        return self._public_user(dict(row))

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
        return dict(row) if row else None

    def create_collection(self, user_id: str, name: str, description: str = "") -> dict[str, Any]:
        collection_id = secrets.token_hex(12)
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO collections (id, user_id, name, description)
                VALUES (?, ?, ?, ?)
                """,
                (collection_id, user_id, name, description),
            )
        return self.get_collection(user_id, collection_id)

    def list_collections(self, user_id: str) -> list[dict[str, Any]]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT collections.*,
                       COUNT(DISTINCT documents.id) AS document_count,
                       COUNT(DISTINCT chat_sessions.id) AS chat_count
                FROM collections
                LEFT JOIN documents ON documents.collection_id = collections.id
                LEFT JOIN chat_sessions ON chat_sessions.collection_id = collections.id
                WHERE collections.user_id = ?
                GROUP BY collections.id
                ORDER BY collections.created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_collection(self, user_id: str, collection_id: str) -> dict[str, Any]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM collections WHERE id = ? AND user_id = ?",
                (collection_id, user_id),
            ).fetchone()
        if row is None:
            raise KeyError("Collection not found")
        return dict(row)

    def create_document(
        self,
        user_id: str,
        collection_id: str,
        source: str,
        chunks_indexed: int,
    ) -> dict[str, Any]:
        document_id = secrets.token_hex(12)
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO documents (id, user_id, collection_id, source, chunks_indexed)
                VALUES (?, ?, ?, ?, ?)
                """,
                (document_id, user_id, collection_id, source, chunks_indexed),
            )
        return self.get_document(user_id, document_id)

    def list_documents(self, user_id: str, collection_id: str) -> list[dict[str, Any]]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM documents
                WHERE user_id = ? AND collection_id = ?
                ORDER BY created_at DESC
                """,
                (user_id, collection_id),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_document(self, user_id: str, document_id: str) -> dict[str, Any]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE id = ? AND user_id = ?",
                (document_id, user_id),
            ).fetchone()
        if row is None:
            raise KeyError("Document not found")
        return dict(row)

    def create_chat_session(
        self,
        user_id: str,
        collection_id: str,
        title: str,
    ) -> dict[str, Any]:
        session_id = secrets.token_hex(12)
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_sessions (id, user_id, collection_id, title)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, user_id, collection_id, title),
            )
        return self.get_chat_session(user_id, session_id)

    def get_chat_session(self, user_id: str, session_id: str) -> dict[str, Any]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM chat_sessions WHERE id = ? AND user_id = ?",
                (session_id, user_id),
            ).fetchone()
        if row is None:
            raise KeyError("Chat session not found")
        return dict(row)

    def list_chat_sessions(self, user_id: str, collection_id: str) -> list[dict[str, Any]]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM chat_sessions
                WHERE user_id = ? AND collection_id = ?
                ORDER BY updated_at DESC
                """,
                (user_id, collection_id),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_chat_message(self, session_id: str, role: str, content: str) -> dict[str, Any]:
        message_id = secrets.token_hex(12)
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages (id, session_id, role, content)
                VALUES (?, ?, ?, ?)
                """,
                (message_id, session_id, role, content),
            )
            conn.execute(
                "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,),
            )
        return {"id": message_id, "session_id": session_id, "role": role, "content": content}

    def list_chat_messages(self, session_id: str, limit: int = 10) -> list[dict[str, Any]]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM (
                    SELECT * FROM chat_messages
                    WHERE session_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                )
                ORDER BY created_at ASC
                """,
                (session_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_feedback(
        self,
        user_id: str,
        session_id: str,
        rating: int,
        comment: str = "",
    ) -> dict[str, Any]:
        feedback_id = secrets.token_hex(12)
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO feedback (id, user_id, session_id, rating, comment)
                VALUES (?, ?, ?, ?, ?)
                """,
                (feedback_id, user_id, session_id, rating, comment),
            )
        return {"id": feedback_id, "rating": rating, "comment": comment}

    def dashboard_metrics(self, user_id: str) -> dict[str, int]:
        with self._connection() as conn:
            collections = conn.execute(
                "SELECT COUNT(*) AS total FROM collections WHERE user_id = ?",
                (user_id,),
            ).fetchone()["total"]
            documents = conn.execute(
                "SELECT COUNT(*) AS total FROM documents WHERE user_id = ?",
                (user_id,),
            ).fetchone()["total"]
            chats = conn.execute(
                "SELECT COUNT(*) AS total FROM chat_sessions WHERE user_id = ?",
                (user_id,),
            ).fetchone()["total"]
            messages = conn.execute(
                """
                SELECT COUNT(*) AS total FROM chat_messages
                JOIN chat_sessions ON chat_sessions.id = chat_messages.session_id
                WHERE chat_sessions.user_id = ?
                """,
                (user_id,),
            ).fetchone()["total"]
        return {
            "collections": int(collections),
            "documents": int(documents),
            "chats": int(chats),
            "messages": int(messages),
        }

    def _initialize(self) -> None:
        with self._connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS api_tokens (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS collections (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    collection_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    chunks_indexed INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(collection_id) REFERENCES collections(id)
                );

                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    collection_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(collection_id) REFERENCES collections(id)
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
                );

                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    rating INTEGER NOT NULL CHECK(rating IN (-1, 1)),
                    comment TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(session_id) REFERENCES chat_sessions(id)
                );

                CREATE INDEX IF NOT EXISTS idx_collections_user ON collections(user_id);
                CREATE INDEX IF NOT EXISTS idx_documents_collection ON documents(collection_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_collection ON chat_sessions(collection_id);
                CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id);
                """
            )

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            120_000,
        ).hex()
        return f"{salt}${password_hash}"

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        salt, expected_hash = stored_hash.split("$", 1)
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            120_000,
        ).hex()
        return secrets.compare_digest(actual_hash, expected_hash)

    @staticmethod
    def _public_user(user: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": user["id"],
            "email": user["email"],
            "display_name": user["display_name"],
            "created_at": user["created_at"],
        }
