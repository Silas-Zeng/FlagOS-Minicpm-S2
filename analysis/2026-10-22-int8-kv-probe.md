# int8 KV cache probe: negative, and it says the kernel is not bandwidth-bound

 scripts/bench_int8_kv.py runs the same decode attention twice from identical data:
once from a bf16 paged cache and once from an int8 cache with one symmetric scale per
(token, kv head), dequantized in registers. At batch 64, kv 4096, 2 segments:

    bf16  0.5227 ms   513.6 GB/s
    int8  0.8246 ms   325.5 GB/s effective   time ratio 0.634 (i.e. 1.58x slower)
    output difference: max 0.416, mean 0.0068 against the bf16 path on the same data

So halving the KV bytes made the kernel substantially slower. The dequantization path
costs more than the traffic it saves: per page it adds two fp32 vector loads of scales,
two multiplies over the 128x16 K tile and the 16x128 V tile, and an extra dtype
conversion each, on top of the int8 to fp32 widening. At 513 GB/s this kernel is close
to the 553 GB/s that lm_head reaches on this device, so it is no longer issue-limited
by memory alone and removing bytes does not buy time.

Two conclusions for the roadmap. First, do not pursue int8 or fp8 KV for decode
attention speed; if KV capacity is worth attacking for the 16K queueing problem, it
has to be justified by resident-request count rather than by kernel time. Second, the
remaining room in this kernel is arithmetic and issue pressure per step, not traffic:
the scale of the win already took decode attention from 283 to 513 GB/s, so further
effort should go to the per-step work (dot shapes, the fp32 to bf16 cast of P, the
accumulator rescale) rather than to loading less data.

The 16K case of this probe was not measured: the idle serving process holds most of
the device and the fp32 quantization temporaries for a 1.07 GB cache do not fit. That
does not change the conclusion, which is already 1.58x in the wrong direction at the
shape where the kernel is fastest.
