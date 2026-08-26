# src/app/routes/users.py
"""
User management routes. Users are the only entity managed directly via
the API rather than through the CLI (cli/run.py) — the CLI path stays
for local dev convenience, but the API routes are what the real client
will use.

  POST   /users          create a user, returns their uuid (which IS
                         their bearer credential — store it, it's the
                         only time it's handed back in the response body)
  GET    /users          list all active users (admin-flavoured; no
                         per-caller scoping — any valid user can see the
                         full list, since the game creation flow needs to
                         let a creator pick from real user UUIDs)
  GET    /users/me       the caller's own profile (convenience endpoint —
                         useful for validating a stored credential)
  DELETE /users/{uuid}   soft-delete: sets is_active=False, does NOT
                         remove the row (games the user participated in
                         must remain queryable; their UUID is a FK in
                         GamePlayer and the source of truth for all
                         persisted events)

Auth:
  POST /users       — unauthenticated (bootstrapping: the first user
                      must be creatable without a credential)
  GET  /users       — get_current_user (any valid user)
  GET  /users/me    — get_current_user
  DELETE /users/:id — get_current_user; only the user themselves may
                      soft-delete their own account (no admin escalation
                      path yet — flagged, not an oversight)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from src.config import ACCESS_TOKEN_EXPIRE_DAYS, ALGORITHM, HASH_SECRET_KEY
from src.app.auth import get_current_user
from src.app.auth import create_access_token
from src.app.models.db import User
from src.db.session import get_session

router = APIRouter(prefix="/api/users", tags=["users"])

# ------------------------------------------------------------------
# Request / response schemas (users-only, kept local — not in
# schemas.py, which is scoped to game/event shapes)
# ------------------------------------------------------------------


class TokenData(BaseModel):
    uuid: str


class UserCreateRequest(BaseModel):
    name: str | None = None


class UserOut(BaseModel):
    uuid: str
    name: str | None
    is_active: bool
    created_at: str

    @classmethod
    def from_row(cls, user: User) -> UserOut:
        return cls(
            uuid=user.uuid,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )


class UserCreateOut(UserOut):
    """
    Returned ONLY on POST /users. Identical shape to UserOut — separated
    as a distinct class so the Swagger doc can call out that uuid is the
    bearer credential and is only surfaced here.
    """


class UserListOut(BaseModel):
    users: list[UserOut]


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------


class LoginRequest(BaseModel):
    uuid: str


class LoginResponse(BaseModel):
    token: str
    uuid: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, session: Session = Depends(get_session)):
    """Login with UUID, receive JWT token."""

    user = session.exec(select(User).where(User.uuid == request.uuid)).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=401, detail="Unknown code. Check and try again."
        )

    token = create_access_token(
        user.uuid, ACCESS_TOKEN_EXPIRE_DAYS, HASH_SECRET_KEY, ALGORITHM
    )
    return LoginResponse(token=token, uuid=user.uuid)


@router.post("", response_model=UserCreateOut, status_code=status.HTTP_201_CREATED)
def create_user(
    request: UserCreateRequest,
    session: Session = Depends(get_session),
) -> UserCreateOut:
    """
    No auth required — bootstrapping. The uuid in the response is the
    caller's bearer credential for every subsequent request; it is not
    stored or recoverable after this response is closed. Treat it like
    an API key.
    """
    user = User(name=request.name)
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserCreateOut.from_row(user)


@router.get("", response_model=UserListOut)
def list_users(
    session: Session = Depends(get_session),
) -> UserListOut:
    """
    Returns all active users. Any valid user can call this — the game
    creation flow needs callers to be able to find real UUIDs to seat.
    Inactive (soft-deleted) users are excluded: they can no longer auth
    and cannot be seated in new games.
    """
    rows = session.exec(
        select(User).where(User.is_active).order_by(User.created_at)
    ).all()
    return UserListOut(users=[UserOut.from_row(u) for u in rows])


@router.get("/me", response_model=UserOut)
def get_me(
    user: User = Depends(get_current_user),
) -> UserOut:
    """Validate a stored credential and return the caller's own profile."""
    return UserOut.from_row(user)


@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    uuid: str,
    caller: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """
    Soft-delete: sets is_active=False. The row is never removed — UUIDs
    are FKs in GamePlayer and are embedded in every persisted Event row;
    deleting the User row would corrupt the event log.

    Only the user themselves may deactivate their own account. A future
    admin escalation path would go here — flagged, not implemented yet.
    """
    if uuid != caller.uuid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may only deactivate your own account",
        )
    target = session.get(User, uuid)
    if target is None or not target.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    target.is_active = False
    session.add(target)
    session.commit()
