"""
Global exception handlers for comprehensive error logging and response formatting.
"""

import traceback

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import app_logger, security_logger


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    # Log the full exception with traceback
    app_logger.error(
        "Unhandled exception occurred",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
        },
    )

    # Return generic error response (don't expose internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
            "error_code": "INTERNAL_ERROR",
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for HTTP exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    # Log based on status code severity
    log_data = {
        "request_id": request_id,
        "url": str(request.url),
        "method": request.method,
        "status_code": exc.status_code,
        "detail": exc.detail,
    }

    if exc.status_code >= 500:
        app_logger.error("Server error", extra=log_data)
    elif exc.status_code >= 400:
        app_logger.warning("Client error", extra=log_data)
    else:
        app_logger.info("HTTP exception", extra=log_data)

    # Log security-relevant errors
    if exc.status_code in [401, 403, 404]:
        security_logger.warning(
            "Security-relevant HTTP error",
            extra={
                **log_data,
                "client_ip": request.headers.get(
                    "x-forwarded-for",
                    request.client.host if request.client else "unknown",
                ),
                "user_agent": request.headers.get("user-agent", ""),
            },
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": request_id,
            "error_code": f"HTTP_{exc.status_code}",
        },
    )


async def starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handler for Starlette HTTP exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    app_logger.warning(
        "Starlette HTTP exception",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "request_id": request_id,
            "error_code": f"HTTP_{exc.status_code}",
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler for request validation errors."""
    request_id = getattr(request.state, "request_id", "unknown")

    # Format validation errors
    validation_errors = []
    for error in exc.errors():
        validation_errors.append(
            {
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    app_logger.warning(
        "Request validation failed",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "validation_errors": validation_errors,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "request_id": request_id,
            "error_code": "VALIDATION_ERROR",
            "validation_errors": validation_errors,
        },
    )


async def database_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handler for database-related exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")

    app_logger.error(
        "Database error occurred",
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "request_id": request_id,
            "error_code": "DATABASE_ERROR",
        },
    )


def setup_exception_handlers(app) -> None:
    """Setup all exception handlers for the FastAPI app."""
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)

    app_logger.info("Exception handlers configured")
