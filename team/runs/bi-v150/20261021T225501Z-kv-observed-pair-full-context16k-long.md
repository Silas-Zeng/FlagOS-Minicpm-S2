<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T225501Z-kv-observed-pair-full-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #108 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：TPS+0.060305656%/duration省0.060269311%少0.131898123305s/TTFT+0.207191537%，均保留单次小信号
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T225501Z-kv-observed-pair-full-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T22:55:05.310847+00:00",
  "profile_id": "kv_observed_pair_full_repeat_verify0",
  "phase": "short_context16k_long_full_repeat_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_B2_observed_full_two_pairs_closed_small_signals_retained",
  "artifacts": "experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long",
  "conclusion": "本agent唯一c0 full实际exit0/pass，report62b07a8c引用A2 e52a572e；418/init39fb/同6a/1aff-84be-5d9a/e155/fc937-d768/原bc51-SERVER-contextlong-seed721201/VERIFY0；32-0/524288in32768out/218.7160065015778s/2546.937505444904total/TTFT62627.150716711185ms，KV521936/CPU6/32768MiB；A2B2启动非时间内存项/原args包installed/DB四端51919340三SHA89729d71ac同，真实PID238635/profile1/原int22447777996→父真list/三hook恢复；R16704/P1044/718405632B/source24run/SAVE1008/目的66run/FULL2772/0ZERO/fast454/consumer8/host释放/runner6，无回读；组内TPS+0.060305656%/duration省0.060269311%少0.131898123305s/TTFT+0.207191537%，均保留单次小信号；首组KV521840结果分层不合均值，不证稳定收益/纯ZERO时间/新accuracy。23:01:06.003547Z418源无变/68-0双栈闭无GPU进程，测前与shutdown ERROR皆空/forcekill WARN留；两组按预先计划结束本项重复，不追容量/择最好。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T225501Z-kv-observed-pair-full-context16k-long](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-070000.json](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-070000.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T225501Z-kv-observed-pair-full-context16k-long/exit-code)
- 相关说明：[2026-10-22-kv-observed-pair-two-pairs](../../../analysis/2026-10-22-kv-observed-pair-two-pairs.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
