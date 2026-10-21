# Attention 后端假设登记

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

> 历史记录：以下事实、假设和实验计划按当时证据保留；最新结论以项目工作记录为准。

## 已验证的代码事实

基线所用的官方 `vllm-plugin-FL` commit 同时包含：

- 默认返回的通用 vLLM Triton Attention 路径；
- 由 `VLLM_FL_USE_FLAGGEMS_ATTN` 控制的可选 FlagGems FlashAttention-2 适配器，默认值为 `"0"`。

相关源码：

- `vllm_fl/dispatch/backends/flaggems/flaggems.py`
- `vllm_fl/dispatch/backends/flaggems/impl/attention.py`
- `vllm_fl/dispatch/backends/vendor/iluvatar/iluvatar.py`

基线服务没有打印启用 FlagGems 后端的消息，源码默认值也为禁用。因此，基线未使用已有的 FlagGems FlashAttention-2 适配器。

已安装的 FlagGems 包设置了 `use_c_extension=False`，所以可选的 FlagGems 路径使用纯 Triton `flash_varlen_fwd_kernel`，不使用 C++ 扩展。PyTorch 报告该设备实例有 16 个 SM 和 16 MiB L2。

当时 Iluvatar 的启发式配置如下：

| 逻辑 tile | BLOCK_M | BLOCK_N | warps | stages |
|---|---:|---:|---:|---:|
| `mha_block_16` | 16 | 32 | 4 | 3 |
| `mha_block_32` | 32 | 32 | 4 | 3 |
| `mha_block_64` | 64 | 32 | 4 | 3 |
| `mha_block_128` | 128 | 32 | 4 | 3 |

对于 16 个 query head、2 个 KV head 的单 token decode，FlagGems 将八个 query group 换到序列维度。所得最大 query 长度为八，而启发式选择 16 行 tile。因此，微基准也测试 8 行 tile，并比较 32、64 和 128 的 block size。

默认 paged-cache block size 为 16。16K 上下文因此需要每序列 1,024 个页表项。原计划比较 16、32 和 64 的 cache block size；更小的页表可能降低 decode 开销，但只有端到端服务仍然正确且可重复地更快才保留。

## 假设

通用 Triton Attention 路径是以下两项开销的重要来源：

- 较长的 16K prefill/TTFT 尾部，公开 TianShu 均值为 599 秒；
- 4K decode 尾部，本地平均 TPOT 约为 160-173 ms。

这尚非测得的根因。将完整差距归因于该路径之前，必须通过 profiler trace 量化通用 Attention kernel 的占比。

## 原实验顺序

1. 对未修改的基线做 profiling，按 prefill 和 decode 聚合 kernel。
2. 在同一服务条件下，对 FlagGems FA2 tile 候选做微基准。
3. 仅为诊断对比启用已有的 FlagGems 路径。
4. 若有收益，在 FlagGems 中加入实际的 BI-V150 专用 kernel/配置优化，并通过提交代码启用优化路径，不新增最终服务环境变量。
5. 验证输出一致性、重复性能、TTFT 和官方精度评测。

## 首轮微基准矩阵

| 阶段 | Batch | 序列长度 | Cache block size | 目的 |
|---|---:|---:|---:|---|
| Prefill | 8 | 4096 | 16, 32, 64 | 匹配约 32K 的 query token 总量 |
| Prefill | 2 | 16384 | 16, 32, 64 | query token 总量相同，上下文为 4x |
| Decode | 64 | 4096 | 16, 32, 64 | 官方 4K 的活跃并发 |
| Decode | 32 | 16384 | 16, 32, 64 | 接近实测 KV 容量限制下的活跃请求数 |

## 合规边界

只通过环境变量从通用后端切到已有的 FlagGems 后端，不足以作为最终提交。比赛禁止未优化算子就切换算子。最终改动必须包含可审计的 FlagGems 实现或 kernel 调优，以及相对已有算子的消融对比。

## 外部证据

一个相关公开项目报告了同样的默认禁用路径，并提出相同的验证顺序：

- <https://github.com/SOLECA794/minicpm5-2b-infer-opt-flagos>

该项目明确将其性能归因标为 `PLAUSIBLE`，尚未证明。这里只把它作为线索。
