from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_python_template_has_required_bootstrap_assets() -> None:
    root = _repo_root()
    required = [
        "templates/python/scripts/wt_bootstrap.sh",
        "templates/python/scripts/wt_run.sh",
        "templates/python/requirements/ci-constraints.txt",
        "templates/python/.github/workflows/ci.yml",
    ]
    for rel in required:
        assert (root / rel).exists(), f"missing python template asset: {rel}"


def _clean_template_caches(root: Path) -> None:
    for cache in root.glob("templates/**/__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    for pyc in root.glob("templates/**/*.pyc"):
        pyc.unlink(missing_ok=True)


def test_python_generated_ci_has_required_lanes(tmp_path: Path) -> None:
    root = _repo_root()
    _clean_template_caches(root)
    project = tmp_path / "parity_py"
    cmd = ["./newproj", "parity_py", "python", str(tmp_path)]
    result = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    ci = (project / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "./scripts/wt_bootstrap.sh" in ci
    assert "./scripts/wt_run.sh mypy src/__PROJECT_NAME__" in ci
    assert "./scripts/wt_run.sh pytest --cov=src/__PROJECT_NAME__ --cov-fail-under=90" in ci
    assert "detect_import_cycles.py --fail-on new" in ci


def test_typescript_template_retains_build_and_test_scripts() -> None:
    package_json = _repo_root() / "templates/typescript/package.json"
    scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts", {})
    assert scripts.get("build") == "tsc --noEmit"
    assert scripts.get("test") == "vitest run"
