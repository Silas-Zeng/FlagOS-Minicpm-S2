<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T185627Z-mapped-decode-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #90 · 非前缀 decode 映射

- **尝试**：单层构造、服务实际命中与重复结果分开记录。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：TPS−1.07166475%，基线KV521936不同，不归因单算法；post19:00:37.354668Z68MiB0双栈闭无GPU进程，未默认/新accuracy
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T185627Z-mapped-decode-context16k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T18:56:29.391763+00:00",
  "profile_id": "sql_mixed_mapped_decode",
  "phase": "short_context16k_service_screen",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_service_no_positive_signal_kv_boundary",
  "artifacts": "experiments/framework/20261021T185627Z-mapped-decode-context16k",
  "conclusion": "独立414源SHA/3566runner/d085policy/919e/72713/bc51/原SERVER/seed721201；32成功0失败/524288in4096out/121.790163835976s/4338.478439947034total/TTFT62258.128146859235ms；实际KV521840，DBbeforeafter51619270实体三SHA不变/CPU6/32768MiB/preempt0→0；Engine207423真实FIRST_SELECTED decode_requests15，首次marker非全程；相对183543描述TPS−1.07166475%，基线KV521936不同，不归因单算法；原退出ERROR按shutdown分类保留；post19:00:37.354668Z68MiB0双栈闭无GPU进程，未默认/新accuracy；详run/independent-service-review.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T185627Z-mapped-decode-context16k](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261022-025947.json](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261022-025947.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261021T185627Z-mapped-decode-context16k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
