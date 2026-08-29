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

# Get log level from env or defaults
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if IS_PRODUCTION else "DEBUG").upper()

# Module-level filters: suppress noisy modules during development
# Format: module_name -> log level (None = inherit from global)
MODULE_LEVELS = {
    "websocket": "INFO",  # Only log connections, disconnects, errors (not pong/ping)
}


def should_log(record):
    """Filter function to suppress noisy debug logs by module."""
    module = record.get("module")

    if module in MODULE_LEVELS:
        module_level = MODULE_LEVELS[module]
        # Parse level string to number (DEBUG=10, INFO=20, etc.)
        level_map = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50,
        }
        record_level = level_map.get(record["level"].name, 20)
        module_threshold = level_map.get(module_level, 20)

        if record_level < module_threshold:
            return False

    return True


# Console handler (different format for dev vs prod)
if IS_PRODUCTION:
    # Production: JSON format for structured logging
    logger.add(
        sys.stdout,
        format="{message}",  # Raw message is already JSON
        level=LOG_LEVEL,
        serialize=True,  # Output as JSON
        filter=should_log,
    )
else:
    # Development: human-readable format with colors
    logger.add(
        sys.stdout,
        format="<level>{time:HH:mm:ss}</level> | <level>{level: <8}</level> |"
        " <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
        " - <level>{message}</level>",
        level=LOG_LEVEL,
        colorize=True,
        filter=should_log,
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
