# Team and experiment protocol

## Scope

This repository records the FlagOS Season 2 Track 2 work for MiniCPM5-2B.
Existing GitHub repositories are read-only references. Never push to or modify
them. Publish only to a newly created repository dedicated to this experiment.

## Device ownership

- The current FlagOS instance exposes one BI-V150 accelerator. Only one
  GPU-active experiment may run at a time.
- CPU-only source reading, test preparation, documentation, and log analysis
  may proceed concurrently.
- The owner of a running device job is responsible for its PID, output
  directory, and clean shutdown.
- Never start a second `vllm serve`, benchmark, profiler, or GPU microbenchmark
  while port 9031 or the accelerator is active unless the experiment explicitly
  requires both and has sufficient memory.

## Collaboration split

- Framework/end-to-end owner: scheduling, execution graph, metadata, buffers,
  host/device interaction, and official benchmark integrity.
- Kernel/KV owner: operator implementations, Attention/KV access, fusion,
  tiling, correctness tests, and kernel microbenchmarks.
- Raw official measurements remain owned by the framework/end-to-end owner.
- Every optimization patch is reviewed by the other owner before final
  integration.

## Evidence requirements

- Every experiment has a unique UTC run ID and a directory under
  `/workspace/experiments/minicpm-s2/`.
- Preserve source revisions, environment fingerprint, exact commands, original
  CSV/logs, GPU samples, failures, and the conclusion.
- Never place profiler-enabled runs in the official performance baseline
  directory.
- Never compare two results produced with different launch arguments, source
  revisions, device-memory sizes, or concurrent host workloads.
- Record negative results. They are required for the experiment report and
  prevent duplicated work.

## Competition compliance

- Use only MiniCPM5-2B.
- Preserve the official benchmark script and serving arguments.
- Do not enable quantization or speculation by changing hyperparameters.
- A switched operator requires an actual implementation change; do not merely
  route to an existing alternative.
- Do not merge a newer framework branch for performance.
- Final optimizations must be enabled by submitted code and pass the accuracy
  and reproducibility gates.

## Secret handling

- Never commit SSH private keys, API keys, cookies, tokens, or raw credential
  manager output.
- Connection notes may contain the public gateway and username only when
  necessary for reproducibility, but not private keys or passwords.
