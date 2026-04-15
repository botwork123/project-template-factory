from __future__ import annotations

import pytest


def _runtime_banner():
    pytest.importorskip("__PROJECT_NAME__")
    from __PROJECT_NAME__.main import runtime_banner

    return runtime_banner


def _main_func():
    pytest.importorskip("__PROJECT_NAME__")
    from __PROJECT_NAME__.main import main

    return main


def test_runtime_banner_contains_bind_target(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_HOST", "127.0.0.1")
    monkeypatch.setenv("APP_PORT", "9000")
    banner = _runtime_banner()()
    assert "env=test" in banner
    assert "127.0.0.1:9000" in banner


def test_main_prints_banner(monkeypatch, capsys) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_HOST", "127.0.0.1")
    monkeypatch.setenv("APP_PORT", "9000")
    exit_code = _main_func()()
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "starting __PROJECT_NAME__" in captured.out
