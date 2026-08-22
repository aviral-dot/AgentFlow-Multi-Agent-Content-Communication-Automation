import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# LOG PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT / "logs"

LOG_FILE = LOG_DIR / "agentflow.jsonl"


# ============================================================
# JSON FORMATTER
# ============================================================

class JsonFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:

        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # ----------------------------------------------------
        # Event name
        # ----------------------------------------------------

        event = getattr(
            record,
            "event",
            None,
        )

        if event is not None:
            log_entry["event"] = event

        # ----------------------------------------------------
        # Structured context
        # ----------------------------------------------------

        context = getattr(
            record,
            "context",
            None,
        )

        if context:
            log_entry.update(context)

        # ----------------------------------------------------
        # Exception information
        # ----------------------------------------------------

        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info

            log_entry["exception"] = {
               "type": (
                   exc_type.__name__
                if exc_type is not None
                   else "UnknownError"
                ),
            "message": str(exc_value),
            "traceback": self.formatException(
                 record.exc_info
                ),
            }       

        return json.dumps(
            log_entry,
            default=str,
            ensure_ascii=False,
        )


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

def configure_logging() -> None:
    """Configure application-wide structured logging."""

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    root_logger = logging.getLogger()

    log_level = os.getenv(
        "LOG_LEVEL",
        "INFO",
    ).upper()

    root_logger.setLevel(log_level)

    # --------------------------------------------------------
    # Avoid duplicate handlers
    # --------------------------------------------------------

    existing_handler_names = {
        getattr(
            handler,
            "name",
            None,
        )
        for handler in root_logger.handlers
    }

    formatter = JsonFormatter()

    # --------------------------------------------------------
    # File handler
    # --------------------------------------------------------

    if "agentflow_file" not in existing_handler_names:

        file_handler = logging.FileHandler(
            LOG_FILE,
            encoding="utf-8",
        )

        file_handler.name = "agentflow_file"

        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        root_logger.addHandler(
            file_handler
        )

    # --------------------------------------------------------
    # Console handler
    # --------------------------------------------------------

    if "agentflow_console" not in existing_handler_names:

        console_handler = logging.StreamHandler(
            sys.stdout
        )

        console_handler.name = "agentflow_console"

        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        root_logger.addHandler(
            console_handler
        )


# ============================================================
# LOGGER FACTORY
# ============================================================

def get_logger(
    name: str,
) -> logging.Logger:
    """Return a configured application logger."""

    configure_logging()

    return logging.getLogger(name)


# ============================================================
# STRUCTURED EVENT LOGGER
# ============================================================

def log_event(
    logger: logging.Logger,
    *,
    level: int,
    event: str,
    **context: Any,
) -> None:
    """Write a structured application event."""

    logger.log(
        level,
        event,
        extra={
            "event": event,
            "context": context,
        },
    )