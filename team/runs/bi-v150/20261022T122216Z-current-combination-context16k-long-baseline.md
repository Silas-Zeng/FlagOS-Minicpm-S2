<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T122216Z-current-combination-context16k-long-baseline

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #138 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：性能分析诊断；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：输出/32请求/c64，32成功0失败，219.973985s、总2532.372182 tok/s、输出148.963070 tok/s、TTFT62352.5218ms
- **是否保留**：保留作对照基线；不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T122216Z-current-combination-context16k-long-baseline",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T12:22:18.138102+00:00",
  "profile_id": "current_combination_long_baseline",
  "phase": "unprofiled_context16k_long_baseline",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_baseline",
  "artifacts": "experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline",
  "conclusion": "干净6f组合无profiler长输出基线，原服务参数/seed721201；16K输入/1024输出/32请求/c64，32成功0失败，219.973985s、总2532.372182 tok/s、输出148.963070 tok/s、TTFT62352.5218ms。KV521936，抢占0→1；DB前后527表19608行一致，412源码未变，451封存原件逐项核验、设备已清理。仅当前长负载参考，不与不同DB/诊断条件直接算收益；关停告警原样保存，下一步结合容量评估GPU热点与调度方案。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T122216Z-current-combination-context16k-long-baseline](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline/launch-command.json)；[command.txt](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-202715.json](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-202715.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline/server.log)；[gpu.csv](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline/gpu.csv)；[exit-code](../../../experiments/framework/20261022T122216Z-current-combination-context16k-long-baseline/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
