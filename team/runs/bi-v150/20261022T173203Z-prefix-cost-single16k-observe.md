<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T173203Z-prefix-cost-single16k-observe

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #153 · 公共前缀扫描

- **尝试**：在实际不支持cascade的后端中检查公共前缀统计成本；观察诊断与跳过扫描的真实服务结果分开记录。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 128 / 1 / 1。
- **结果**：1成功0失败
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T173203Z-prefix-cost-single16k-observe",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T17:32:05.239722+00:00",
  "profile_id": "no_cascade_prefix_cost",
  "phase": "single_request_cpu_cost_observation",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "1",
  "num_prompts": "1",
  "profiler": "false",
  "status": "complete_diagnostic_valid",
  "artifacts": "experiments/framework/20261022T173203Z-prefix-cost-single16k-observe",
  "conclusion": "固定clean6f，原服务与原负载脚本，单请求16K/128out/c1；仅观察无cascade的公共前缀扫描，1成功0失败。实际ARMED、128次N1快照累计CPU10.453319ms/wall10.696291ms；32→128的96次平均CPU107.610052us/wall109.497646us。快照含smoke及客户端试请求，不代表完整负载；相邻clock开销在内，不换算吞吐收益。保留省死扫描的小项依据，下一最短skip服务对照。413源/DB前后三SHA一致、460原件逐seal核验；关闭阶段EngineDeadError保留，设备68MiB/0及9031关闭。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T173203Z-prefix-cost-single16k-observe](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe/launch-command.json)；[command.txt](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe-control/source-sha256.json)
- 原始结果：[prefix-single16k-infqps-concurrency1-minicpm-20261023-013327.json](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe/prefix-single16k/results/prefix-single16k-infqps-concurrency1-minicpm-20261023-013327.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe/server.log)；[gpu.csv](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe/gpu.csv)；[exit-code](../../../experiments/framework/20261022T173203Z-prefix-cost-single16k-observe/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
