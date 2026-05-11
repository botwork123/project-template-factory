#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$REPO_ROOT/.venv"
VENV_PY="$VENV_DIR/bin/python"

if [[ ! -x "$VENV_PY" ]]; then
  echo "[wt_doctor] Missing worktree-local venv at $VENV_PY" >&2
  echo "[wt_doctor] Run: ./scripts/wt_env.sh" >&2
  exit 1
fi

export VIRTUAL_ENV="$VENV_DIR"
export PATH="$VENV_DIR/bin:$PATH"

ACTIVE_PY="$(command -v python)"
ACTIVE_PY_ABS="$(python -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$ACTIVE_PY")"
VENV_PY_ABS="$(python -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$VENV_PY")"

if [[ "$ACTIVE_PY_ABS" != "$VENV_PY_ABS" ]]; then
  echo "[wt_doctor] Active python is not this worktree venv python" >&2
  echo "[wt_doctor] active: $ACTIVE_PY_ABS" >&2
  echo "[wt_doctor] expect: $VENV_PY_ABS" >&2
  echo "[wt_doctor] Run: ./scripts/wt_env.sh" >&2
  exit 1
fi

"$VENV_PY" - "$REPO_ROOT" "$VENV_PY_ABS" "$VENV_DIR" <<'PY'
import importlib.util
import pathlib
import sys

repo_root = pathlib.Path(sys.argv[1]).resolve()
expected_python = pathlib.Path(sys.argv[2])
expected_venv_dir = pathlib.Path(sys.argv[3]).resolve()

if pathlib.Path(sys.executable) != expected_python:
    print("[wt_doctor] Interpreter drift detected", file=sys.stderr)
    raise SystemExit(1)

if pathlib.Path(sys.prefix).resolve() != expected_venv_dir:
    print("[wt_doctor] Virtualenv prefix drift detected", file=sys.stderr)
    raise SystemExit(1)

spec = importlib.util.find_spec("__PROJECT_NAME__")
if spec is None:
    print("[wt_doctor] Unable to resolve package import", file=sys.stderr)
    raise SystemExit(1)

origin_path: pathlib.Path | None = None
if spec.origin and spec.origin not in {"built-in", "frozen"}:
    origin_path = pathlib.Path(spec.origin).resolve()
elif spec.submodule_search_locations:
    pkg_root = pathlib.Path(next(iter(spec.submodule_search_locations))).resolve()
    origin_path = pkg_root / "__init__.py"

if origin_path is None:
    print("[wt_doctor] Could not determine package origin path", file=sys.stderr)
    raise SystemExit(1)

if not str(origin_path).startswith(str(repo_root) + "/"):
    print("[wt_doctor] Package import is outside this worktree", file=sys.stderr)
    print(f"[wt_doctor] package.__file__: {origin_path}", file=sys.stderr)
    print(f"[wt_doctor] worktree root: {repo_root}", file=sys.stderr)
    raise SystemExit(1)
PY

echo "[wt_doctor] OK"
