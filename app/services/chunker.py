import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    text: str
    index: int


class TextChunker:
    def __init__(self, chunk_size: int = 900, chunk_overlap: int = 150) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[TextChunk]:
        normalized = self._normalize(text)
        if not normalized:
            return []

        chunks: list[TextChunk] = []
        start = 0
        while start < len(normalized):
            end = min(start + self.chunk_size, len(normalized))
            if end < len(normalized):
                boundary = self._best_boundary(normalized, start, end)
                if boundary > start:
                    end = boundary

            chunk_text = normalized[start:end].strip()
            if chunk_text:
                chunks.append(TextChunk(text=chunk_text, index=len(chunks)))

            if end >= len(normalized):
                break
            start = max(0, end - self.chunk_overlap)

        return chunks

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def _best_boundary(text: str, start: int, end: int) -> int:
        window = text[start:end]
        for separator in ("\n\n", "\n", ". ", "? ", "! ", "; ", ", "):
            pos = window.rfind(separator)
            if pos > len(window) * 0.5:
                return start + pos + len(separator)
        return end
