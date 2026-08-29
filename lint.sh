(cd ui && bunx prettier -w .)
(cd api && uv run black . && uv run ruff check --fix)
