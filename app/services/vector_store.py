import json
import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from app.models.schemas import RetrievedChunk


class SQLiteVectorStore:
    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def add_chunks(self, rows: list[dict[str, Any]]) -> int:
        if not rows:
            return 0

        with self._connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO chunks
                (id, source, chunk_index, text, embedding, metadata)
                VALUES (:id, :source, :chunk_index, :text, :embedding, :metadata)
                """,
                [
                    {
                        **row,
                        "embedding": json.dumps(row["embedding"]),
                        "metadata": json.dumps(row.get("metadata", {})),
                    }
                    for row in rows
                ],
            )
        return len(rows)

    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        with self._connection() as conn:
            records = conn.execute(
                "SELECT id, source, text, embedding, metadata FROM chunks"
            ).fetchall()

        scored: list[RetrievedChunk] = []
        for record in records:
            embedding = json.loads(record["embedding"])
            score = self._cosine_similarity(query_embedding, embedding)
            scored.append(
                RetrievedChunk(
                    id=record["id"],
                    source=record["source"],
                    text=record["text"],
                    score=score,
                    metadata=json.loads(record["metadata"] or "{}"),
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def delete_by_source(self, source: str) -> int:
        with self._connection() as conn:
            cursor = conn.execute("DELETE FROM chunks WHERE source = ?", (source,))
            return cursor.rowcount

    def count(self) -> int:
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS total FROM chunks").fetchone()
            return int(row["total"])

    def count_sources(self) -> int:
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(DISTINCT source) AS total FROM chunks").fetchone()
            return int(row["total"])

    def _initialize(self) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source)")

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)
