# src/config.py
"""
Env-var loading, fail-fast on anything required and missing — same
pattern as the reference project's src/config.py (project_bootstrap_brief.md
§3.1 note: pattern reused, not content — the actual variable names differ
since this app has no SECRET_KEY/session cookie to configure at all,
per the UUID-bearer, no-password auth model in brief §3.2).
"""

import os


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DATABASE_URL = _require_env("DATABASE_URL")
