# Experiments

Each experiment must retain:

- a unique UTC timestamp and experiment identifier;
- source revisions and environment fingerprint;
- exact launch command and benchmark command;
- original CSV and service/benchmark logs;
- profiler trace or trace location and hash;
- correctness and accuracy checks;
- repeat count, exclusions, and failure explanations;
- a one-paragraph conclusion tied to measured evidence.

The authoritative raw experiment directory on the device is
`/workspace/experiments/minicpm-s2/`. This repository stores summaries and the
small evidence required to reconstruct each result.
