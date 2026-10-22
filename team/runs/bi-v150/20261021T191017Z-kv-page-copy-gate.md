<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T191017Z-kv-page-copy-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #91 · KV 连续页复制

- **尝试**：连续页合并提交工具；提交不是完成ACK，工具与服务协议分开看。
- **改动**：相关实现 [biv150_kv_page_copy.py](../../../patches/framework/biv150_kv_page_copy.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：16384 / 未记录 / 未记录 / 未记录。
- **结果**：遮蔽stdlib copy触发dataclasses循环，尚未import torch/初始化复制
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T191017Z-kv-page-copy-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T19:10:17.749540+00:00",
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
  "status": "archive_import_shadow_failed_before_gpu_copy",
  "artifacts": "experiments/framework/20261021T191017Z-kv-page-copy-gate",
  "conclusion": "独立8源SHA/d841/c95f/1219/a351核实；exit1/cases[]，policy加载时source/copy.py遮蔽stdlib copy触发dataclasses循环，尚未import torch/初始化复制；无字节正确性/事件/成本结果，不归算术失败；原件与worker traceback保留；19:11:31.638525Z owner完整68MiB0双栈闭无GPU进程、worker退出controller仅Z；最小新93eb仅四归档/hash/load名改biv150_kv_page_copy.py，policy不改；CPU真实source新进程旧fail新pass及hardware定向互审通过，待新run。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T191017Z-kv-page-copy-gate](../../../experiments/framework/20261021T191017Z-kv-page-copy-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T191017Z-kv-page-copy-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T191017Z-kv-page-copy-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T191017Z-kv-page-copy-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T191017Z-kv-page-copy-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T191017Z-kv-page-copy-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261021T191017Z-kv-page-copy-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T191017Z-kv-page-copy-gate/exit-code)
- 相关说明：[2026-10-22-framework-milestone](../../../analysis/2026-10-22-framework-milestone.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
