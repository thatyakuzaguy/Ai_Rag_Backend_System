from functools import lru_cache

from app.core.settings import Settings, get_settings
from app.services.chunker import TextChunker
from app.services.embeddings import EmbeddingProvider, build_embedding_provider
from app.services.llm import LLMProvider, build_llm_provider
from app.services.rag import RAGService
from app.services.vector_store import SQLiteVectorStore


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    return build_embedding_provider(get_settings())


@lru_cache
def get_llm_provider() -> LLMProvider:
    return build_llm_provider(get_settings())


@lru_cache
def get_vector_store() -> SQLiteVectorStore:
    return SQLiteVectorStore(get_settings().database_path)


@lru_cache
def get_chunker() -> TextChunker:
    settings: Settings = get_settings()
    return TextChunker(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)


def get_rag_service() -> RAGService:
    return RAGService(
        chunker=get_chunker(),
        embedder=get_embedding_provider(),
        store=get_vector_store(),
        llm=get_llm_provider(),
        default_top_k=get_settings().top_k,
    )
