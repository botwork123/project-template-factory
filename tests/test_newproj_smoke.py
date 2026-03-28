from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False, env=env)


def _clean_template_caches(root: Path) -> None:
    for cache in root.glob("templates/**/__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    for pyc in root.glob("templates/**/*.pyc"):
        pyc.unlink(missing_ok=True)


def _generate(tmp_path: Path, name: str, stack: str) -> Path:
    root = _repo_root()
    _clean_template_caches(root)
    result = _run(["./newproj", name, stack, str(tmp_path)], cwd=root)
    assert result.returncode == 0, result.stderr
    project = tmp_path / name
    assert project.exists(), f"missing generated project: {project}"
    return project


def _assert_success(result: subprocess.CompletedProcess[str], marker: str) -> None:
    detail = f"{marker} failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    assert result.returncode == 0, detail


def test_python_generation_smoke(tmp_path: Path) -> None:
    project = _generate(tmp_path, "smoke_py", "python")
    required = [
        "scripts/wt_bootstrap.sh",
        "scripts/wt_run.sh",
        "scripts/detect_import_cycles.py",
        "scripts/import_cycle_baseline.txt",
        ".github/workflows/ci.yml",
        "requirements/ci-constraints.txt",
    ]
    for rel in required:
        assert (project / rel).exists(), f"missing expected file: {rel}"


def test_typescript_generation_smoke(tmp_path: Path) -> None:
    project = _generate(tmp_path, "smoke_ts", "typescript")
    scripts = json.loads((project / "package.json").read_text(encoding="utf-8")).get("scripts", {})
    assert scripts.get("build") == "tsc --noEmit"
    assert scripts.get("test") == "vitest run"
    assert (project / ".github/workflows/ci.yml").exists()


def test_rust_generation_smoke(tmp_path: Path) -> None:
    project = _generate(tmp_path, "smoke_rs", "rust")
    cargo_toml = (project / "Cargo.toml").read_text(encoding="utf-8")
    assert 'name = "smoke_rs"' in cargo_toml
    assert (project / ".github/workflows/ci.yml").exists()


def _run_python_checks(project: Path, env: dict[str, str]) -> None:
    checks = [
        (["./scripts/wt_run.sh", "pre-commit", "run", "--all-files"], "pre-commit"),
        (["./scripts/wt_run.sh", "mypy", "src/smoke_exec"], "mypy"),
        (["./scripts/wt_run.sh", "pytest", "-q"], "pytest"),
        (["./scripts/wt_run.sh", "python", "scripts/detect_import_cycles.py", "--fail-on", "new"], "import-cycles"),
    ]
    for cmd, marker in checks:
        _assert_success(_run(cmd, cwd=project, env=env), marker)


def test_generated_python_executable_smoke(tmp_path: Path) -> None:
    assert shutil.which("uv"), "uv is required for this smoke test"
    project = _generate(tmp_path, "smoke_exec", "python")
    env = dict(os.environ)
    env["CI"] = "1"
    bootstrap = _run(["./scripts/wt_bootstrap.sh"], cwd=project, env=env)
    _assert_success(bootstrap, "wt_bootstrap")
    _run_python_checks(project, env)
    assert "[wt_bootstrap] Using uv" in bootstrap.stdout
