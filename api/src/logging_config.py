# src/logging_config.py
"""
Structured logging setup with loguru.

Logs are:
- Console: human-readable (dev)
- JSON: machine-readable (prod/storage)
- File: persisted (debugging)
"""

import sys
import os
from pathlib import Path
from loguru import logger

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Remove default handler
logger.remove()

# Determine if running in production
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

# Console handler (different format for dev vs prod)
if IS_PRODUCTION:
    # Production: JSON format for structured logging
    logger.add(
        sys.stdout,
        format="{message}",  # Raw message is already JSON
        level="INFO",
        serialize=True,  # Output as JSON
    )
else:
    # Development: human-readable format with colors
    logger.add(
        sys.stdout,
        format="<level>{time:HH:mm:ss}</level> | <level>{level: <8}</level> |"
        " <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
        " - <level>{message}</level>",
        level="DEBUG",
        colorize=True,
    )

# File handler: persist all logs (JSON for parseability)
logger.add(
    LOGS_DIR / "verdict.log",
    format="{message}",
    level="DEBUG",
    serialize=True,
    rotation="100 MB",  # Rotate when file hits 100MB
    retention="30 days",  # Keep logs for 30 days
)

# Exception handler: log full tracebacks
logger.add(
    LOGS_DIR / "errors.log",
    format="{message}",
    level="ERROR",
    serialize=True,
    rotation="100 MB",
)


def get_logger(name: str):
    """Get a logger instance with a specific name."""
    return logger.bind(module=name)
