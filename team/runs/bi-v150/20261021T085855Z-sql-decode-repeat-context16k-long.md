<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T085855Z-sql-decode-repeat-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #53 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：SQL+C2 source073309
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T085855Z-sql-decode-repeat-context16k-long",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T08:58:56.224393+00:00",
  "profile_id": "sql_reflection+C2",
  "phase": "context-16k-long-warm-repeat",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "",
  "status": "warm_control_completed_single_mixed_signal",
  "artifacts": "experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long",
  "conclusion": "SQL+C2 source073309;exit0;32completed0failed;524288input32768outputtokens;231.32209699694067s/2408.140023075129total tok/s;medianITL92.23801782354712ms;same source/SERVER/packages/driver28d6a034/seed721201;KV521840 now equal mixed085302;DBbefore=after483tables18119rows and all hashes identical mixed before-after with local entities SHA verified;known DB/KV initial confounds removed;single mixed/warm throughput+4.970763percent duration-4.735378percent and nearly unchanged medianITL;not stable/official performance or mixed accuracy;metrics09:03:34.629064UTC service num_preemptions_total1.0 once observed not final complete count or benchmark-scoped delta and no proof mixed zero;CPU2568periods4throttles14.794389534s cumulative throttled time;postflight09:05:05.260646UTC68MiB0percent portclosed no processes;commit explicit manifest base plus hashes"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T085855Z-sql-decode-repeat-context16k-long](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/manifest.json)；[postflight.json](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/postflight.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261021-170404.json](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261021-170404.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/exit-code)
- 相关说明：[2026-10-21-innovation-systems](../../../analysis/2026-10-21-innovation-systems.md)；[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
