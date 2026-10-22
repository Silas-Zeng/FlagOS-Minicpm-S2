<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T173921Z-mm-cta-group-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #75 · 矩阵乘 CTA 分组

- **尝试**：固定tile下的映射与守卫诊断；单层收益不外推服务。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：RNG true但guard_rows false
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T173921Z-mm-cta-group-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T17:39:21.428775+00:00",
  "profile_id": "fixed_tile_mm_cta_group8",
  "phase": "isolated_gpu_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "guard_correctness_rejected_pending_diagnosis",
  "artifacts": "experiments/framework/20261021T173921Z-mm-cta-group-gate",
  "conclusion": "独立11源SHA核实；policy06c7/gate4b44/原4c2e/compiled26全参数；仅gate-upM2048N12288K2048实际执行，output bits equal/finite/inputs/RNG true但guard_rows false；exit1，无timing，down未执行；不能启用、不先判kernel越界或guard误报，negative原件保留等分阶段诊断；17:39:31.434110Z完成，postixsmi68MiB0无GPU进程/9031free；后继180033定位advanced初始化即错，180646修正读法后两shape门过，旧exit1原件保持"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T173921Z-mm-cta-group-gate](../../../experiments/framework/20261021T173921Z-mm-cta-group-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T173921Z-mm-cta-group-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T173921Z-mm-cta-group-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T173921Z-mm-cta-group-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T173921Z-mm-cta-group-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T173921Z-mm-cta-group-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261021T173921Z-mm-cta-group-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T173921Z-mm-cta-group-gate/exit-code)
- 相关说明：[2026-10-22-mm-cta-group](../../../analysis/2026-10-22-mm-cta-group.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
