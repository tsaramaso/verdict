# src/db/session.py
"""
Engine creation + per-request session dependency. Mirrors the reference
project's src/db/init.py + src/db/session.py split conceptually, adapted
from Flask's `g`-per-request pattern to FastAPI's Depends()-per-request
pattern — same lifecycle idea (one session per request, closed after),
different mechanism.
"""

from collections.abc import Generator

from sqlmodel import Session, create_engine

from src.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
