# project-template-factory

Language-agnostic starter templates with enforced quality gates.

## Create a new project

```bash
./newproj <project-name> <python|typescript|rust> [destination]
```

Examples:

```bash
./newproj typetrace2 python ~/git
./newproj stream-engine typescript ~/git
./newproj fast-core rust ~/git
```

## Template CI (this repository)

This repository has its own CI workflow to validate template integrity and generator behavior.

### CI jobs

- `lint`: shell lint for `newproj`
- `template-tests`: run `pytest` suite for template/parity checks
- `generator-smoke`: run generator smoke tests for python/typescript/rust

### Local smoke commands

```bash
# full local test suite
pytest -q

# generation smoke only
pytest -q tests/test_newproj_smoke.py -k "generation_smoke or typescript or rust"

# generated python executable smoke (requires uv)
pytest -q tests/test_newproj_smoke.py -k generated_python_executable_smoke
```

## Goals

- Fast project bootstrap
- Consistent lint/type/test enforcement
- Clear encapsulation defaults
