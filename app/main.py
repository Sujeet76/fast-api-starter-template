"""
FastAPI application factory and configuration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import users
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import app_logger, setup_logging
from app.core.middleware import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    app_logger.info(
        "Application starting",
        extra={
            "service": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug,
            "environment": "development" if settings.debug else "production",
        },
    )
    yield
    # Shutdown
    app_logger.info("Application shutting down")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    # Setup logging first
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url=f"{settings.api_v1_prefix}/docs",
        redoc_url=f"{settings.api_v1_prefix}/redoc",
        lifespan=lifespan,
    )

    # Setup exception handlers
    setup_exception_handlers(app)

    # Add middleware in correct order (last added = first executed)

    # CORS middleware (should be last to handle CORS for all requests)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    if settings.enable_request_logging:
        app.add_middleware(RequestLoggingMiddleware)

    # Include routers
    app.include_router(
        users.router,
        prefix=f"{settings.api_v1_prefix}/users",
        tags=["users"],
    )

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": f"{settings.api_v1_prefix}/docs",
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": settings.app_name}

    return app


# Create app instance
app = create_app()
