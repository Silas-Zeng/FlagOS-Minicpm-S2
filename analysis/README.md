# Analysis index

This directory contains concise, audit-friendly summaries derived from raw
artifacts stored under `/workspace/experiments/minicpm-s2/`.

Rules:

- Link every conclusion to a run ID and raw log path.
- Separate unprofiled performance measurements from profiler-enabled runs.
- Never treat a single raw repetition as the official average.
- Keep CPU and device timing separate because they overlap.
- Record the experiment identifier, source revision, and profiler settings.
