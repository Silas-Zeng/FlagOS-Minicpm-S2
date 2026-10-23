<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #171 · KV 保存 / 恢复协议

- **尝试**：单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32成功0失败、诊断180.527678s不算收益；新组合不继承旧accuracy
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T21:31:34+00:00",
  "profile_id": "q_gqa_kv_swap",
  "phase": "current_combination_verify1",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "passed_current_combination_verify1_no_performance_verdict",
  "artifacts": "experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long",
  "conclusion": "当前QGQA414仅重定两runner身份锁并累加原KV保存/FULL恢复到422源；原bc51/16K+1024/32请求/c64/seed721201。VERIFY1 32成功0失败、诊断180.527678s不算收益；R16688/1043页/每方向717717504B，SAVE210、FULL2772、0ZERO，源与目的各42层字节全过，runner六checks及原consumer16通过、host释放。真实同Engine Q/GQA；KV521840、DB540/20112三SHA前后一致。原owner清理后EngineDeadError日志保留；root核490原件，reader6c5f通过。新组合不继承旧accuracy。详analysis/q-gqa-kv-swap-verify1.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-053553.json](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-053553.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
