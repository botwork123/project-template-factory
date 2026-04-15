from __future__ import annotations

from __PROJECT_NAME__.settings import load_settings, validate_startup


def runtime_banner() -> str:
    settings = load_settings()
    validate_startup(settings)
    return (
        f"starting __PROJECT_NAME__ env={settings.app_env} "
        f"bind={settings.app_host}:{settings.app_port}"
    )


def main() -> int:
    print(runtime_banner())
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
