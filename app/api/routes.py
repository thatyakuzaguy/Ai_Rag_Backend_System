from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.core.dependencies import get_rag_service, get_vector_store
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    DeleteResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
    HealthResponse,
    SearchResponse,
)
from app.services.rag import RAGService
from app.services.vector_store import SQLiteVectorStore

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health(store: SQLiteVectorStore = Depends(get_vector_store)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        documents=store.count_sources(),
        chunks_indexed=store.count(),
    )


@router.post(
    "/documents",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_document(
    payload: DocumentIngestRequest,
    rag: RAGService = Depends(get_rag_service),
) -> DocumentIngestResponse:
    chunks = rag.ingest_text(payload.text, source=payload.source, metadata=payload.metadata)
    return DocumentIngestResponse(source=payload.source, chunks_indexed=chunks)


@router.post(
    "/documents/file",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_file(
    file: UploadFile = File(...),
    rag: RAGService = Depends(get_rag_service),
) -> DocumentIngestResponse:
    allowed_extensions = {".txt", ".md", ".csv"}
    filename = file.filename or "uploaded-file"
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt, .md, and .csv uploads are supported.",
        )

    raw = await file.read()
    text = raw.decode("utf-8", errors="replace")
    chunks = rag.ingest_text(text, source=filename, metadata={"filename": filename})
    return DocumentIngestResponse(source=filename, chunks_indexed=chunks)


@router.get("/search", response_model=SearchResponse)
def search(
    query: str = Query(..., min_length=2),
    top_k: int = Query(4, ge=1, le=20),
    rag: RAGService = Depends(get_rag_service),
) -> SearchResponse:
    results = rag.search(query=query, top_k=top_k)
    return SearchResponse(query=query, results=results)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, rag: RAGService = Depends(get_rag_service)) -> ChatResponse:
    return rag.answer(question=payload.question, top_k=payload.top_k)


@router.delete("/documents/{source}", response_model=DeleteResponse)
def delete_source(
    source: str,
    store: SQLiteVectorStore = Depends(get_vector_store),
) -> DeleteResponse:
    deleted = store.delete_by_source(source)
    return DeleteResponse(source=source, chunks_deleted=deleted)
