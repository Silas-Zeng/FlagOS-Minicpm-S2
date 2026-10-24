<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T174712Z-no-cascade-prefix-baseline-single16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #155 · 公共前缀扫描

- **尝试**：在实际不支持cascade的后端中检查公共前缀统计成本；观察诊断与跳过扫描的真实服务结果分开记录。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 128 / 1 / 1。
- **结果**：1成功0失败
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T174712Z-no-cascade-prefix-baseline-single16k",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T17:47:14.190652+00:00",
  "profile_id": "no_cascade_prefix_skip",
  "phase": "single_request_service_baseline",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "1",
  "num_prompts": "1",
  "profiler": "false",
  "status": "complete_baseline_unmatched_kv",
  "artifacts": "experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k",
  "conclusion": "干净6f、原16K/128out/c1负载，1成功0失败；KV521936，与候选521840失配，不能形成严格性能配对，观察轮173203也不能替代性能基线。吞吐2108.943270tok/s、TTFT5263.264409ms、TPOT20.203599ms；只保存原始基线，不补大测或为小差异反复重跑。412源、DB四端527表19702行三SHA一致、459原件逐seal核验，关闭EngineDeadError保留，设备清理。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T174712Z-no-cascade-prefix-baseline-single16k](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k-control/source-sha256.json)
- 原始结果：[prefix-single16k-infqps-concurrency1-minicpm-20261023-014833.json](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k/prefix-single16k/results/prefix-single16k-infqps-concurrency1-minicpm-20261023-014833.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k/server.log)；[gpu.csv](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T174712Z-no-cascade-prefix-baseline-single16k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
