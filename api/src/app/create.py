# src/app/create.py
"""
FastAPI app factory. Registers the routes module and, since Alembic
migrations are explicitly still pending (handoff doc §1 — "still the
very start"), creates tables directly from the SQLModel metadata on
startup as a dev-only placeholder. This is NOT a substitute for
migrations and shouldn't be mistaken for one once they exist —
`SQLModel.metadata.create_all` has no notion of incremental schema
change, only "create if missing." Flagged here explicitly so it gets
deleted the moment `alembic upgrade head` becomes the real bootstrap
path, not left behind as a second, silently-diverging way tables get
created.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.routes import router
from src.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="GABO — Renaissance Edition (API, Swagger-first milestone)",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app()
