"""Centralized logging utilities."""

import logging
import logging.handlers
import os
import sys
from contextvars import ContextVar
from pathlib import Path
from typing import Any

_transaction_id: ContextVar[str] = ContextVar("transaction_id", default="")


def get_log_root() -> str:
    """Get the log root directory path."""
    if "LOG_ROOT" in os.environ:
        return os.environ["LOG_ROOT"]
    repo_root = Path(__file__).parent.parent.parent
    return str(repo_root / "logs")


LOG_ROOT = get_log_root()
LOG_DIR = Path(LOG_ROOT)
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_MAX_BYTES = 1 * 1024 * 1024
LOG_BACKUP_COUNT = 10


def _create_rotating_file_handler(
    filename: str,
) -> logging.handlers.RotatingFileHandler:
    """Create a rotating file handler with standard rotation settings."""
    return logging.handlers.RotatingFileHandler(
        filename=filename,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )


def get_logger(
    name: str, add_file_handler: bool = False, log_filename: str | None = None
) -> logging.Logger:
    """Get a logger instance with readable text formatting."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = ReadableFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if add_file_handler:
            filename = log_filename or f"{name}.log"
            file_handler = _create_rotating_file_handler(str(LOG_DIR / filename))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.setLevel(logging.INFO)

    return logger


def get_file_logger(
    name: str, log_filename: str | None = None, force_reconfigure: bool = False
) -> logging.Logger:
    """Get a logger instance that writes only to file (no stdout)."""
    logger = logging.getLogger(name)

    if force_reconfigure:
        logger.handlers.clear()

    if not logger.handlers:
        filename = log_filename or f"{name}.log"
        log_file_path = LOG_DIR / filename
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            file_handler = _create_rotating_file_handler(str(log_file_path))
            formatter = ReadableFormatter()
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            console_handler = logging.StreamHandler(sys.stdout)
            formatter = ReadableFormatter()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            print(
                f"Warning: Could not create log file {log_file_path}: {e}",
                file=sys.stderr,
            )

        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger


def set_transaction_id(transaction_id: str) -> None:
    """Set the transaction ID for the current context."""
    _transaction_id.set(transaction_id)


def get_transaction_id() -> str:
    """Get the current transaction ID."""
    return _transaction_id.get("")


class ReadableFormatter(logging.Formatter):
    """Custom readable formatter with transaction ID support."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as readable text."""
        base_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(base_format)
        message = formatter.format(record)

        if transaction_id := get_transaction_id():
            message = f"[{transaction_id}] {message}"

        if hasattr(record, "extra_fields"):
            extra_fields = record.extra_fields
            extra = " ".join(f"{k}={v}" for k, v in extra_fields.items())
            message = f"{message} | {extra}"

        return message


class StructuredLogger:
    """Wrapper for structured logging with extra fields."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """Internal logging method with extra fields."""
        record = self._logger.makeRecord(
            self._logger.name,
            level,
            "(unknown file)",
            0,
            message,
            (),
            None,
        )
        record.extra_fields = kwargs  # type: ignore[attr-defined]
        self._logger.handle(record)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info level message with extra fields."""
        self._log(logging.INFO, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error level message with extra fields."""
        self._log(logging.ERROR, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning level message with extra fields."""
        self._log(logging.WARNING, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical level message with extra fields."""
        self._log(logging.CRITICAL, message, **kwargs)
