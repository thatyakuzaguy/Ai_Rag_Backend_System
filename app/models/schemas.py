from typing import Any

from pydantic import BaseModel, Field


class DocumentIngestRequest(BaseModel):
    source: str = Field(..., min_length=1, max_length=160, examples=["portfolio-readme"])
    text: str = Field(..., min_length=1, max_length=50_000)
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
    content: str = Field(..., min_length=1, max_length=4_000)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2_000)
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


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=80)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    created_at: str


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


class CollectionCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)


class CollectionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    created_at: str
    document_count: int = 0
    chat_count: int = 0


class CollectionDocumentRequest(BaseModel):
    source: str = Field(..., min_length=1, max_length=160)
    text: str = Field(..., min_length=1, max_length=50_000)


class DocumentRecordResponse(BaseModel):
    id: str
    user_id: str
    collection_id: str
    source: str
    chunks_indexed: int
    created_at: str


class ChatSessionCreateRequest(BaseModel):
    title: str = Field(default="New chat", min_length=1, max_length=120)


class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    collection_id: str
    title: str
    created_at: str
    updated_at: str


class CollectionChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2_000)
    session_id: str | None = None
    top_k: int = Field(default=4, ge=1, le=20)


class CollectionChatResponse(ChatResponse):
    session_id: str


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int = Field(..., ge=-1, le=1)
    comment: str = Field(default="", max_length=1_000)


class FeedbackResponse(BaseModel):
    id: str
    rating: int
    comment: str


class DashboardMetrics(BaseModel):
    collections: int
    documents: int
    chats: int
    messages: int
