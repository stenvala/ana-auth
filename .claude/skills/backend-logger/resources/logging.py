"""Centralized logging utilities."""

import logging
import logging.handlers
import os
import sys
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Optional

# Context variable to store correlation/transaction ID across async calls
_transaction_id: ContextVar[str] = ContextVar("transaction_id", default="")


def get_log_root() -> str:
    """Get the log root directory path.

    Priority:
    1. LOG_ROOT environment variable if set
    2. Repository root/logs (calculated from module location)

    Returns:
        Absolute path to log root directory
    """
    if "LOG_ROOT" in os.environ:
        return os.environ["LOG_ROOT"]
    # Default to repository root/logs (src/shared is 3 levels deep from repo root)
    repo_root = Path(__file__).parent.parent.parent
    return str(repo_root / "logs")


LOG_ROOT = get_log_root()
LOG_DIR = Path(LOG_ROOT)

# Debug: print where logs are going (helpful for deployment issues)
if "LOG_ROOT" in os.environ:
    _log_source = f"from env variable LOG_ROOT={LOG_ROOT}"
else:
    _log_source = f"using default {LOG_ROOT}"
print(f"[logging.py] Initialized logging: {_log_source}", file=sys.stderr)

LOG_DIR.mkdir(parents=True, exist_ok=True)


# Log rotation settings
LOG_MAX_BYTES = 1 * 1024 * 1024  # 1 MB per file
LOG_BACKUP_COUNT = 10  # Keep 10 backup files (.log.1 through .log.10)


def _create_rotating_file_handler(
    filename: str,
) -> logging.handlers.RotatingFileHandler:
    """Create a rotating file handler with standard rotation settings.

    Rotates at 1 MB, keeps 10 backups (11 files total: .log + .log.1 through .log.10).
    """
    return logging.handlers.RotatingFileHandler(
        filename=filename,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )


def get_logger(
    name: str, add_file_handler: bool = False, log_filename: Optional[str] = None
) -> logging.Logger:
    """Get a logger instance with readable text formatting.

    Args:
        name: Logger name
        add_file_handler: Whether to add a file handler with rotation
        log_filename: Custom log filename (defaults to {name}.log)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = ReadableFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Add rotating file handler if requested
        if add_file_handler:
            filename = log_filename or f"{name}.log"
            file_handler = _create_rotating_file_handler(str(LOG_DIR / filename))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        logger.setLevel(logging.INFO)

    return logger


def get_file_logger(
    name: str, log_filename: Optional[str] = None, force_reconfigure: bool = False
) -> logging.Logger:
    """Get a logger instance that writes only to file (no stdout).

    Args:
        name: Logger name
        log_filename: Custom log filename (defaults to {name}.log)
        force_reconfigure: If True, reconfigure logger even if handlers exist (useful for multiprocessing)

    Returns:
        Configured logger instance with only file handler
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured, or if force_reconfigure is True
    if force_reconfigure:
        logger.handlers.clear()

    if not logger.handlers:
        filename = log_filename or f"{name}.log"
        log_file_path = LOG_DIR / filename

        # Ensure parent directory exists
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            file_handler = _create_rotating_file_handler(str(log_file_path))
            formatter = ReadableFormatter()
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            # Fallback to console if file creation fails
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

        # Add transaction ID if available
        if transaction_id := get_transaction_id():
            message = f"[{transaction_id}] {message}"

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            extra_fields = getattr(record, "extra_fields")
            extra = " ".join(f"{k}={v}" for k, v in extra_fields.items())
            message = f"{message} | {extra}"

        return message


class StructuredLogger:
    """Wrapper for structured logging with extra fields."""

    def __init__(self, logger: logging.Logger):
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
        record.extra_fields = kwargs
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

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug level message with extra fields."""
        self._log(logging.DEBUG, message, **kwargs)


def diagnose_logging() -> None:
    """Print diagnostic information about logging configuration."""
    print(f"LOG_ROOT: {LOG_ROOT}")
    print(f"LOG_DIR: {LOG_DIR}")
    print(f"LOG_DIR exists: {LOG_DIR.exists()}")
    print(f"LOG_DIR is writable: {os.access(LOG_DIR, os.W_OK)}")

    # Try creating a test file
    test_file = LOG_DIR / ".logging_test"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print("Can write to LOG_DIR: Yes")
    except Exception as e:
        print(f"Can write to LOG_DIR: No ({e})")
