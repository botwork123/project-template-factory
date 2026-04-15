from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings shared by local and container execution."""

    app_env: str
    app_host: str
    app_port: int
    log_level: str


# Ordered schema is the single source of truth for env contract + .env.example.
_ENV_SCHEMA: tuple[tuple[str, str], ...] = (
    ("APP_ENV", "dev"),
    ("APP_HOST", "0.0.0.0"),
    ("APP_PORT", "8000"),
    ("LOG_LEVEL", "INFO"),
)


def _env_value(key: str) -> str:
    default = dict(_ENV_SCHEMA)[key]
    return os.getenv(key, default)


def load_settings() -> AppSettings:
    return AppSettings(
        app_env=_env_value("APP_ENV"),
        app_host=_env_value("APP_HOST"),
        app_port=int(_env_value("APP_PORT")),
        log_level=_env_value("LOG_LEVEL"),
    )


def validate_startup(settings: AppSettings) -> None:
    if settings.app_port <= 0:
        raise ValueError("APP_PORT must be a positive integer")
    if settings.log_level.upper() not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL")


def generate_env_example(destination: str | Path = ".env.example") -> Path:
    path = Path(destination)
    lines = [f"{key}={default}" for key, default in _ENV_SCHEMA]
    body = "\n".join(lines) + "\n"
    path.write_text(body, encoding="utf-8")
    return path
