<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T063353Z-async-token-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #30 · 异步 token 更新

- **尝试**：整数gather/scatter更新；既有索引、stream和回退条件保留。
- **改动**：相关实现 [biv150_async_token_update.py](../../../patches/framework/biv150_async_token_update.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：Exit 0
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T063353Z-async-token-gate",
  "local_date": "2026-10-21",
  "utc_start": "2026-10-21T06:33:53.945772+00:00",
  "profile_id": "async_token_update",
  "phase": "actual_method_integer_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "integer_wrapper_gate_pass",
  "artifacts": "experiments/framework/20261021T063353Z-async-token-gate",
  "conclusion": "Exit 0; 12 actual prepare_input_ids method comparisons with stub buffers/config exact across entire storage and H2D call records; 5 invalid mappings rejected before launch; fixed-address previous rows 62/61/60 retain one identical cache entry and exact storage; caller cross-stream wait explicit; no exhaustive race or error-text equivalence claim; no weights/service/model accuracy/timing result; 7 archived source hashes match; postflight 06:34:08 UTC 68 MiB 0 percent port closed; no source commit in manifest"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T063353Z-async-token-gate](../../../experiments/framework/20261021T063353Z-async-token-gate)
- 原命令：[command.json](../../../experiments/framework/20261021T063353Z-async-token-gate/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T063353Z-async-token-gate/manifest.json)；[postflight.json](../../../experiments/framework/20261021T063353Z-async-token-gate/postflight.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T063353Z-async-token-gate/results.json)
- 日志 / 采样：[gate.log](../../../experiments/framework/20261021T063353Z-async-token-gate/gate.log)；[gpu.csv](../../../experiments/framework/20261021T063353Z-async-token-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T063353Z-async-token-gate/exit-code)
- 相关说明：[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
