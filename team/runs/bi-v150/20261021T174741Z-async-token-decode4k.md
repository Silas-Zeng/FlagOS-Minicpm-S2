<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T174741Z-async-token-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #78 · 异步 token 更新

- **尝试**：整数gather/scatter更新；既有索引、stream和回退条件保留。
- **改动**：相关实现 [biv150_async_token_update.py](../../../patches/framework/biv150_async_token_update.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：post2026-10-21T17:50:48.770684+00:0068MiB0%双栈闭无GPU进程，owned退出或Z；FIRST_SELECTED，保留待确认，非稳定因果/未默认或新accuracy
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T174741Z-async-token-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T17:47:42.252630+00:00",
  "profile_id": "sql_mixed_async_token",
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
  "artifacts": "experiments/framework/20261021T174741Z-async-token-decode4k",
  "conclusion": "独立stdlib核完整411源SHA/bc51/0813/原SERVER/seed721201/CPU6/BI-V15032768MiB；64成功0失败/262144in8192out；39.134667001665s/6907.839537474561total/TTFT20126.242607628228ms；实际KV521840；前后DB实体physical1593/schemaa0a590/logical90e9同516表19270行不变，4runinstalled身份同；preempt0到0；post2026-10-21T17:50:48.770684+00:0068MiB0%双栈闭无GPU进程，owned退出或Z；对A1同KV521840/同DB单次TPS+0.7036569314%/TTFT-0.8656382386%；FIRST_SELECTED，保留待确认，非稳定因果/未默认或新accuracy；可复算analysis/2026-10-22-small-framework-comparison.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T174741Z-async-token-decode4k](../../../experiments/framework/20261021T174741Z-async-token-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T174741Z-async-token-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T174741Z-async-token-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261021T174741Z-async-token-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T174741Z-async-token-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T174741Z-async-token-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T174741Z-async-token-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T174741Z-async-token-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T174741Z-async-token-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-014934.json](../../../experiments/framework/20261021T174741Z-async-token-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-014934.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T174741Z-async-token-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261021T174741Z-async-token-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261021T174741Z-async-token-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
