from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[5]


class Environment(StrEnum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", REPO_ROOT / ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_name: str = Field(default="AURA", alias="PROJECT_NAME")
    project_description: str = Field(
        default="Autonomous Unified Reel Assistant API",
        alias="PROJECT_DESCRIPTION",
    )
    environment: Environment = Field(default=Environment.DEVELOPMENT, alias="ENVIRONMENT")
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    docs_enabled: bool = Field(default=True, alias="DOCS_ENABLED")

    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    rabbitmq_url: str = Field(alias="RABBITMQ_URL")
    ollama_base_url: AnyHttpUrl = Field(alias="OLLAMA_BASE_URL")
    openai_base_url: AnyHttpUrl = Field(alias="OPENAI_BASE_URL")
    openai_api_key: SecretStr = Field(alias="OPENAI_API_KEY")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_dir: Path = Field(default=REPO_ROOT / "logs", alias="LOG_DIR")
    health_disk_path: Path = Field(default=REPO_ROOT, alias="HEALTH_DISK_PATH")
    health_timeout_seconds: float = Field(
        default=2.0,
        alias="HEALTH_TIMEOUT_SECONDS",
        ge=0.1,
        le=30.0,
    )
    rate_limit_requests: int = Field(default=120, alias="RATE_LIMIT_REQUESTS", ge=1, le=10000)
    rate_limit_window_seconds: int = Field(
        default=60,
        alias="RATE_LIMIT_WINDOW_SECONDS",
        ge=1,
        le=3600,
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        normalized = value.upper()
        allowed_levels = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        if normalized not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {sorted(allowed_levels)}")
        return normalized

    @field_validator("health_disk_path")
    @classmethod
    def validate_health_disk_path(cls, value: Path) -> Path:
        resolved = value.resolve()
        if not resolved.exists():
            raise ValueError("HEALTH_DISK_PATH must exist")
        return resolved

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("API_V1_PREFIX must start with '/'")
        return value.rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
