# Compute ceiling on BI-V150: bf16 is saturated, int8 is 2.3x

`scripts/bench_gemm_ceiling.py`, measured 2026-10-22 19:49 on the serving instance
(idle server holding memory, no other GPU work).

## bf16 through the vendor GEMM

| case | time | throughput |
|---|---|---|
| square 4096^3 | 1.45 ms | 94.7 TFLOP/s |
| square 8192^3 | 11.39 ms | 96.5 TFLOP/s |
| qkv_proj m8192 k2048 n2560 | 0.93 ms | 91.9 TFLOP/s |
| o_proj m8192 k2048 n2048 | 0.75 ms | 91.8 TFLOP/s |
| gate_up_proj m8192 k2048 n12288 | 4.58 ms | 90.0 TFLOP/s |
| down_proj m8192 k6144 n2048 | 2.15 ms | 96.1 TFLOP/s |
| lm_head m8192 k2048 n130560 | 48.05 ms | 91.2 TFLOP/s |

The real per-layer prefill shapes run at 90 to 96 TFLOP/s against a square-matrix
peak of about 96 TFLOP/s, i.e. **94 to 100 percent of the machine's bf16 ceiling**.
There is no meaningful headroom left in GEMM scheduling, tiling, layout or backend
choice on this device: the vendor library is already delivering peak on exactly the
shapes the model uses.

Cross-check with the serving numbers: the official 4K run processes 1,048,576 prefill
tokens in about 267 s, which is 3.97 GFLOP per token, i.e. roughly 15.6 TFLOP/s
end to end. The difference against 92 TFLOP/s of pure GEMM is attention, norms,
scheduling and memory work, which is exactly where the decode kernel gained 33 %.

## int8 exists and is 2.31x faster

`torch._int_mm` at m8192, k2048, n12288 completes on this device in 1.85 ms, which is
**223 TOP/s** against 90 TFLOP/s for the same bf16 shape. It is not a paper option; the
integer path is present, callable, and faster by a factor of 2.31.

## What this means for the roadmap

Prefill is 94 percent of the tokens in the 16K case and its linear layers are at the
bf16 hardware ceiling, so no further kernel work on the linear path can pay. The only
route to a large remaining gain is fewer bits per multiply:

1. A self-developed W8A8 path, which the rules permit because it is real implementation
   work rather than turning on a quantization flag: offline per-output-channel weight
   scales, per-token dynamic activation scales routed through `_int_mm`, and a
   scale-times-accumulated-int32 epilogue. Measured ceiling is about 2.3x on the linear
   part, which for the 16K case is most of the runtime.
2. The risk is accuracy, not speed. The current build sits at 0.9714 with a 0.95 gate, so
   about 2.1 points of margin. Before any serving integration, the quantization scheme has
   to be simulated offline (quantize-dequantize the weights and activations in fp32 and
   compare greedy continuations and Level-3 answers against the bf16 model) because that
   costs no device time and answers the go/no-go question directly.
3. Decode-time gains from int8 weights are much smaller: `lm_head` at batch 64 reads 535 MB
   per step at 553 GB/s, so halving those bytes is worth roughly 0.5 ms of a 48 ms step.
   The prize is prefill, and therefore the 16K case.

## Consistency with the earlier negative result

The int8 KV-cache probe came out 1.58x slower, and that is not in contradiction with
this. Decode attention at 513 GB/s is limited by issue and per-step work rather than by
KV bytes, so removing bytes buys nothing there. The GEMM path is the opposite case: it is
genuinely at the arithmetic ceiling, so removing bits is exactly what works.
