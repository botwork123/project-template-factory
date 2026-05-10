from __future__ import annotations

import sys
from pathlib import Path

import yaml


def main(argv: list[str]) -> int:
    failed = False
    for name in argv[1:]:
        path = Path(name)
        try:
            with path.open("r", encoding="utf-8") as handle:
                yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            print(f"{path}: invalid yaml: {exc}", file=sys.stderr)
            failed = True
        except OSError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
