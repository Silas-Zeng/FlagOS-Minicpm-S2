<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T191545Z-kv-page-copy-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #93 · KV 连续页复制

- **尝试**：连续页合并提交工具；提交不是完成ACK，工具与服务协议分开看。
- **改动**：相关实现 [biv150_kv_page_copy.py](../../../patches/framework/biv150_kv_page_copy.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：16384 / 未记录 / 未记录 / 未记录。
- **结果**：失败保留，详independent-gate-review.json和analysis/2026-10-22-kv-page-copy-result.json
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T191545Z-kv-page-copy-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T19:15:46.038755+00:00",
  "profile_id": "kv_page_copy_cost",
  "phase": "isolated_gpu_copy_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_four_case_byte_event_pass_single_cost_samples",
  "artifacts": "experiments/framework/20261021T191545Z-kv-page-copy-gate",
  "conclusion": "独立8源SHA/93eb/c95f/1219/a351/exit0；normal42与packed42各contiguous和fragmented8四case，8pass×5checks/RNG4均true，42actual factory view/guard/未选poison；每向704643072B，normal42或336copy/packed1或8；timed roundtrip wall依次222.053105/235.270289/119.956194/120.716930ms，方向event和wall差大，CPUquota/host提交混杂未知，不称稳定DMA带宽或E2E；构造布局非服务observed，无模型/协议/accuracy；19:18:05.738516Z完整68MiB0双栈闭无GPU进程；191017原导入失败保留，详independent-gate-review.json和analysis/2026-10-22-kv-page-copy-result.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T191545Z-kv-page-copy-gate](../../../experiments/framework/20261021T191545Z-kv-page-copy-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T191545Z-kv-page-copy-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T191545Z-kv-page-copy-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T191545Z-kv-page-copy-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T191545Z-kv-page-copy-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T191545Z-kv-page-copy-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261021T191545Z-kv-page-copy-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T191545Z-kv-page-copy-gate/exit-code)
- 相关说明：[2026-10-22-kv-page-copy-gate](../../../analysis/2026-10-22-kv-page-copy-gate.md)；[2026-10-22-framework-milestone](../../../analysis/2026-10-22-framework-milestone.md)；[2026-10-22-scheduler-kv-innovation](../../../analysis/2026-10-22-scheduler-kv-innovation.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
