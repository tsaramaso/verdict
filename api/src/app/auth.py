# src/app/auth.py
"""
UUID-as-bearer-credential auth (project_bootstrap_brief.md §3.2) — the
UUID itself IS the credential, no password, sent as a standard
Authorization: Bearer <uuid> header. In Swagger, this shows up as the
padlock icon + "Authorize" button (HTTPBearer is a recognized OpenAPI
security scheme) — paste a user's uuid in once, every route in the
"Try it out" panel carries it automatically after that.

Deliberately NOT a decorator (see chat: FastAPI's idiomatic equivalent
to Flask's @login_required is Depends(), not a decorator wrapping the
route function — a decorator here would be invisible to OpenAPI, so
Swagger would never show the auth requirement or the Authorize button
at all, which defeats the actual point of building this test-via-Swagger
first).

Two layers, because "is this a valid, active user" and "is this user
allowed to act in THIS specific game" are genuinely different checks:

  get_current_user   — authentication only. Valid bearer uuid, and
                        is_active (soft-delete, brief §3.2). Used
                        directly by any route that just needs to know
                        who's asking (e.g. GET /games — list games this
                        user is part of).

  get_current_player  — authorization for one game. Built ON TOP of
                        get_current_user via FastAPI's sub-dependency
                        resolution (it takes `user` as a Depends()
                        parameter itself, so get_current_user only ever
                        runs once per request either way). Confirms the
                        user is actually seated in `game_id` in that
                        route's URL path, then returns just the player_id
                        string — ready to hand straight to an engine
                        function's `player_id` parameter, no further
                        unwrapping needed at the call site.

DECIDED (not an accident): every route depends on get_current_player,
which runs before game_registry.py's own 404 check ever gets a chance
to fire — so a genuinely nonexistent game_id returns 403 here, same as
a real game you're just not seated in. This was flagged as an open
question and resolved deliberately: reordering so 404 could "win"
would mean an unauthorized caller could distinguish "doesn't exist"
from "exists, you're just not in it" — strictly more information
leaked to someone with no business asking, not less. game_registry.py's
404 path is intentionally unreachable from any route that also depends
on get_current_player (currently: every route).

Every action route (draw, take_action, testify, ...) depends on
get_current_player, never on get_current_user directly — a valid user
who isn't seated in this game must never reach the engine at all.
"""

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from src.app.models.db import GamePlayer, User
from src.db.session import get_session

bearer_scheme = HTTPBearer(
    description="Paste a user's uuid (from `python -m src.cli.run add ...`)"
    " as the token."
)


class TokenData(BaseModel):
    uuid: str


def create_access_token(
    uuid: str, access_token_expire_days: int, secret_key: str, algorithm: str
) -> str:
    """Create a JWT token for a user UUID."""
    to_encode: dict[str, str | datetime] = {"uuid": uuid}
    expire = datetime.now(timezone.utc) + timedelta(days=access_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_token(token: str, secret_key: str, algorithm: str) -> str | None:
    """Verify JWT token and return UUID if valid."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        if (uuid := payload.get("uuid")) is None:
            return None
        return uuid
    except JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    from src.config import HASH_SECRET_KEY, ALGORITHM

    # Verify JWT token and extract UUID
    uuid = verify_token(credentials.credentials, HASH_SECRET_KEY, ALGORITHM)

    if uuid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Look up user by UUID
    user = session.get(User, uuid)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_player(
    game_id: str = Path(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> str:
    """
    Returns the authenticated user's player_id, but only if they're
    actually seated in `game_id`. This is authorization, not just
    authentication — a real, valid, active user who happens not to be
    in this particular game is a 403, not a 401 (they proved who they
    are; they just aren't allowed to act here).
    """
    is_seated = session.exec(
        select(GamePlayer.id).where(
            GamePlayer.game_id == game_id, GamePlayer.user_uuid == user.uuid
        )
    ).first()
    if is_seated is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a player in this game",
        )
    return user.uuid
