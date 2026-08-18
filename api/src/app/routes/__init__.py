# src/app/routes/__init__.py
"""
Assembles the top-level router from the three sub-modules.
create.py imports `router` from here — same line, same name as before.

Sub-module layout:
  games.py     — game lifecycle (create, list, status, events)
  gameplay.py  — in-game actions (draw, action, power, trial, ...)
  users.py     — user management (create, list, me, soft-delete)
  _shared.py   — _call / _persist / _result helpers (not routes)
"""

from fastapi import APIRouter

from src.app.routes.gameplay import router as gameplay_router
from src.app.routes.games import router as games_router
from src.app.routes.users import router as users_router
from src.app.routes.ws import router as ws_router
from src.app.routes.lobbies import router as lobbies_router

router = APIRouter()
router.include_router(games_router)
router.include_router(gameplay_router)
router.include_router(users_router)
router.include_router(ws_router)
router.include_router(lobbies_router)