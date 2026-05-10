from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    failed = False
    for name in argv[1:]:
        path = Path(name)
        try:
            content = path.read_bytes()
        except OSError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            failed = True
            continue
        if not content:
            continue
        if not content.endswith(b"\n"):
            print(f"{path}: missing trailing newline", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
