<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T194020Z-finite-growth-candidate-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #165 · 有限窗口增长准入

- **尝试**：真实服务消除本轮抢占，但共同DB对照仍有KV容量失配；默认关闭保留研究证据，不宣称确定收益。

两轮原 bc51 smoke 仅作启动显存诊断：共同 observer 下，finite 的非 Torch 内存多 4 MiB，差异在 before_profile 已存在；KV 为 baseline 521936、finite 521840，与旧性能对照方向相反。四端 DB 均为 532 表、19839 行且三项 SHA 一致；文本及 32 个 token ID 相同，但未覆盖 mixed Q/GQA 命中，不算准确率或性能收益。停止追查启动差异，旧性能对照仍因 KV 容量失配而不能归因。
- **改动**：相关实现 [finite-growth-common-db-service-pair.json](../../../analysis/finite-growth-common-db-service-pair.json)；[finite-growth-warm-service-pair.json](../../../analysis/finite-growth-warm-service-pair.json)；[finite-growth-service-pair.json](../../../analysis/finite-growth-service-pair.json)；[current-kv-memory-smokes.json](../../../analysis/current-kv-memory-smokes.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32成功0失败
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T194020Z-finite-growth-candidate-context16k-long",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T19:40:22.300985+00:00",
  "profile_id": "finite_growth_admission",
  "phase": "real_service_candidate_context16k_long",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_cold_confounded_KV_DB",
  "artifacts": "experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long",
  "conclusion": "有限首完成窗口准入415源，仅init+helper8f564变化、runnercc442/Q/GQA不变，原长负载32成功0失败；175.720693616s、3170.121791tok/s、抢占0、KV521936。Engine349215首次真实defer free1664<future2559、horizon791、running30；两个operator实际成功execute证据同原比较门。DB529表19769行→532表19839行，3新表4行与3旧表新增66行，旧行typed多重集全保留。对193302因DB/KV双失配收益null，不认稳定negative；root479seal验收。无有限策略准确率，原Q/GQA准确率不自动继承。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T194020Z-finite-growth-candidate-context16k-long](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-034435.json](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-034435.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T194020Z-finite-growth-candidate-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
