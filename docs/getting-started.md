# Getting Started

HeliosBench ships as a Python package with a small CLI and a task catalog.

## Install

```bash
cd heliosBench
pip install -e .
```

## Inspect tasks

```bash
helios-bench tasks
```

## Run a benchmark

```bash
helios-bench run --binary /path/to/codex --task palindrome --runs 5
```

## Compare binaries

```bash
helios-bench compare --binary-a custom-codex --binary-b homebrew-codex
```

## Check for leaks

```bash
helios-bench leak --binary /path/to/codex --runs 20
```

## Output shape

Each run records elapsed time and resource stats so the same task can be compared across
builds, binaries, and environments.
