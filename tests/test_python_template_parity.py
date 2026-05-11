from __future__ import annotations

import subprocess
from pathlib import Path


def test_python_template_ci_lanes_and_scripts(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[1]
    dest_root = tmp_path / "out"
    dest_root.mkdir()

    subprocess.run(
        [str(repo / "newproj"), "demo_pkg", "python", str(dest_root)],
        check=True,
        cwd=repo,
    )

    project = dest_root / "demo_pkg"
    ci = (project / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for lane in [
        "ci / lint",
        "ci / imports",
        "ci / mypy",
        "ci / test",
        "ci / cycles",
        "ci / docker_smoke",
        "ci / prefect_scaffold",
        "ci / report",
    ]:
        assert lane in ci

    precommit = (project / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    for hook in ["typing-imports", "semgrep-import-policy", "semgrep-guardrails", "semgrep-python-ethos"]:
        assert hook in precommit

    assert (project / "scripts/detect_import_cycles.py").exists()
    assert (project / "scripts/import_cycle_baseline.txt").exists()
    assert (project / "scripts/generate_env_example.py").exists()
    assert (project / "scripts/prefect/deploy.sh").exists()

    run_script = (project / "scripts/wt_run.sh").read_text(encoding="utf-8")
    doctor_script = (project / "scripts/wt_doctor.sh").read_text(encoding="utf-8")
    assert "wt_doctor.sh" in run_script
    assert "find_spec(\"demo_pkg\")" in doctor_script

    dockerfile = (project / "Dockerfile").read_text(encoding="utf-8")
    prefect_yaml = (project / "prefect.yaml").read_text(encoding="utf-8")
    compose = (project / "docker-compose.yml").read_text(encoding="utf-8")
    assert "python\", \"-m\", \"demo_pkg.main\"" in dockerfile
    assert "command: [\"python\", \"-m\", \"demo_pkg.main\"]" in compose
    assert 'entrypoint: "src/demo_pkg/main.py:main"' in prefect_yaml
