from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from src.app.routes import router
from src.app.routes.ws import router as ws_router
from src.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Verdict",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4173", "http://localhost:5173"],  # UI dev/prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes at /api/*, WebSocket routes at /ws/*
    app.include_router(router)
    app.include_router(ws_router)
    return app


app = create_app()
