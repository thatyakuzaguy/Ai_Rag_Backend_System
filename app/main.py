from fastapi import FastAPI

from app.api.routes import router
from app.core.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="A local-first Retrieval-Augmented Generation backend.",
    )
    app.include_router(router)
    return app


app = create_app()
