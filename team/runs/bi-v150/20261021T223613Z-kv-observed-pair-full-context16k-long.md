<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T223613Z-kv-observed-pair-full-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #106 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：TPS+0.198765756%/duration-0.198371462%少0.434074268s/TTFT-0.215245394%，保留单次小信号不称稳定收益或纯ZERO时间/新accuracy；本项不再重复，非稳定收益
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T223613Z-kv-observed-pair-full-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T22:36:17.225018+00:00",
  "profile_id": "kv_observed_pair_full_verify0",
  "phase": "short_context16k_long_full_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_observed_full_firstpair_small_signal_two_pairs_closed",
  "artifacts": "experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long",
  "conclusion": "framework唯一c0全审4fb9b2ca与本agent独立原字段核；418/init39fb/同6a/1aff-84be-5d9a/e155/fc937-d768/bc51原SERVER-contextlong-seed721201/VERIFY0，32-0/524288in32768out/218.3848344660364s/2550.799836270839total/TTFT62338.00159151724ms；双方KV521840/CPU6/32GiB/启动非时间内存项/DB四快照51919340三SHA89729d71ac同；实际R16688/P1043/717717504B/SAVE23run966/目的66run2772/fast462/consumer16/host释放/runner6同，hardware核SAVE源与恢复目的pageIDs逐项同；FULL3ACK serial123/0ZERO/覆盖真ACK，无回读；首组TPS+0.198765756%/duration-0.198371462%少0.434074268s/TTFT-0.215245394%，保留单次小信号不称稳定收益或纯ZERO时间/新accuracy；22:42:01.143516Z418源post无变/68-0双栈闭无GPU进程，测前和shutdown ERROR均空，forcekill WARN留；唯一A2B2已按预定完成，第二组KV521936且TPS+0.060305656%/TTFT+0.207191537%，不跨层混均值；本项不再重复，非稳定收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T223613Z-kv-observed-pair-full-context16k-long](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-064111.json](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-064111.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261021T223613Z-kv-observed-pair-full-context16k-long/exit-code)
- 相关说明：[2026-10-22-kv-memory-four-mib-observation](../../../analysis/2026-10-22-kv-memory-four-mib-observation.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
