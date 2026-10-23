# Official 4K result: decode kernel with dynamic split-K width, after the fix

Branch `cjj/on-team-base` head `b71e585`, server
`baseline/20261022T170500Z-gqa-fixed`, started with
`VLLM_DISABLE_COMPILE_CACHE=1 VLLM_FL_BIV150_DECODE_WARPS=1 VLLM_FL_BIV150_GQA_DECODE=1`.
Server log records `BIV150_GQA_DECODE_FIRST_WIDTH seqs=64 builder_segments=16
segments=2 target_programs=256`, and a greedy smoke check on this server returns the
same text as the validated fixed-width build.

Driver and protocol unchanged: `benchmark_throughput_serve.py`, case
`[4096,1024,64,256]`, RUNS=4, SKIP_FIRST=1.

## Per run

| run | total tok/s | mean TTFT ms | mean TPOT ms | duration s |
|---|---|---|---|---|
| 1 (discarded) | 4771.01 | 4977.60 | 61.85 | 274.73 |
| 2 | 4615.49 | 4877.41 | 64.23 | 283.98 |
| 3 | 4904.45 | 4643.76 | 60.37 | 267.25 |
| 4 | 4908.13 | 4648.09 | 60.32 | 267.05 |

Official score (runs 2-4): **4809.36 total tok/s**, mean TTFT **4723.09 ms**, mean
TPOT 61.64 ms, req/s 0.94. Runs 3 and 4 are at 4906 and show run 2 was still
settling, so the protocol average is about 2 % below steady state.

## Standing against everything measured on this instance

| build | official 4K | vs baseline | Level 3 |
|---|---|---|---|
| baseline | 1878.47 | — | 0.962 stated |
| decode w1s1 only | 2244.83 | +19.5 % | bit-exact |
| prefill/top-p + w1s1 | 3487.86 | +85.7 % | teammate 0.9810 |
| teammate build + fixed-width decode kernel | 4614.33 | +145.6 % | 0.9714 |
| **teammate build + dynamic-width decode kernel** | **4809.36** | **+156.0 %** | **0.9714** |
| teammate's own official 4K on his instance | 3683.65 | +96.1 % | 0.9810 |

Relative to the teammate's official 4K that is **+30.6 %**, and TTFT is 4723 ms
against a baseline of 12320 ms, so the TTFT ceiling has 62 % of margin. The
accuracy score is unchanged by the dynamic width, measured on the same protocol.

## Note on the previous entry in this directory tree

`baseline/20261022T082318Z-4k-official` records 4900.37 from the same configuration
**before** the reduction fix. That number is invalidated for reporting because the
build produced incoherent text (Level 3 = 0.0286); the throughput itself was
unaffected by the bug since the benchmark fixes output length with `--ignore-eos`,
which is exactly why a generation smoke check is now mandatory before quoting any
throughput number.
