<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T180646Z-mm-cta-group-cpu-guard-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #82 · 矩阵乘 CTA 分组

- **尝试**：固定tile下的映射与守卫诊断；单层收益不外推服务。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wall1.4179341875到1.188571765625ms省16.17581577%，event1.4043543934822083到1.174988865852356ms省16.33245345%；仅fixedtile fixture非E2E/accuracy/稳定收益，不同时默认
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T180646Z-mm-cta-group-cpu-guard-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T18:06:46.402328+00:00",
  "profile_id": "fixed_mm_cta_cpu_guard",
  "phase": "isolated_gpu_gate_or_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "fixed_two_shape_gate_pass_positive_and_negative_signals",
  "artifacts": "experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate",
  "conclusion": "独立11源SHA/b216/06c7/64basic文件；两shape各8phase/bits/finite/inputs/RNG及post全true，basic expected与initialSHA守卫，高级仅旁证；32callABBA gate-up wall1.4179341875到1.188571765625ms省16.17581577%，event1.4043543934822083到1.174988865852356ms省16.33245345%；down wall0.735825265625到0.763840109375ms慢3.80726853%，event0.7219997048377991到0.7500479817390442ms慢3.88480448%；仅fixedtile fixture非E2E/accuracy/稳定收益，不同时默认；18:06:56.861033Z exit0/post68MiB0端口free无GPU进程；详本run/independent-gate-review.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T180646Z-mm-cta-group-cpu-guard-gate](../../../experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate/exit-code)
- 相关说明：[2026-10-22-mm-cta-group-service](../../../analysis/2026-10-22-mm-cta-group-service.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
