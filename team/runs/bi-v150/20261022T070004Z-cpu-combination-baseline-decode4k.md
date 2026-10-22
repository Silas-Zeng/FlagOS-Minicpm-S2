<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T070004Z-cpu-combination-baseline-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #119 · CPU metadata + async token 组合

- **尝试**：两种CPU准备方法的组合；方法正确性与短服务性能分别记录。
- **改动**：相关实现 [model_runner.py](../../../docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py)；[biv150_cpu_metadata.py](../../../patches/framework/biv150_cpu_metadata.py)；[biv150_async_token_update.py](../../../patches/framework/biv150_async_token_update.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：39.225860193837434s/6891.780031441377total/TTFT20088.914546053275ms
- **是否保留**：保留作对照基线；不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T070004Z-cpu-combination-baseline-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T07:00:05.513586+00:00",
  "profile_id": "CPU_combination_short_pair_baseline",
  "phase": "decode4k_single_pair_screen",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_matched_single_pair_baseline",
  "artifacts": "experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k",
  "conclusion": "唯一配对后验89da4cbe：450seal/410源/0519launcher-cd506完整基点/e155/原bc51SERVER-decode-seed721201，64-0/262144in8192out/39.225860193837434s/6891.780031441377total/TTFT20088.914546053275ms/KV521936/CPU6-32GiB/preempt0-0。A前后与B前后三SHA物理dc2c-schema0dc7-logicalc05d/52319474全同，包/installed依赖及原命令一致；07:02:04Zexit0，07:02:34Z68-0双栈闭/无GPU进程，controllerZ而server-Engine消失。A无ERROR但关停forcekill/资源warning保留。组合前误比live与backup物理SHA的CPU前置exit1无run-GPU，六header字节差但逻辑同，原件保留不写DB内容变化。单轮A-B，不复用旧基点或062205性能。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T070004Z-cpu-combination-baseline-decode4k](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-150158.json](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-150158.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T070004Z-cpu-combination-baseline-decode4k/exit-code)
- 相关说明：[2026-10-22-cpu-combination-screen-result](../../../analysis/2026-10-22-cpu-combination-screen-result.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
