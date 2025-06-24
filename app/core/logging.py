"""
Logging configuration and utilities for the FastAPI application.

This module provides:
- Structured logging with JSON and text formatters
- File rotation and retention
- Request/response logging middleware
- SQL query logging
- Performance monitoring
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "__dict__"):
            extra_fields = {
                k: v
                for k, v in record.__dict__.items()
                if k
                not in {
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "message",
                }
            }
            if extra_fields:
                log_data["extra"] = extra_fields

        return json.dumps(log_data, default=str)


class PrettyConsoleFormatter(logging.Formatter):
    """Pretty console formatter with colors and clean layout."""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
        "BOLD": "\033[1m",  # Bold
        "DIM": "\033[2m",  # Dim
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and clean layout."""
        # Parse structured log if it's from structlog
        message = record.getMessage()
        extra_data = {}

        try:
            if message.startswith("{") and '"event":' in message:
                import json

                data = json.loads(message)
                message = data.get("event", message)
                extra_data = data.get("extra", {})
        except Exception:
            pass

        # Extract timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # Color the log level
        level_color = self.COLORS.get(record.levelname, "")
        level = f"{level_color}{record.levelname:8}{self.COLORS['RESET']}"

        # Color the logger name
        logger_color = self.COLORS["DIM"]
        logger_name = f"{logger_color}{record.name}{self.COLORS['RESET']}"

        # Format the main message
        main_msg = (
            f"{self.COLORS['DIM']}{timestamp}{self.COLORS['RESET']} | "
            f"{level} | {logger_name} | {message}"
        )

        # Add extra data if present
        if extra_data:
            extra_items = []
            for k, v in extra_data.items():
                if k not in ["taskName"] and v is not None:  # Skip common noise
                    extra_items.append(f"{k}={v}")

            if extra_items:
                extra_str = (
                    f"{self.COLORS['DIM']} | "
                    f"{' | '.join(extra_items)}{self.COLORS['RESET']}"
                )
                main_msg += extra_str

        # Add exception info if present
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            main_msg += f"\n{self.COLORS['RED']}{exc_text}{self.COLORS['RESET']}"

        return main_msg


class StructuredFormatter(logging.Formatter):
    """Structured text formatter with key-value pairs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured key-value pairs."""
        timestamp = datetime.fromtimestamp(record.created).isoformat()
        base_msg = (
            f"{timestamp} | {record.levelname:8} | "
            f"{record.name} | {record.getMessage()}"
        )

        # Add extra fields
        if hasattr(record, "__dict__"):
            extra_fields = {
                k: v
                for k, v in record.__dict__.items()
                if k
                not in {
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "message",
                }
            }
            if extra_fields:
                extra_str = " | ".join([f"{k}={v}" for k, v in extra_fields.items()])
                base_msg += f" | {extra_str}"

        if record.exc_info:
            base_msg += f"\n{self.formatException(record.exc_info)}"

        return base_msg


def get_formatter() -> logging.Formatter:
    """Get the appropriate formatter based on configuration."""
    if settings.log_format == "json":
        return JSONFormatter()
    elif settings.log_format == "structured":
        return StructuredFormatter()
    else:  # text format
        return logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def get_console_formatter() -> logging.Formatter:
    """Get the appropriate console formatter based on configuration."""
    if settings.console_log_format == "pretty":
        return PrettyConsoleFormatter()
    elif settings.console_log_format == "json":
        return JSONFormatter()
    elif settings.console_log_format == "structured":
        return StructuredFormatter()
    else:  # text format
        return logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )


def setup_file_handler() -> Optional[logging.Handler]:
    """Setup file handler with rotation if log file is configured."""
    if not settings.log_file:
        return None

    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if settings.log_rotation == "size":
        handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=settings.log_max_size * 1024 * 1024,  # Convert MB to bytes
            backupCount=settings.log_retention,
        )
    else:  # daily or weekly
        when = "D" if settings.log_rotation == "daily" else "W0"
        handler = logging.handlers.TimedRotatingFileHandler(
            log_path,
            when=when,
            interval=1,
            backupCount=settings.log_retention,
        )

    handler.setFormatter(get_formatter())
    return handler


def setup_console_handler() -> logging.Handler:
    """Setup console handler."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(get_console_formatter())
    return handler


def setup_error_file_handler() -> Optional[logging.Handler]:
    """Setup separate error file handler."""
    if not settings.log_file:
        return None

    error_log_path = Path(settings.log_file).parent / "app_error.log"
    error_log_path.parent.mkdir(parents=True, exist_ok=True)

    if settings.log_rotation == "size":
        handler = logging.handlers.RotatingFileHandler(
            error_log_path,
            maxBytes=settings.log_max_size * 1024 * 1024,
            backupCount=settings.log_retention,
        )
    else:
        when = "D" if settings.log_rotation == "daily" else "W0"
        handler = logging.handlers.TimedRotatingFileHandler(
            error_log_path,
            when=when,
            interval=1,
            backupCount=settings.log_retention,
        )

    handler.setLevel(logging.ERROR)
    handler.setFormatter(get_formatter())
    return handler


def setup_structlog() -> None:
    """Setup structlog for structured logging."""
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def setup_logging() -> None:
    """Setup application logging configuration."""
    # Setup structlog
    setup_structlog()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Add console handler
    console_handler = setup_console_handler()
    root_logger.addHandler(console_handler)

    # Add file handler if configured
    file_handler = setup_file_handler()
    if file_handler:
        root_logger.addHandler(file_handler)

    # Add error file handler
    error_handler = setup_error_file_handler()
    if error_handler:
        root_logger.addHandler(error_handler)

    # Configure specific loggers
    configure_external_loggers()

    # Log configuration
    app_logger.info(
        "Logging configured",
        extra={
            "log_level": settings.log_level,
            "log_format": settings.log_format,
            "log_file": settings.log_file,
            "log_rotation": settings.log_rotation,
            "handlers": len(root_logger.handlers),
        },
    )


def configure_external_loggers() -> None:
    """Configure external library loggers."""
    # SQLAlchemy logging
    if settings.enable_sql_logging:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        if settings.log_sql_queries:
            logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.INFO)
    else:
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    # Uvicorn logging
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    # FastAPI logging
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Development tools - reduce noise
    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)  # File watcher
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    # Third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
    logging.getLogger("starlette").setLevel(logging.WARNING)


class PerformanceLogger:
    """Logger for performance monitoring."""

    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)

    def log_slow_query(
        self, query: str, duration: float, params: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log slow database queries."""
        if duration >= settings.log_slow_queries_threshold:
            self.logger.warning(
                "Slow query detected",
                extra={
                    "query": query,
                    "duration_seconds": duration,
                    "params": params,
                    "threshold": settings.log_slow_queries_threshold,
                },
            )

    def log_request_timing(
        self, method: str, path: str, duration: float, status_code: int
    ) -> None:
        """Log request timing information."""
        level = logging.WARNING if duration > 1.0 else logging.INFO
        self.logger.log(
            level,
            "Request completed",
            extra={
                "method": method,
                "path": path,
                "duration_seconds": duration,
                "status_code": status_code,
            },
        )


# Global logger instances
app_logger = structlog.get_logger("app")
api_logger = structlog.get_logger("api")
database_logger = structlog.get_logger("database")
security_logger = structlog.get_logger("security")
performance_logger = PerformanceLogger()


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_exception(
    logger: structlog.BoundLogger,
    exc: Exception,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """Log an exception with context."""
    extra = {"exception_type": type(exc).__name__, "exception_message": str(exc)}
    if context:
        extra.update(context)

    logger.error("Exception occurred", exc_info=exc, extra=extra)


def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """Log security-related events."""
    security_logger = get_logger("security")
    security_logger.warning(
        "Security event", extra={"event_type": event_type, **details}
    )
