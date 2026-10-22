<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T224411Z-kv-observed-pair-capacity-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #107 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：TPS+0.060305656%/duration省0.060269311%/TTFT+0.207191537%仅小信号，两组分层不混算
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T224411Z-kv-observed-pair-capacity-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T22:44:13.879379+00:00",
  "profile_id": "kv_observed_pair_capacity_repeat_verify0",
  "phase": "short_context16k_long_capacity_repeat_reference",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_A2_observed_capacity_reference_two_pairs_closed",
  "artifacts": "experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long",
  "conclusion": "本agent唯一c0实际exit0/pass，report e52a572e/validator c0c80dcf，未重复入口或旧suite；418/39fb/同6a/67e4-616-31cc/e155/fc937-d768/原bc51-SERVER-contextlong-seed721201/VERIFY0；32-0/524288in32768out/218.84790462488309s/2545.402483769829total/TTFT62497.66085240117ms，KV521936/CPU6/32768MiB/DB51919340三SHA89729d71ac前后同；原PID236995/profile1/int22447777996→PARENT真list/三恢复，nonTorchIncrease1000341504/available22447777996.8；真实R16704/P1044/718405632B/SAVE24run1008/目的66/ZERO-RESTORE2772/fast454/consumer8/host释放/runner6，无回读；22:50:43.051813Z418源post无变/68-0双栈闭无GPU进程，测前及shutdown ERROR均空，forcekill WARN留；与A1的KV521840/R16688不同，不混均值或套首pair值，B2 225501已唯一c0全审通过，组内条件/几何匹配，TPS+0.060305656%/duration省0.060269311%/TTFT+0.207191537%仅小信号，两组分层不混算；本项按预定收口不再重复。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T224411Z-kv-observed-pair-capacity-context16k-long](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-064908.json](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-064908.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T224411Z-kv-observed-pair-capacity-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
