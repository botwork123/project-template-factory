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
    for lane in ["ci / lint", "ci / imports", "ci / mypy", "ci / test", "ci / cycles", "ci / report"]:
        assert lane in ci

    precommit = (project / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    for hook in ["typing-imports", "semgrep-import-policy", "semgrep-guardrails", "semgrep-python-ethos"]:
        assert hook in precommit

    assert (project / "scripts/detect_import_cycles.py").exists()
    assert (project / "scripts/import_cycle_baseline.txt").exists()
    run_script = (project / "scripts/wt_run.sh").read_text(encoding="utf-8")
    assert "find_spec(\"demo_pkg\")" in run_script
