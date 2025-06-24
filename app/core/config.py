"""
Application configuration management using Pydantic Settings.
"""

from functools import lru_cache
from typing import Annotated

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "FastAPI Template"
    app_version: str = "0.1.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    port: int = 8000

    # Security
    secret_key: Annotated[str, Field(min_length=32)] = (
        "your-super-secret-key-change-this-in-production"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json, text, or structured
    log_file: str | None = "logs/app.log"  # Optional log file path
    log_max_size: int = 10  # MB
    log_retention: int = 7  # days
    log_rotation: str = "daily"  # daily, weekly, or size
    console_log_format: str = "pretty"  # pretty, json, text, or structured
    enable_request_logging: bool = True
    enable_sql_logging: bool = False
    log_sql_queries: bool = False
    log_slow_queries_threshold: float = 1.0  # seconds

    # Database
    postgres_server: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    postgres_db: str = "fastapi_template"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    model_config = {"env_file": ".env", "case_sensitive": False}


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
