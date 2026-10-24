<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T125135Z-current-combination-context16k-long-baseline

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #142 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：性能分析诊断；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32成功0失败，219.995999768s、总2532.118768tok/s、输出148.948163tok/s、TTFT62317.2833ms
- **是否保留**：保留作对照基线；不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T125135Z-current-combination-context16k-long-baseline",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T12:51:37.147775+00:00",
  "profile_id": "current_combination_long_baseline_new_db",
  "phase": "unprofiled_context16k_long_baseline",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_baseline",
  "artifacts": "experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline",
  "conclusion": "干净6f新DB起点长输出基线，原SERVER/seed721201；32成功0失败，219.995999768s、总2532.118768tok/s、输出148.948163tok/s、TTFT62317.2833ms。实际KV521840，抢占0→1；DB527表19702行前后physical/schema/logical三SHA同，412源码，root451项evidence-seal全核复用，后态68MiB0/双栈闭。122216是旧19608行DB且KV521936，不能据两次近似耗时算配对收益；仅作为当前新起点参考，关停告警原样保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T125135Z-current-combination-context16k-long-baseline](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline/launch-command.json)；[command.txt](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-205633.json](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-205633.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline/server.log)；[gpu.csv](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline/gpu.csv)；[exit-code](../../../experiments/framework/20261022T125135Z-current-combination-context16k-long-baseline/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
