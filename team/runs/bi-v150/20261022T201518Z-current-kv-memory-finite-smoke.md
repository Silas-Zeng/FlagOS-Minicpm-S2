<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T201518Z-current-kv-memory-finite-smoke

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #169 · 有限窗口增长准入

- **尝试**：真实服务消除本轮抢占，但共同DB对照仍有KV容量失配；默认关闭保留研究证据，不宣称确定收益。

两轮原 bc51 smoke 仅作启动显存诊断：共同 observer 下，finite 的非 Torch 内存多 4 MiB，差异在 before_profile 已存在；KV 为 baseline 521936、finite 521840，与旧性能对照方向相反。四端 DB 均为 532 表、19839 行且三项 SHA 一致；文本及 32 个 token ID 相同，但未覆盖 mixed Q/GQA 命中，不算准确率或性能收益。停止追查启动差异，旧性能对照仍因 KV 容量失配而不能归因。
- **改动**：相关实现 [finite-growth-common-db-service-pair.json](../../../analysis/finite-growth-common-db-service-pair.json)；[finite-growth-warm-service-pair.json](../../../analysis/finite-growth-warm-service-pair.json)；[finite-growth-service-pair.json](../../../analysis/finite-growth-service-pair.json)；[current-kv-memory-smokes.json](../../../analysis/current-kv-memory-smokes.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：启动或描述符诊断；输入 / 输出 / 并发 / 请求数：8 / 32 / 1 / 1。
- **结果**：原 bc51 smoke 启动显存诊断，非性能轮；文本及32个token ID相同，未覆盖mixed Q/GQA命中，不算accuracy/收益
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T201518Z-current-kv-memory-finite-smoke",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T20:15:19.602806+00:00",
  "profile_id": "finite_growth_admission",
  "phase": "startup_memory_finite_smoke",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "8",
  "output_len": "32",
  "concurrency": "1",
  "num_prompts": "1",
  "profiler": "false",
  "status": "complete_startup_memory_diagnostic_no_performance_verdict",
  "artifacts": "experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke",
  "conclusion": "原 bc51 smoke 启动显存诊断，非性能轮；finite加共同 observer，共416源文件，退出0且严格idle；源差异限init/helper接线。较baseline非Torch内存多4MiB，在before_profile已存在，available KV bytes少4194304，KV521840比baseline少96，与旧性能pair方向相反。四端DB同532表19839行且三SHA一致；文本及32个token ID相同，未覆盖mixed Q/GQA命中，不算accuracy/收益。停止追启动，旧perf仍KVconfounded，不回填历史因果。root逐464seal核验复用；详见analysis/current-kv-memory-smokes.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T201518Z-current-kv-memory-finite-smoke](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke)
- 原命令：[launch-command.json](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke/launch-command.json)；[command.json](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke-control/command.json)；[command.txt](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke-control/source-sha256.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke/server.log)；[gpu.csv](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke/gpu.csv)；[exit-code](../../../experiments/framework/20261022T201518Z-current-kv-memory-finite-smoke/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
