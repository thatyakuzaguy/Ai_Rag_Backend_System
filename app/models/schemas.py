from typing import Any

from pydantic import BaseModel, Field


class DocumentIngestRequest(BaseModel):
    source: str = Field(..., min_length=1, examples=["portfolio-readme"])
    text: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentIngestResponse(BaseModel):
    source: str
    chunks_indexed: int


class RetrievedChunk(BaseModel):
    id: str
    source: str
    text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2)
    top_k: int = Field(default=4, ge=1, le=20)
    history: list[ChatMessage] = Field(default_factory=list, max_length=10)


class Citation(BaseModel):
    source: str
    chunk_id: str
    score: float


class ChatResponse(BaseModel):
    question: str
    answer: str
    citations: list[Citation]
    context: list[RetrievedChunk]


class DeleteResponse(BaseModel):
    source: str
    chunks_deleted: int


class HealthResponse(BaseModel):
    status: str
    documents: int
    chunks_indexed: int
