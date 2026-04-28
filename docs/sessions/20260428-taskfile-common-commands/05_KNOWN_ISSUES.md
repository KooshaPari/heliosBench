# Known Issues

- `build` assumes `uv` is available when building the Python package.
- If `uv` is unavailable, the task falls back to `python -m build`.

