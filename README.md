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

## Goals
- Fast project bootstrap
- Consistent lint/type/test enforcement
- Clear encapsulation defaults
