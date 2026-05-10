from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    failed = False
    for name in argv[1:]:
        path = Path(name)
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
        except OSError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            failed = True
            continue
        for lineno, line in enumerate(lines, start=1):
            stripped_newline = line.rstrip("\r\n")
            if stripped_newline.rstrip(" \t") != stripped_newline:
                print(f"{path}:{lineno}: trailing whitespace", file=sys.stderr)
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
