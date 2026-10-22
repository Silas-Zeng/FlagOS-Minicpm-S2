# 天数 BI-V150 算子线：int8 决策测量

本轮目标是回答“bf16 算术已到设备上限（88–96 TFLOP/s，方矩阵峰值实测 96.5），int8 到底能不能拿分”。结论是：能拿分的形式只有一种，另一类看起来最自然的做法在本设备是负的。原始数据在 [`experiments/operator/`](../experiments/operator) 的 `int8_decision` 登记行，脚本在实验仓库 `scripts/bench_int8_gemm_shapes.py`、`scripts/bench_w8a16_decode_gemm.py`、`scripts/bench_int_mm_epilogue.py`、`scripts/w8a8_risk.py`、`scripts/w8a8_sweep.py`。

## 已排除

- **Triton int8 GEMM**：FlagGems `scaled_mm` 在该 vendor 走通用回退（`flag_gems/ops/scaled_mm.py`，nvidia 默认 64³/4 warp 配置，无 iluvatar 覆盖），在合并形状的 M=2048 / M=8192 只有 bf16 的 0.5185–0.7020x，即 46.25–63.53 TOP/s；同一 kernel 在 M=64 却达 0.8689–2.0536x（其中 k_proj 0.873、v_proj 0.869、lm_head 0.968 仍低于 1）。自写同类 kernel 也因 `tl.dot` 在该后端对 int8 tile 的编译限制未能跑通；这条路不值得继续。
- **`torch._int_mm` + torch 反量化链**：0.32–1.04x。原因不在 GEMM 而在 epilogue——int32→fp32、物化 `[M,1]x[1,N]` 的 fp32 scale 乘积、再加 bias，等于对 `[M,N]` 多走三遍。q_proj M=2048 的 GEMM 部分约 0.08 ms，整链测得 0.425 ms（bf16 为 0.195 ms）。
- **W8A16（int8 权重 + bf16 数学）**：自写 Triton kernel 测两种权重布局。`[N,K]` 列读（不合并）16 个形状各取 8 个配置里最快者，ratio 0.2007–0.6092、权重带宽 1.1–128.5 GB/s（m=2048 为 0.20–0.25，qkv 0.2531；m=8192 稳定 0.21；maxdiff 0.0391–0.0547）；改成 `[K,N]` 双向合并反而更差，0.2079–0.4180、36.2–79.0 GB/s，且那一版只测到 m=128。瓶颈是内循环逐元素 int8→bf16 加宽而不是地址模式：两版都远低于 `lm_head` 的 553 GB/s 锚点（analysis/2026-10-22-int8-kv-probe.md，同文 int8 KV 慢 1.58x）。**该设备上进 tensor core 的数据必须一路 int8，任何逐元素转换都亏。**

## 成立的形式

三 kernel 链：Triton per-token 对称量化 → `torch._int_mm`（193–255 TOP/s）→ 自写融合 dequant+bias（一次 int32 读、一次 bf16 写）。合并形状实测：

| M | qkv | o | gate_up | down | lm_head |
|---|---|---|---|---|---|
| 64 | 1.103x | 0.877x | 1.604x | 1.135x | 1.523x |
| 2048 | 1.412x | 1.224x | 1.493x | 1.543x | 1.523x |
| 8192 | 1.178x | 1.246x | 1.504x | 1.614x | 未测（输出张量尺寸保护） |

小 M 的收益本质是字节减半：`_int_mm` 只在 m>=2048 达到 193–255 TOP/s，m=64/128 只有 27.3–112.4 TOP/s。量化与反量化各只有一次启动且含 eager Python 开销，进 CUDA graph 后 decode 侧还应改善。按此建模：16K 的 prefill 每 8192-token chunk 的线性部分从 8.51 ms 降到 6.66 ms（保留 down_proj 时），4K 的 decode 每步省约 1.8 ms。

## 精度侧

真实 checkpoint 的 294 个线性层做 QDQ（fp32 量化-反量化、bf16 矩阵乘，比 int32 累加保守），24 道 Level-3 greedy、1024 token、单次加载逐臂还原权重：

| 方案 | gold/24 | 最终答案一致率 |
|---|---|---|
| 只量化权重（per-channel） | 13 | 95.8%（1 题翻转） |
| W8A8 per-channel + per-token | 11 | 87.5%（3 题翻转） |
| W8A8 权重分组 128 | 12 | 91.7% |
| W8A8 权重分组 64 | 11 | 87.5% |
| W8A8 去掉 down_proj | 13 | **95.8%（1 题翻转）** |
| W8A8 只量化 MLP | 13 | **95.8%（1 题翻转）** |

三点方法学结论：损伤来自**激活量化**，不是权重粒度（分组更细不更好）；**困惑度筛不出来**——所有 int8 方案的 teacher-forcing PPL 都在 bf16 的 ±0.15% 内，而同一方案能改动 12.5% 的 greedy 答案；per-projection 排序能定位敏感层（`down_proj` 最差 +0.354%，去掉它反而 -0.529%），与生成侧一致。

## 当前状态

按上面的组合实现了自研 W8A8 补丁 `vllm_fl/patches/biv150_w8a8_linear.py`（框架库分支 `codex/biv150-w8a8-linear`，提交 `b9840d883358a3e745e6c136592c8c2063cbe05c`）：在 `process_weights_after_loading` 里把 bf16 权重对称量化成 per-channel int8 并 `replace_parameter` 释放原显存，`apply` 跑三 kernel；默认层集 `qkv_proj,o_proj,gate_up_proj`，`down_proj` 与 `lm_head` 保持 bf16。不读 checkpoint 的量化配置、不改官方服务参数，`VLLM_FL_BIV150_W8A8` 未开启时完全不生效。

未闭环：端到端两轮对照、官方 Level-3、以及 CUDA graph 捕获下 `_int_mm` 的可用性验证。这些跑完之前不进入合并讨论，也不按微测外推收益。
