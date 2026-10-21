# 外部证据与可迁移性

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

> 历史记录：本文区分当时的公开说法和本地复现测量；候选计划不代表当前执行安排。

## 官方与一手参考

- FlagOS 比赛页面：
  <https://flagos.io/race-detail-season2?id=539vlt2p&lang=cn>
- BI-V150 适配 PR，包含 32 GiB 设备和 CoreX 4.5.0 环境：
  <https://github.com/flagos-ai/vllm-plugin-FL/pull/310>
- 官方 operator-profile 流程：
  <https://github.com/Silas-Zeng/vllm-plugin-FL/tree/main/tools/operator_profile>
- Iluvatar BI-V150 厂商描述：
  <https://moark.com/docs/compute/clusters_gpu/iluvatar/iluvatar_BI-V150_gpu>

## 相关公开项目

<https://github.com/SOLECA794/minicpm5-2b-infer-opt-flagos>

该项目发现了相同的默认关闭 FlagGems Attention 适配器，并建议先测量再宣称性能收益。其示例优化 CSV 不是该设备上可复现的测量，不作为证据。

另一个公开 workspace 报告了具体、可独立审阅的改动：

<https://github.com/xy200303/minicpm-flagserve>

- Attention metadata cache 在其 MetaX 专用 prefill 路径中消除了重复的 pageable device-to-host copy。该 commit 声称该路径约有 10% 端到端收益，但不能将实现原样套用到 Iluvatar 的 `TRITON_ATTN`。
- 其 sampler 工作融合 top-k/top-p 过滤和 Gumbel-Max sampling。本环境的 `FlagGems v5.3.5` 不包含这些更新的融合模块，不能将其视为已有能力。
- 其 README 汇总的组织方问答称允许 shape-aware dispatch 和自主开发的 speculative 策略，但禁止自行训练 draft model。使用这些说法前，仍需向组织方直接确认。

重复 DtoH copy 模式是审查整个 Attention 路径的有用 profiling 线索，但不能证明 Iluvatar 基线也存在相同操作。

## 本地独立验证的事实

- 实例可见一张 BI-V150，容量为 32,768 MiB。
- CoreX 为 4.5.0，活跃 FlagTree Triton 版本为 3.6.0。
- 源码为官方 `flagos-2026-s2` commit `13eb9be`。
- FlagGems 为 tag `v5.3.5`、commit `4df52d91`。
- `VLLM_FL_USE_FLAGGEMS_ATTN` 默认关闭，因此基线解析到 `TRITON_ATTN`。
- 官方 FLASH_ATTN-2 适配器代码和 paged KV 实现均存在。
- 当时 32 GiB KV cache 容量为 521,936 token。每请求 16K 时，尽管客户端并发为 64，scheduler 实际约可容纳 30-31 个请求。

## 当时可迁移的候选

1. 为 BI-V150 的 16Q/2KV/head-dim 128 调优 FlagGems paged Attention kernel，并用实际优化实现替换通用路径。
2. 在保持固定服务参数的前提下，评估更大的 paged-cache block，以减少 block-table 和索引开销。
3. 对 sampling 做 profiling；尽管镜像报告 Triton 3.6.0 且 target 可用，plugin 在 Iluvatar 上禁用了 sampler compilation。
4. 只有 profile 证明端到端占比足够时，才融合 RoPE 与 KV-cache write，或研究 fused residual RMSNorm。

## 未被接纳为已证明的说法

- Attention 单独解释 BI-V150 与 C500 的全部差距。
- 在该镜像上切换到 FlagGems Attention 能改善任一负载。
- 最优 tile 就是当时的 BM8 候选。
- Block-size 或 sampler 改动能提升端到端吞吐。
- 第三方仓库中的任何合成或示例结果。
