<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T175049Z-cpu-metadata-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #79 · CPU metadata 复用

- **尝试**：复用已计算的CPU视图，写回原GPU缓冲区；回退和事件边界见原报告。
- **改动**：相关实现 [biv150_cpu_metadata.py](../../../patches/framework/biv150_cpu_metadata.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：post2026-10-21T17:54:39.866651+00:0068MiB0%双栈闭无GPU进程，owned退出或Z
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T175049Z-cpu-metadata-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T17:50:51.116511+00:00",
  "profile_id": "sql_mixed_cpu_metadata",
  "phase": "short_decode4k_independent_pair",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "single_positive_signal_retained_not_integrated",
  "artifacts": "experiments/framework/20261021T175049Z-cpu-metadata-decode4k",
  "conclusion": "独立stdlib核完整411源SHA/bc51/0813/原SERVER/seed721201/CPU6/BI-V15032768MiB；64成功0失败/262144in8192out；39.073248478118s/6918.697843907006total/TTFT20123.110001033638ms；实际KV521936；前后DB实体physical1593/schemaa0a590/logical90e9同516表19270行不变，4runinstalled身份同；preempt0到0；post2026-10-21T17:54:39.866651+00:0068MiB0%双栈闭无GPU进程，owned退出或Z；对后继A2同KV521936/同DB单次TPS+0.2867234444%/TTFT+0.2344306304%；FIRST_SELECTED；不能对A1报约0.86%严格收益，保留待确认未默认；可复算analysis/2026-10-22-small-framework-comparison.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T175049Z-cpu-metadata-decode4k](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-015243.json](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-015243.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261021T175049Z-cpu-metadata-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
