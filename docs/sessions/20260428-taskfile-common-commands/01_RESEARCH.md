# Research

## Repo signals

- `pyproject.toml` defines the Python package, test config, and ruff config.
- `package.json` only exposes VitePress docs scripts.
- `README.md` describes the benchmark harness as a Python CLI with docs support.

## Conclusion

The repo is Python-first, so the common task aliases should use `uv`/`pytest`/`ruff`
for the main flow and optionally run the docs build when the VitePress manifest is present.

