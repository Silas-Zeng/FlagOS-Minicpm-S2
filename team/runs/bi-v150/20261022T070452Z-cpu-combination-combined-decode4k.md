<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T070452Z-cpu-combination-combined-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #120 · CPU metadata + async token 组合

- **尝试**：两种CPU准备方法的组合；方法正确性与短服务性能分别记录。
- **改动**：相关实现 [model_runner.py](../../../docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py)；[biv150_cpu_metadata.py](../../../patches/framework/biv150_cpu_metadata.py)；[biv150_async_token_update.py](../../../patches/framework/biv150_async_token_update.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：TPS+0.6986430312pct、耗时省0.6937958747pct即0.2721474s、TTFT-0.1250025609pct，仅单轮短筛信号非稳定因果/官方或accuracy，不相加单项收益/不继承103-105
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T070452Z-cpu-combination-combined-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T07:04:54.111695+00:00",
  "profile_id": "CPU_combination_short_pair_combined",
  "phase": "decode4k_single_pair_screen",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_matched_single_pair_combined_small_positive_signal",
  "artifacts": "experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k",
  "conclusion": "唯一配对后验89da4cbe：451seal/412源，仅runner6f918+metadata0e961-async1bb85相对410基点三差分，原bc51SERVER-decode-seed721201/64-0/262144in8192out/38.95371279399842s/6939.928972358459total/TTFT20063.802888413193ms/KV521936/CPU6-32GiB/preempt0-0，Engine273944两FIRST_SELECTED真命中非全步计数。与070004同KV/DB四端52319474三SHA全同/包与installed依赖及原命令一致：TPS+0.6986430312pct、耗时省0.6937958747pct即0.2721474s、TTFT-0.1250025609pct，仅单轮短筛信号非稳定因果/官方或accuracy，不相加单项收益/不继承103-105。07:06:52Zexit0，07:07:32Z68-0双栈闭无GPU进程/源live同；controllerZ。测量完成后abort-forcekill阶段有8条ERROR组成EngineDeadError尾栈和资源warning，均保留，不写无ERROR或测量失败；不自动复跑/大测。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T070452Z-cpu-combination-combined-decode4k](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-150647.json](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-150647.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k/exit-code)
- 相关说明：[2026-10-22-cpu-combination-screen-result](../../../analysis/2026-10-22-cpu-combination-screen-result.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
