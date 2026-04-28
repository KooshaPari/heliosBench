# Session Overview

## Goal

Add a `Taskfile.yml` that exposes common repo tasks and routes them to the
correct stack based on the repository manifests.

## Success criteria

- `Taskfile.yml` exists at repo root
- `build`, `test`, `lint`, and `clean` work from the repo root
- The task runner prefers the Python project metadata and still notices the docs shell

