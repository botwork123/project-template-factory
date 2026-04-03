#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from pathlib import Path


def build_graph(src_dir: Path, package: str) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    modules = collect_modules(src_dir, package)
    for py in src_dir.rglob("*.py"):
        mod = module_name(py, src_dir, package)
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            add_import_edge(graph, modules, mod, node)
    for module in modules:
        graph.setdefault(module, set())
    return graph


def collect_modules(src_dir: Path, package: str) -> set[str]:
    modules: set[str] = set()
    for py in src_dir.rglob("*.py"):
        modules.add(module_name(py, src_dir, package))
    return modules


def module_name(path: Path, src_dir: Path, package: str) -> str:
    rel = path.relative_to(src_dir).with_suffix("")
    return package + "." + ".".join(rel.parts)


def add_import_edge(
    graph: dict[str, set[str]], modules: set[str], mod: str, node: ast.AST
) -> None:
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name in modules:
                graph[mod].add(alias.name)
    if isinstance(node, ast.ImportFrom):
        target = node.module or ""
        if node.level > 0:
            parts = mod.split(".")
            base = ".".join(parts[:-node.level])
            target = f"{base}.{target}".strip(".")
        if target in modules:
            graph[mod].add(target)


def sccs(graph: dict[str, set[str]]) -> list[list[str]]:
    found: list[list[str]] = []
    seen: set[str] = set()
    for start in sorted(graph):
        if start in seen:
            continue
        stack = [start]
        component: set[str] = set()
        while stack:
            node = stack.pop()
            if node in component:
                continue
            component.add(node)
            stack.extend(graph[node])
            stack.extend([n for n, edges in graph.items() if node in edges])
        seen.update(component)
        if len(component) > 1:
            found.append(sorted(component))
    return sorted(found, reverse=True)


def load_baseline(path: Path) -> set[tuple[str, ...]]:
    if not path.exists():
        return set()
    groups: list[list[str]] = [[]]
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line:
            groups[-1].append(line)
        elif groups[-1]:
            groups.append([])
    return {tuple(sorted(group)) for group in groups if group}


def write_baseline(path: Path, comps: list[list[str]]) -> None:
    body = "\n\n".join("\n".join(comp) for comp in comps)
    path.write_text((body + "\n") if body else "", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="src/__PROJECT_NAME__")
    parser.add_argument("--package", default="__PROJECT_NAME__")
    parser.add_argument("--baseline", default="scripts/import_cycle_baseline.txt")
    parser.add_argument("--fail-on", choices=["none", "any", "new"], default="new")
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args()

    cycles = sccs(build_graph(Path(args.src), args.package))
    baseline_path = Path(args.baseline)

    if args.write_baseline:
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        write_baseline(baseline_path, cycles)
        return 0
    if args.fail_on == "none":
        return 0
    if args.fail_on == "any":
        return 1 if cycles else 0

    baseline = load_baseline(baseline_path)
    current = {tuple(comp) for comp in cycles}
    return 1 if current - baseline else 0


if __name__ == "__main__":
    raise SystemExit(main())
