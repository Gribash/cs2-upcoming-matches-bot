from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.health import router as health_router
from api.routers.matches import router as matches_router
from api.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="CS2 Matches API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, prefix="/api")
    app.include_router(matches_router, prefix="/api")

    return app


app = create_app()


