"""
prizepicks_ev_bot/logging_config.py

Configures structured logging for the entire application.
Call setup_logging() once at the entry point.

Usage:
    from prizepicks_ev_bot.logging_config import setup_logging, get_logger
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Pipeline started")
"""

from __future__ import annotations

import logging
import sys
from typing import Any


def setup_logging(level: str = "INFO", fmt: str = "text") -> None:
    """
    Configure root logger. Call once at startup.
    fmt="text" for development, "json" for production.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    if fmt == "json":
        import json

        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_data: dict[str, Any] = {
                    "time": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Pass __name__ from each module."""
    return logging.getLogger(name)
