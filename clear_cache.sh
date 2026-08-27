find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
rm -rf api/.venv
rm -rf api/.ruff_cache
