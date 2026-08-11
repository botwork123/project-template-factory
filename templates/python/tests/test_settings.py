from __future__ import annotations

from pathlib import Path

import pytest


def _settings_symbols():
    pytest.importorskip("__IMPORT_NAME__")
    from __IMPORT_NAME__.settings import AppSettings, generate_env_example, validate_startup

    return AppSettings, generate_env_example, validate_startup


def test_generate_env_example_is_deterministic(tmp_path: Path) -> None:
    _, generate_env_example, _ = _settings_symbols()
    target = tmp_path / ".env.example"
    generate_env_example(target)
    first = target.read_text(encoding="utf-8")
    generate_env_example(target)
    second = target.read_text(encoding="utf-8")
    assert first == second
    assert "APP_ENV=dev" in first


def test_validate_startup_rejects_invalid_port() -> None:
    AppSettings, _, validate_startup = _settings_symbols()
    settings = AppSettings(app_env="dev", app_host="0.0.0.0", app_port=0, log_level="INFO")
    try:
        validate_startup(settings)
    except ValueError as exc:
        assert "APP_PORT" in str(exc)
    else:
        raise AssertionError("expected ValueError")
