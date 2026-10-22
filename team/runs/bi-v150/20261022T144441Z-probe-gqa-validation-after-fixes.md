<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T144441Z-probe-gqa-validation-after-fixes

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #140 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：4096 / 1024 / 64 / 64。
- **结果**：与修复前 #125 的 5058.23 / 3234.26 相比差 0.008% 与 0.06%，即  审计、batch-invariant 拒绝、seq_len==0 安全化、视图键加 stride 与 try/except 这些改动对性能与数值是中性的；本轮 GPU KV 为 521840 tokens（#125 候选为 521936），是同一构建在不同 重启下的分配抖动，两臂对照仍用各自的 marker 与 KV 数字，不外推
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T144441Z-probe-gqa-validation-after-fixes",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T14:44:41+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "warm_probe_candidate_validation_after_review_fixes",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d3844f15677ebc657f93fb52536e7c1620c7c974",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_kernel_active_performance_neutral",
  "artifacts": "experiments/operator/20261022T144441Z-probe-gqa-validation-after-fixes",
  "conclusion": "审阅修复后的复测（同一 worktree，kernel 开启、W8A8 关闭）：install marker installed True、rows 8、page_size 16、backend_rebound True，且出现 `BIV150_GQA_DECODE_FIRST_WIDTH seqs=64 builder_segments=16 segments=2 target_programs=256`，说明真实 decode 步已走本 kernel。缩放暖探针 4K（4096x1024x64x64，3 个 repeat）4638.95 / 5059.85 / 5058.63，全部中位 5058.63、TPOT 48.15 ms；16K（16384x1024x64x16）3236.25 / 3236.77、TPOT 56.33 ms。与修复前 #125 的 5058.23 / 3234.26 相比差 0.008% 与 0.06%，即 SHA 审计、batch-invariant 拒绝、seq_len==0 安全化、视图键加 stride 与 try/except 这些改动对性能与数值是中性的。本轮 GPU KV 为 521840 tokens（#125 候选为 521936），是同一构建在不同 重启下的分配抖动，两臂对照仍用各自的 marker 与 KV 数字，不外推。另一项重要发现：greedy smoke 的指纹在同一模型上跨构建不可复现——三次运行（140539Z 0.500、141457Z 0.650、本轮 0.575，40 题、temperature 0、seed 42）response_sha256 全不同。原因是连续批处理下每个请求所在 batch 的形状会变，bf16 归约顺序随之变化，贪心轨迹因此分叉；所以 scripts/greedy_parity_check.py 只能当“是否输出崩坏”的粗筛，不能当逐位一致性门，真正的精度门只有官方 math_500 Level 3。本轮 errors=0、accuracy 0.575 与截断水平一致，判定为通过粗筛。"
}
```

</details>

## 登记 #141 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 16。
- **结果**：与修复前 #125 的 5058.23 / 3234.26 相比差 0.008% 与 0.06%，即  审计、batch-invariant 拒绝、seq_len==0 安全化、视图键加 stride 与 try/except 这些改动对性能与数值是中性的；本轮 GPU KV 为 521840 tokens（#125 候选为 521936），是同一构建在不同 重启下的分配抖动，两臂对照仍用各自的 marker 与 KV 数字，不外推
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T144441Z-probe-gqa-validation-after-fixes",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T14:44:41+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "warm_probe_16k_validation_after_review_fixes",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d3844f15677ebc657f93fb52536e7c1620c7c974",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "16",
  "profiler": "false",
  "status": "complete_kernel_active_performance_neutral",
  "artifacts": "experiments/operator/20261022T144441Z-probe-gqa-validation-after-fixes",
  "conclusion": "审阅修复后的复测（同一 worktree，kernel 开启、W8A8 关闭）：install marker installed True、rows 8、page_size 16、backend_rebound True，且出现 `BIV150_GQA_DECODE_FIRST_WIDTH seqs=64 builder_segments=16 segments=2 target_programs=256`，说明真实 decode 步已走本 kernel。缩放暖探针 4K（4096x1024x64x64，3 个 repeat）4638.95 / 5059.85 / 5058.63，全部中位 5058.63、TPOT 48.15 ms；16K（16384x1024x64x16）3236.25 / 3236.77、TPOT 56.33 ms。与修复前 #125 的 5058.23 / 3234.26 相比差 0.008% 与 0.06%，即 SHA 审计、batch-invariant 拒绝、seq_len==0 安全化、视图键加 stride 与 try/except 这些改动对性能与数值是中性的。本轮 GPU KV 为 521840 tokens（#125 候选为 521936），是同一构建在不同 重启下的分配抖动，两臂对照仍用各自的 marker 与 KV 数字，不外推。另一项重要发现：greedy smoke 的指纹在同一模型上跨构建不可复现——三次运行（140539Z 0.500、141457Z 0.650、本轮 0.575，40 题、temperature 0、seed 42）response_sha256 全不同。原因是连续批处理下每个请求所在 batch 的形状会变，bf16 归约顺序随之变化，贪心轨迹因此分叉；所以 scripts/greedy_parity_check.py 只能当“是否输出崩坏”的粗筛，不能当逐位一致性门，真正的精度门只有官方 math_500 Level 3。本轮 errors=0、accuracy 0.575 与截断水平一致，判定为通过粗筛。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T144441Z-probe-gqa-validation-after-fixes](../../../experiments/operator/20261022T144441Z-probe-gqa-validation-after-fixes)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
