#!/usr/bin/env python3
from __future__ import annotations

import ast
import sys
from pathlib import Path


def iter_python_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths or ["src", "tests"]:
        path = Path(raw)
        if path.is_file() and path.suffix == ".py":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.py")))
    return files


def typing_guard_lines(tree: ast.AST) -> set[int]:
    lines: set[int] = set()
    for node in ast.walk(tree):
        is_guard = isinstance(node, ast.If)
        is_name = is_guard and isinstance(node.test, ast.Name)
        if is_name and node.test.id == "TYPE_CHECKING":
            for child in ast.walk(node):
                if hasattr(child, "lineno"):
                    lines.add(child.lineno)
    return lines


def file_violations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    lines = path.read_text(encoding="utf-8").splitlines()
    guarded = typing_guard_lines(tree)
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            has_typing_only = "typing-only" in lines[node.lineno - 1].lower()
            if has_typing_only and node.lineno not in guarded:
                out.append(f"{path}:{node.lineno}: typing-only import must be guarded")
    return out


def main() -> int:
    violations: list[str] = []
    for path in iter_python_files(sys.argv[1:]):
        violations.extend(file_violations(path))
    if not violations:
        return 0
    print("Found typing-import violations:")
    for violation in violations:
        print(f"  - {violation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
