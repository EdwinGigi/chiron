from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for Chiron."""

    # GitHub App config
    github_app_id: int
    github_private_key_path: str
    github_webhook_secret: str

    # Google Gemini
    gemini_api_key: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    # App
    log_level: str = "INFO"
    fix_strategy: Literal["direct", "branch"] = "branch"
    sentry_dsn: str = ""
    port: int = 8080

    # Review settings
    max_fix_attempts: int = 3
    review_timeout_seconds: int = 300

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings() -> Settings:
    """Returns the application settings."""
    return Settings()
