# Metrics

HeliosBench records system-level metrics during each run so output is comparable across
binary versions and task types.

## Tracked metrics

- Latency: mean, median, and standard deviation
- Memory: RSS mean and max in MB
- CPU: mean and max percentage
- File descriptors: mean and max
- Threads: mean and max

## How to read the results

- Rising RSS across repeated runs is a leak signal.
- Rising FD counts are a separate leak signal.
- CPU and thread growth often point to work amplification or concurrency regressions.

## Typical uses

- Compare one build against another
- Catch leaks before a release
- Track benchmark regressions in CI
- Produce JSON for downstream analysis
