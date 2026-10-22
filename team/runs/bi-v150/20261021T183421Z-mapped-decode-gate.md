<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T183421Z-mapped-decode-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #86 · 非前缀 decode 映射

- **尝试**：单层构造、服务实际命中与重复结果分开记录。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：18:34:44.773036Z完成/post68MiB0%无GPU进程/9031free
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T183421Z-mapped-decode-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T18:34:21.645775+00:00",
  "profile_id": "mapped_decode_nonprefix",
  "phase": "isolated_gpu_correctness_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "compile_binding_failed_no_case_results",
  "artifacts": "experiments/framework/20261021T183421Z-mapped-decode-gate",
  "conclusion": "独立17源SHA/c2ded9 gate/7bf4 policy/0433transform/67a9derived核实；exit1/cases[]/timingfalse，首derived skip2D JIT add_accelerate_matmul(pm,use_sme68954357763)被backend binding拒绝，尚无数学正确性或性能结果；原backend wrappers恢复true；18:34:44.773036Z完成/post68MiB0%无GPU进程/9031free；根因需审实际compiler-option hook，不提前归算法错误/全过；详independent-gate-review.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T183421Z-mapped-decode-gate](../../../experiments/framework/20261021T183421Z-mapped-decode-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T183421Z-mapped-decode-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T183421Z-mapped-decode-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T183421Z-mapped-decode-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T183421Z-mapped-decode-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T183421Z-mapped-decode-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261021T183421Z-mapped-decode-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T183421Z-mapped-decode-gate/exit-code)
- 相关说明：[2026-10-22-c3-coverage-and-metadata](../../../analysis/2026-10-22-c3-coverage-and-metadata.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
