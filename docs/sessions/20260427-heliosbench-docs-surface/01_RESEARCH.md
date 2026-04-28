# Research

## Local sources checked

- `README.md`
- `pyproject.toml`
- `src/helios_bench/__init__.py`
- `src/helios_bench/tasks.py`
- `src/helios_bench/cli.py`

## Findings

- The harness already has a clear benchmark story: run tasks, compare binaries, and detect leaks.
- The task catalog is small and stable enough to document directly.
- The package is still Python-first, so the docs shell should stay separate from runtime code.
- Bun is the correct JS package manager to use for the docs layer in this workspace.

