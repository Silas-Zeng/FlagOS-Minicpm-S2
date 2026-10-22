<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T083031Z-sql-decode-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #45 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：SQL+C2 source073309；short screen only no new accuracy or official performance
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T083031Z-sql-decode-context16k",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T08:30:31.812762+00:00",
  "profile_id": "sql_reflection+C2",
  "phase": "context-16k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "",
  "status": "completed_short_context_screen",
  "artifacts": "experiments/framework/20261021T083031Z-sql-decode-context16k",
  "conclusion": "SQL+C2 source073309; exit0;32 completed0failed;16384input128output c64 seed721201;524288input4096outputtokens;131.73937312606722s/4010.8282547721406total tok/s;medianITL394.592467462644ms;13 sourcehashes/SERVER/packages same as073309;contextdriver b7891958;SQL/C2 install and capture FIRST_SELECTED;KV521840;DB479tables17982rows to481tables18052rows with2tables70rows added and local entities SHA verified;later sequential pair can have warmer configuration state;CPU1565periods4throttles13.903549083s cumulative throttled time;postflight08:34:54.607214UTC68MiB0percent portclosed no processes;short screen only no new accuracy or official performance;SQL+C2 prior073644101/105pass retained;commit is manifest base plus hashes; later083455 starts from this after-cache and hasKV521936 versus521840;singlepair+9.173040percent throughput/-8.402294percent duration is DB/KV-confounded not attributed mixed gain"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T083031Z-sql-decode-context16k](../../../experiments/framework/20261021T083031Z-sql-decode-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T083031Z-sql-decode-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T083031Z-sql-decode-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261021T083031Z-sql-decode-context16k-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T083031Z-sql-decode-context16k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T083031Z-sql-decode-context16k/manifest.json)；[postflight.json](../../../experiments/framework/20261021T083031Z-sql-decode-context16k/postflight.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261021-163402.json](../../../experiments/framework/20261021T083031Z-sql-decode-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261021-163402.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T083031Z-sql-decode-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261021T083031Z-sql-decode-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261021T083031Z-sql-decode-context16k/exit-code)
- 相关说明：[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
