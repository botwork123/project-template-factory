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
    env = dict(os.environ)
    env.setdefault("XDG_CACHE_HOME", str(tmp_path / ".cache"))
    # Ensure initial scaffold commit works in CI where global git identity may be absent.
    env.setdefault("GIT_AUTHOR_NAME", "template-ci")
    env.setdefault("GIT_AUTHOR_EMAIL", "template-ci@example.com")
    env.setdefault("GIT_COMMITTER_NAME", env["GIT_AUTHOR_NAME"])
    env.setdefault("GIT_COMMITTER_EMAIL", env["GIT_AUTHOR_EMAIL"])
    result = _run(["./newproj", name, stack, str(tmp_path)], cwd=root, env=env)
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
        "scripts/generate_env_example.py",
        "scripts/prefect/deploy.sh",
        ".github/workflows/ci.yml",
        ".forgejo/workflows/ci.yml",
        "requirements/ci-constraints.txt",
        "Dockerfile",
        ".dockerignore",
        "docker-compose.yml",
        "prefect.yaml",
        "docs/deployment.md",
        ".env.example",
    ]
    for rel in required:
        assert (project / rel).exists(), f"missing expected file: {rel}"


def test_python_generation_supports_hyphenated_distribution_name(tmp_path: Path) -> None:
    project = _generate(tmp_path, "promotion-service", "python")
    assert (project / "src/promotion_service/__init__.py").exists()
    assert "from promotion_service.settings import" in (
        project / "scripts/generate_env_example.py"
    ).read_text(encoding="utf-8")
    assert 'name = "promotion-service"' in (project / "pyproject.toml").read_text(encoding="utf-8")


def test_python_env_example_generation_is_deterministic(tmp_path: Path) -> None:
    project = _generate(tmp_path, "smoke_py_env", "python")
    before = (project / ".env.example").read_text(encoding="utf-8")
    result = _run(["python3", "scripts/generate_env_example.py"], cwd=project)
    _assert_success(result, "generate_env_example")
    after = (project / ".env.example").read_text(encoding="utf-8")
    assert before == after


def test_typescript_generation_smoke(tmp_path: Path) -> None:
    project = _generate(tmp_path, "smoke_ts", "typescript")
    scripts = json.loads((project / "package.json").read_text(encoding="utf-8")).get("scripts", {})
    assert scripts.get("build") == "tsc --noEmit"
    assert scripts.get("test") == "vitest run"
    assert (project / "package-lock.json").exists()
    workflow = (project / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "npm ci" in workflow
    assert "npm run -s build" in workflow
    assert "npm test" in workflow
    assert (project / ".github/workflows/release.yml").exists()


def test_generated_typescript_project_passes_ci_commands(tmp_path: Path) -> None:
    assert shutil.which("npm"), "npm is required for this smoke test"
    project = _generate(tmp_path, "smoke_ts_ci", "typescript")
    env = dict(os.environ)
    env["npm_config_cache"] = str(tmp_path / ".npm-cache")
    for command, marker in [
        (["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], "npm ci"),
        (["npm", "run", "-s", "build"], "npm build"),
        (["npm", "test"], "npm test"),
    ]:
        _assert_success(_run(command, cwd=project, env=env), marker)


def test_rust_generation_smoke(tmp_path: Path) -> None:
    project = _generate(tmp_path, "smoke_rs", "rust")
    cargo_toml = (project / "Cargo.toml").read_text(encoding="utf-8")
    assert 'name = "smoke_rs"' in cargo_toml
    assert (project / ".github/workflows/ci.yml").exists()
    assert (project / ".github/workflows/release.yml").exists()


def _run_python_checks(project: Path, env: dict[str, str]) -> None:
    pre_commit_cmd = ["./scripts/wt_run.sh", "pre-commit", "run", "--all-files"]
    first = _run(pre_commit_cmd, cwd=project, env=env)
    if first.returncode != 0 and "files were modified by this hook" in first.stdout:
        first = _run(pre_commit_cmd, cwd=project, env=env)
    _assert_success(first, "pre-commit")

    checks = [
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
    env.setdefault("XDG_CACHE_HOME", str(tmp_path / ".cache"))
    bootstrap = _run(["./scripts/wt_bootstrap.sh"], cwd=project, env=env)
    _assert_success(bootstrap, "wt_bootstrap")
    _run_python_checks(project, env)
    assert "[wt_bootstrap] Using uv" in bootstrap.stdout
