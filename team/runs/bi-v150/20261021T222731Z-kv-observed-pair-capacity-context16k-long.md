<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T222731Z-kv-observed-pair-capacity-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #105 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：FULL223613已齐，双方KV/组成/DB/几何同，首pair描述小信号+0.198765756%TPS；非稳定收益或独立ZERO计时
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T222731Z-kv-observed-pair-capacity-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T22:27:33.783337+00:00",
  "profile_id": "kv_observed_pair_capacity_verify0",
  "phase": "short_context16k_long_capacity_reference",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_observed_capacity_reference_firstpair_small_signal",
  "artifacts": "experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long",
  "conclusion": "framework唯一c0入口全审通过/report ece929ae；本agent只独立读原raw/选定角色源/真实events/DB字节与post，不重跑同入口或套件；418/init39fb/同6a/67e4-616-31cc/e155/fc937-d768/bc51原SERVER-contextlong-seed721201/VERIFY0；32-0/524288in32768out/218.81890873378143s/2545.7397773504263total/TTFT62472.47070692538ms，KV521840/CPU6/32768MiB；DBbeforeafter51919340三SHA89743b20/29d740d5/71ac1989同；实际PID233942/profile1/原int22443583692→PARENT真list/三hook恢复，profile_nonTorchIncrease1004535808/available22443583692.8，分项由hardware专项解释不补历史；R16688/P1043/717717504B/SAVE23run966/目的66/ZERO-RESTORE各2772/fast462/host释放/runner六checks/consumer16，无回读；22:33:26.459826Z418源post无变/68-0双栈闭无GPU进程，测前ERROR空，shutdown ERROR/WARN原样保留；FULL223613已齐，双方KV/组成/DB/几何同，首pair描述小信号+0.198765756%TPS；唯一A2B2已完成且组内+0.060305656%TPS，各容量层级分开不混算；非稳定收益或独立ZERO计时。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T222731Z-kv-observed-pair-capacity-context16k-long](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-063228.json](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-063228.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long/exit-code)
- 相关说明：[2026-10-22-kv-memory-four-mib-observation](../../../analysis/2026-10-22-kv-memory-four-mib-observation.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
