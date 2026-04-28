---
layout: home
title: HeliosBench
hero:
  name: HeliosBench
  text: Benchmark CLI tools with real resource data.
  tagline: Terminal-Bench style tasks, leak detection, and side-by-side binary comparison.
  actions:
    - theme: brand
      text: Getting Started
      link: /getting-started
    - theme: alt
      text: Task Catalog
      link: /tasks
features:
  - title: Resource monitoring
    details: Track CPU, RSS/VMS, file descriptors, threads, and elapsed time during each run.
  - title: Leak detection
    details: Compare repeated runs to surface memory and descriptor drift before it becomes a problem.
  - title: Comparison mode
    details: Run two binaries against the same workload and compare the result shapes directly.
  - title: JSON output
    details: Export machine-readable results for CI, baselines, and downstream analysis.
---

## What HeliosBench does

HeliosBench is a CLI benchmark harness for command-line tools. It wraps a task prompt,
measures the process while it runs, and records the result in a format that can be compared
across binaries and builds.

## Core flows

- Run one task against one binary.
- Compare two binaries with the same workload.
- Repeat a task many times to watch for leaks.
- Export results for CI and regression tracking.

## Built-in task families

- Code completion
- Code review
- Refactoring
- Debugging
- Test generation
- Scientific computing
- System administration
