<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T191131Z-mapped-decode-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #92 · 非前缀 decode 映射

- **尝试**：单层构造、服务实际命中与重复结果分开记录。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：32成功0失败/524288in4096out/117.028659570962s/4514.996599440720total/TTFT59836.11785736866ms/KV521840；对干净基线KV仍差96，未accuracy默认
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T191131Z-mapped-decode-context16k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T19:11:33.184999+00:00",
  "profile_id": "sql_mixed_mapped_decode_repeat",
  "phase": "short_context16k_service_repeat",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_repeat_positive_after_negative_both_retained",
  "artifacts": "experiments/framework/20261021T191131Z-mapped-decode-context16k",
  "conclusion": "独立414源SHA，其中413文件与185627相同，仅包装innovation-source.json时间/argv/output不同；bc51/原SERVER/seed721201/CPU6/32GiB；32成功0失败/524288in4096out/117.028659570962s/4514.996599440720total/TTFT59836.11785736866ms/KV521840；DBbeforeafter实体3SHA同51619270且等首轮/preempt0→0，Engine210483首次真实D15非全程；首轮121.790163836s、本轮117.028659571s并列不择优，不归因cold或coverage；对干净基线KV仍差96，未accuracy默认；post2026-10-21T19:15:44.582675+00:0068MiB0双栈闭无GPU进程；详systems-independent-service-review.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T191131Z-mapped-decode-context16k](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261022-031445.json](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261022-031445.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261021T191131Z-mapped-decode-context16k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
