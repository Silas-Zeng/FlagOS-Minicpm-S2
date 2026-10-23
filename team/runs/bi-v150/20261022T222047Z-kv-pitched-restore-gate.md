<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T222047Z-kv-pitched-restore-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #178 · KV 二维 FULL 恢复

- **尝试**：保留原页序、私有页资格和完成事件，合并H2D提交；独立单层字节门与真实42层事务分开记录，调用数下降不当作性能收益。
- **改动**：相关实现 [README.md](../../../archive/ai/20261022-framework-kv/q-gqa-kv-restore-pitch/README.md)；[kv-pitched-restore-method.json](../../../analysis/kv-pitched-restore-method.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：RNG
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T222047Z-kv-pitched-restore-gate",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T22:20:47+00:00",
  "profile_id": "kv_restore_pitched",
  "phase": "one_layer_H2D_correctness",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "passed_single_layer_bytes_no_performance",
  "artifacts": "experiments/framework/20261022T222047Z-kv-pitched-restore-gate",
  "conclusion": "独立新H2D桥f9bf8757在真实1043目的页上通过单层字节/gap/guard/非零offset/同流consumer真事件/RNG；66→14提交（4linear+10pitched）、17088512B、fallback0。新方向SDK编译与实际libcudart身份已核；原controller 88seal原件、DB544不变、idle。只证明单层搬运，不是42层事务/模型准确率或性能收益。详analysis/kv-pitched-restore-method.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T222047Z-kv-pitched-restore-gate](../../../experiments/framework/20261022T222047Z-kv-pitched-restore-gate)
- 原命令：[launch-command.json](../../../experiments/framework/20261022T222047Z-kv-pitched-restore-gate-control/launch-command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T222047Z-kv-pitched-restore-gate/manifest.json)；[source-sha256.json](../../../experiments/framework/20261022T222047Z-kv-pitched-restore-gate-control/source-sha256.json)；[postflight.json](../../../experiments/framework/20261022T222047Z-kv-pitched-restore-gate-control/postflight.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T222047Z-kv-pitched-restore-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T222047Z-kv-pitched-restore-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T222047Z-kv-pitched-restore-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T222047Z-kv-pitched-restore-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
