<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T100830Z-cpu-combination-combined-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #123 · CPU metadata + async token 组合

- **尝试**：两种CPU准备方法的组合；方法正确性与短服务性能分别记录。
- **改动**：相关实现 [model_runner.py](../../../docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py)；[biv150_cpu_metadata.py](../../../patches/framework/biv150_cpu_metadata.py)；[biv150_async_token_update.py](../../../patches/framework/biv150_async_token_update.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：10:10:29Z exit0、后态68MiB/0%且端口闭
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T100830Z-cpu-combination-combined-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T10:08:31.449674+00:00",
  "profile_id": "CPU_combination_repeat_candidate",
  "phase": "decode4k_repeat_candidate_only",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_candidate_repeat_unpaired",
  "artifacts": "experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k",
  "conclusion": "64成功0失败；262144输入/8192输出，38.8676648s、6955.2930824 tok/s、平均TTFT19992.4129ms。源码仍为已验6f918组合，DB前后同，412源不变。10:10:29Z exit0、后态68MiB/0%且端口闭。用户随后要求直接合并已有PR，未继续反序基线；本轮无新配对收益或整模型准确率结论，原件保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T100830Z-cpu-combination-combined-decode4k](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-181023.json](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-181023.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T100830Z-cpu-combination-combined-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
