from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.routes import router
from app.core.dependencies import get_rag_service
from app.core.settings import get_settings
from app.services.seed import seed_default_knowledge


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    if settings.auto_seed_knowledge and settings.embedding_provider == "local":
        seed_default_knowledge(get_rag_service())
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="A local-first Retrieval-Augmented Generation backend.",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app()
