# Dockerfile
#
# Local-only, testable — no VPS/SSH/GHCR assumptions baked in anywhere
# here (that's a separate, later concern — brief §3.5/§3.6, not this
# file). Structure matches the reference project's real Dockerfile
# (cache-mounted uv sync, non-root fixed UID/GID, explicit ENTRYPOINT
# reset) — adapted in exactly two places, both because the stack itself
# changed, not because the pattern did:
#   1. Flask/WSGI's `src.wsgi:APP` -> FastAPI/ASGI's `src.app.create:app`,
#      which means gunicorn needs `--worker-class uvicorn.workers.UvicornWorker`
#      to actually serve it (gunicorn alone only speaks WSGI).
#   2. No `/app/data` dir / bind-mounted sqlite file — this app has no
#      local file-backed state at all; Postgres is a separate compose
#      service, not a mounted volume on this container.

FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Install the project into `/app`
WORKDIR /app

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

RUN chown -R nonroot:nonroot /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Use the non-root user to run our application
USER nonroot

EXPOSE 8000

# src.app.create:app -- the FastAPI ASGI app object, built once at
# import time (create.py — see that file's own docstring re: the
# create_all()-on-lifespan dev-only migration stand-in). --worker-class
# is the one real addition vs. the reference's WSGI CMD — gunicorn needs
# to be told this is an ASGI app.
CMD ["uv", "run", "gunicorn", "src.app.create:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "30"]