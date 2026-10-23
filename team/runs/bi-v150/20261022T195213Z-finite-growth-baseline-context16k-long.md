<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T195213Z-finite-growth-baseline-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #167 · 有限窗口增长准入

- **尝试**：真实服务消除本轮抢占，但共同DB对照仍有KV容量失配；默认关闭保留研究证据，不宣称确定收益。

两轮原 bc51 smoke 仅作启动显存诊断：共同 observer 下，finite 的非 Torch 内存多 4 MiB，差异在 before_profile 已存在；KV 为 baseline 521936、finite 521840，与旧性能对照方向相反。四端 DB 均为 532 表、19839 行且三项 SHA 一致；文本及 32 个 token ID 相同，但未覆盖 mixed Q/GQA 命中，不算准确率或性能收益。停止追查启动差异，旧性能对照仍因 KV 容量失配而不能归因。
- **改动**：相关实现 [finite-growth-common-db-service-pair.json](../../../analysis/finite-growth-common-db-service-pair.json)；[finite-growth-warm-service-pair.json](../../../analysis/finite-growth-warm-service-pair.json)；[finite-growth-service-pair.json](../../../analysis/finite-growth-service-pair.json)；[current-kv-memory-smokes.json](../../../analysis/current-kv-memory-smokes.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：TPS+1.000545%不能归因，收益null
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T195213Z-finite-growth-baseline-context16k-long",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T19:52:14.390553+00:00",
  "profile_id": "finite_growth_admission",
  "phase": "real_service_baseline_context16k_long",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_common_DB_baseline_KV_confounded",
  "artifacts": "experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long",
  "conclusion": "原定唯一共同新DB的Q+GQA414未改调度基线，原参数32成功0失败；169.815742162s、3280.355478tok/s，KV521840、抢占0→1。532表19839行三SHA与warm候选四端相同；24项仅KV与候选521936不匹配，表观候选TPS+1.000545%不能归因，收益null。保留baseline及候选机制证据，默认off，不放宽KV门、不为凑KV重跑、不新增accuracy。原metrics窗口194.200528s，exporter进程CPU10.45s；共享cgroup nr_throttled增4/throttled_time增19.832774220s，非Engine独占wall损失。root逐470seal、退出0和68MiB/0/双栈closed后态验收复用，不重跑validator。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T195213Z-finite-growth-baseline-context16k-long](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-035621.json](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-035621.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T195213Z-finite-growth-baseline-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
