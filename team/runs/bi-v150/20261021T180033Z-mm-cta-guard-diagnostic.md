<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T180033Z-mm-cta-guard-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #81 · 矩阵乘 CTA 分组

- **尝试**：固定tile下的映射与守卫诊断；单层收益不外推服务。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：独立11源SHA/ee263/06c7/28basic文件
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T180033Z-mm-cta-guard-diagnostic",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T18:00:33.650193+00:00",
  "profile_id": "fixed_mm_cta_guard_diagnostic",
  "phase": "isolated_gpu_gate_or_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "diagnostic_complete_not_a_correctness_pass",
  "artifacts": "experiments/framework/20261021T180033Z-mm-cta-guard-diagnostic",
  "conclusion": "独立11源SHA/ee263/06c7/28basic文件；7phase两端均-15992=BF16-17且hash不变，高级读后storage不变；advanced未JIT初始化即12288错/原GPUpredicate false，真C identity/24576byte offset正常；定位旧guard读法，非correctness pass，无timing/down，旧173921原件保留；18:00:42.910097Z exit0/post68MiB0端口free无GPU进程；详本run/independent-gate-review.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T180033Z-mm-cta-guard-diagnostic](../../../experiments/framework/20261021T180033Z-mm-cta-guard-diagnostic)
- 原命令：[command.txt](../../../experiments/framework/20261021T180033Z-mm-cta-guard-diagnostic-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T180033Z-mm-cta-guard-diagnostic-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T180033Z-mm-cta-guard-diagnostic/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T180033Z-mm-cta-guard-diagnostic/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T180033Z-mm-cta-guard-diagnostic/worker.log)；[gpu.csv](../../../experiments/framework/20261021T180033Z-mm-cta-guard-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261021T180033Z-mm-cta-guard-diagnostic/exit-code)
- 相关说明：[2026-10-22-mm-cta-group](../../../analysis/2026-10-22-mm-cta-group.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
