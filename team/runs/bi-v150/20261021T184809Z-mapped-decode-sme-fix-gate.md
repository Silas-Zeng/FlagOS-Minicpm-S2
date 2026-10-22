<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T184809Z-mapped-decode-sme-fix-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #88 · 非前缀 decode 映射

- **尝试**：单层构造、服务实际命中与重复结果分开记录。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：四case各13checks全true/nextdecode及crossstream-capture回退原件
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T184809Z-mapped-decode-sme-fix-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T18:48:09.949616+00:00",
  "profile_id": "mapped_decode_sme_fix",
  "phase": "isolated_gpu_correctness_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_four_case_layer_gate_not_accuracy",
  "artifacts": "experiments/framework/20261021T184809Z-mapped-decode-sme-fix-gate",
  "conclusion": "独立仅读17源SHA/四case各13checks全true/nextdecode及crossstream-capture回退原件；ede451/d085/919e/72713；修正编译选项传播后实际writer/整KV/独立oracle bits/FP32三行通过，非原C3 bits相同/非模型accuracy；无timing，18:48:35.930127Z exit0/68MiB0/端口free无GPU进程；框架owner负责算法互审，不重复GPU。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T184809Z-mapped-decode-sme-fix-gate](../../../experiments/framework/20261021T184809Z-mapped-decode-sme-fix-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T184809Z-mapped-decode-sme-fix-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T184809Z-mapped-decode-sme-fix-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T184809Z-mapped-decode-sme-fix-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T184809Z-mapped-decode-sme-fix-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T184809Z-mapped-decode-sme-fix-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261021T184809Z-mapped-decode-sme-fix-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T184809Z-mapped-decode-sme-fix-gate/exit-code)
- 相关说明：[2026-10-22-c3-coverage-and-metadata](../../../analysis/2026-10-22-c3-coverage-and-metadata.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
