# Implementation Strategy

## Approach

Use a small VitePress site under `docs/` instead of changing the Python runtime package.

## Why this shape

- Keeps the benchmark harness untouched
- Gives the repo a public-facing surface quickly
- Uses Bun for the JS layer as requested

## Notes

- Keep the docs content derived from the current source tree.
- Keep the landing page concise and task-oriented.

