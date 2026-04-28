# Implementation Strategy

Use one root `Taskfile.yml` with simple shell conditionals:

- Prefer Python commands when `pyproject.toml` is present
- Detect docs support via `package.json`
- Keep the clean step limited to generated artifacts

