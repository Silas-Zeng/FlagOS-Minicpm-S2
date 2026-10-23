# Official 16K result: team build plus the dynamic-width GQA decode kernel

Server `baseline/20261022T170500Z-gqa-fixed`, plugin branch `cjj/on-team-base`
at `b71e585`, started with `VLLM_DISABLE_COMPILE_CACHE=1
VLLM_FL_BIV150_DECODE_WARPS=1 VLLM_FL_BIV150_GQA_DECODE=1`. Driver and protocol
unchanged: `benchmark_throughput_serve.py`, case `[16384,1024,64,128]`, RUNS=4,
SKIP_FIRST=1. This is the first official 16K measurement taken on this instance.

## Per run

| run | total tok/s | mean TTFT ms | mean TPOT ms | duration s |
|---|---|---|---|---|
| 1 (discarded) | 3252.40 | 160123.39 | 138.59 | 685.10 |
| 2 | 3364.23 | 155375.69 | 133.37 | 662.33 |
| 3 | 3364.10 | 155376.20 | 133.37 | 662.35 |
| 4 | 3363.77 | 155403.23 | 133.38 | 662.42 |

Official score (runs 2-4): **3364.03 total tok/s**, mean TTFT 155385.04 ms, mean
TPOT 133.37 ms. The three scored runs agree to 0.01 %.

## Standing

- Against the teammate's official 16K on his instance, 2729.07: **+23.3 %**.
- Against my own warm probe ladder on this instance: the pre-kernel combined build
  measured 2542.46 and the team build 2588.09, so the decode kernel is worth about
  +24.9 % on 16K, consistent with the +23.3 % against his official number.
- **No official 16K baseline exists for this instance yet.** The 4K baseline here
  (1878.47) matched the teammate's within 0.15 %, so the instances are comparable,
  but any "x% over baseline" claim for 16K still needs the baseline run itself,
  which is about four runs of 1100 s, roughly 75 minutes on an idle device.

## Latency observation worth flagging

Mean TTFT is 155.4 s and mean TPOT 133.4 ms on this case, versus 60.3 ms on 4K.
128 requests of 16384 tokens is 2.1 M input tokens against a GPU KV cache of about
522 k tokens, so roughly 31 requests can be resident at a time and the rest queue:
TTFT here is dominated by queueing and preemption, not by attention speed. That is
why the decode kernel gains 24 % rather than the 80 % the probe throughput ratio
might suggest, and it is the reason KV capacity, not attention, is the next big
lever on this case.
