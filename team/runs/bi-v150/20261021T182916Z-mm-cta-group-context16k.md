<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T182916Z-mm-cta-group-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #84 · 矩阵乘 CTA 分组

- **尝试**：固定tile下的映射与守卫诊断；单层收益不外推服务。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：TPS+1.745903%但KV候选521840对基线521936，不称matched；原32/0后SIGTERM/abort forcekill时EngineDeadError保留，运行期无ERROR，未默认/accuracy
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T182916Z-mm-cta-group-context16k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T18:29:17.848157+00:00",
  "profile_id": "sql_mixed_cta_group_gateup",
  "phase": "short_context16k_service_pair",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_single_service_signal_kv_confounded",
  "artifacts": "experiments/framework/20261021T182916Z-mm-cta-group-context16k",
  "conclusion": "独立审：32成功0失败/524288in4096out/118.417526429985s/4462.042198731546total/TTFT59983.979875105433ms；真实KV521840；DBbeforeafter实体1593/a0a590/90e9同51619270不变/CPU6/32768MiB/preempt0→0，post2026-10-21T18:33:52.922664+00:0068MiB0双栈闭无GPU进程；实际FIRST在startup；首REAL_SELECTED为真实2048-token/1request单步42call，status不是全程计数。413SHA/5artifactSHA/7876/44fc/06c7，97regs0spill65536shared；仅候选绝对结果。对183543描述TPS+1.745903%但KV候选521840对基线521936，不称matched；原32/0后SIGTERM/abort forcekill时EngineDeadError保留，运行期无ERROR，未默认/accuracy；详analysis/2026-10-22-mm-cta-service-comparison.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T182916Z-mm-cta-group-context16k](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261022-023232.json](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261022-023232.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261021T182916Z-mm-cta-group-context16k/exit-code)
- 相关说明：[2026-10-22-mm-cta-compile-cache](../../../analysis/2026-10-22-mm-cta-compile-cache.md)；[2026-10-22-mm-cta-group-service](../../../analysis/2026-10-22-mm-cta-group-service.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
