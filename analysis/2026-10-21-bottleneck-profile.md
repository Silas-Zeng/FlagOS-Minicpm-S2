# 首轮 profiler 分析

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

> 历史记录：本文反映最初基线的诊断窗口，不能当作后续优化服务的瓶颈占比。

这些 trace 是诊断测量，wall time 包含 profiler 开销，不作为性能分数。

## 4K 稳态 decode

实验：`b0-triton-4k-decode`

Trace 包含四个采样 decode 迭代。原生 profiler 报告：

| Kernel / 操作 | GPU 耗时 | 可见 runtime kernel 占比 |
|---|---:|---:|
| `_topk_topp_kernel` | 21.204 ms | 71.68% |
| LM-head `linear_kernel` | 4.434 ms | 14.99% |
| `true_div_func_kernel_rank_2` | 1.272 ms | 4.30% |
| `true_div_func_kernel_rank_1` | 0.703 ms | 2.38% |
| softmax | 0.651 ms | 2.20% |
| Gumbel/exponential noise | 0.367 ms | 1.24% |
| argmax | 0.338 ms | 1.14% |
| bf16-to-fp32 copy | 0.346 ms | 1.17% |

可见 kernel 总计 29.58 ms。Transformer graph 本体通过捕获的 CUDA graph 执行，因此大部分模型层 kernel 在该 trace 中不显示为独立 runtime event。不过，对 post-logits 路径的结论明确：top-p 过滤主导可见设备工作量。

形状数据表明每个 decode step 有 57-59 行、词表为 130,560。过滤 kernel 进行多次全词表二分遍历，由此形成具体候选：采用遍历次数有界的 histogram/zoom 或阈值算法，融合或替换 top-p 过滤与 sampler 尾部。

Profiler 插桩会放大 CPU 耗时，不将其视为模型延迟。Trace 仅用于调用计数和相对设备工作量分析。

## 16K 预填充

实验：`b0-triton-16k-prefill`

五个诊断 engine 迭代产生 948 个 kernel event，总设备耗时为 3.720 秒：

| Kernel / 操作 | GPU 耗时 | 占比 |
|---|---:|---:|
| `vllm::unified_attention_with_output` (`kernel_unified_attention`) | 3.4585 s | **92.96%** |
| `aten::mm` (`mm_kernel`) | 224.64 ms | 6.04% |
| Fused SiLU/multiply/slice | 11.54 ms | 0.31% |
| Fused residual RMSNorm | 6.83 ms | 0.18% |
| KV-cache reshape/write | 2.54 ms | 0.07% |

该 prefill chunk 含 2048 个 query token、16 个 query head、2 个 KV head，head size 为 128。通用 Attention kernel 几乎占据整个设备时间线。这是将 16K prefill Attention 作为首要优化目标的直接证据，而非仅凭静态代码作出的假设。

更早的 engine 时间线还显示，32 GiB cache 约能容纳 30 条并行的 16K 序列。任何改变 cache 容量的候选都必须在相同有效并发下比较。

## 选定的 kernel 调优

GPU 上同形状的 paged FlashAttention 微基准结果：

- 类似 4K 的 decode（`batch=64`、`seq_len=4096`、GQA 16Q/2KV/head128）：
  - 原始启发式 BM16/BN32/w4/s3：约 2.092 ms；
  - 调优后 BM8/BN32/w4/s1：约 1.092 ms；
  - 4K cache block size 16、64、128 对结果的影响小于 2%。
- 2048-token 预填充分块：
  - 原始 BM128/BN32/w4/s3：约 2.658 ms；
  - 调优后 BM128/BN64/w8/s1：约 1.078 ms。

所有已测候选的输出均为有限值，在随机 BF16 Attention 上相对参考配置的最大差异约为 `0.0039`。精确 GQA8 16Q/2KV GPU 测试套件也通过全部 14 项测试。

这些收益仅为 kernel 级结果。只有比较相同服务负载，才能证明端到端收益。
