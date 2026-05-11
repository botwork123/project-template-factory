from __future__ import annotations

import sys
from pathlib import Path


CONFLICT_MARKERS = ("<<<<<<< ", "=======", ">>>>>>> ")


def main(argv: list[str]) -> int:
    failed = False
    for name in argv[1:]:
        path = Path(name)
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            failed = True
            continue
        for lineno, line in enumerate(lines, start=1):
            if any(line.startswith(marker) for marker in CONFLICT_MARKERS):
                print(f"{path}:{lineno}: merge conflict marker found", file=sys.stderr)
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
