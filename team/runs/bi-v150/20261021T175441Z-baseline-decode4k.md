<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T175441Z-baseline-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #80 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：post2026-10-21T17:58:40.426636+00:0068MiB0%双栈闭无GPU进程，owned退出或Z
- **是否保留**：保留作对照基线；不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T175441Z-baseline-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T17:54:42.213747+00:00",
  "profile_id": "sql_mixed_baseline",
  "phase": "short_decode4k_independent_pair",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_matched_short_control_independent_review",
  "artifacts": "experiments/framework/20261021T175441Z-baseline-decode4k",
  "conclusion": "独立stdlib核完整410源SHA/bc51/0813/原SERVER/seed721201/CPU6/BI-V15032768MiB；64成功0失败/262144in8192out；39.185280642007s/6898.917031366118total/TTFT20076.045600762882ms；实际KV521936；前后DB实体physical1593/schemaa0a590/logical90e9同516表19270行不变，4runinstalled身份同；preempt0到0；post2026-10-21T17:58:40.426636+00:0068MiB0%双栈闭无GPU进程，owned退出或Z；A2基线供metadata同KV521936配对；与A1容量不同，不称matched漂移/官方成绩；可复算analysis/2026-10-22-small-framework-comparison.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T175441Z-baseline-decode4k](../../../experiments/framework/20261021T175441Z-baseline-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T175441Z-baseline-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T175441Z-baseline-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261021T175441Z-baseline-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T175441Z-baseline-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T175441Z-baseline-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T175441Z-baseline-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T175441Z-baseline-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T175441Z-baseline-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-015634.json](../../../experiments/framework/20261021T175441Z-baseline-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-015634.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T175441Z-baseline-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261021T175441Z-baseline-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261021T175441Z-baseline-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
