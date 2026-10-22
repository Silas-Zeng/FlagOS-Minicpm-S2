<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T185023Z-mapped-decode-sme-fix-timing

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #89 · 非前缀 decode 映射

- **尝试**：单层构造、服务实际命中与重复结果分开记录。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wall14.344921375→12.435507453125ms省13.31073118%，event14.216219902039→12.401883125305ms省12.76244170%
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T185023Z-mapped-decode-sme-fix-timing",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T18:50:24.083607+00:00",
  "profile_id": "mapped_decode_sme_fix_timing",
  "phase": "isolated_gpu_layer_timing_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_synthetic_layer_signal_not_service",
  "artifacts": "experiments/framework/20261021T185023Z-mapped-decode-sme-fix-timing",
  "conclusion": "独立17源SHA/四case各13checks全true；32call ABBA构造D29/P2019（非服务实测几何）wall14.344921375→12.435507453125ms省13.31073118%，event14.216219902039→12.401883125305ms省12.76244170%；方法含actual build+forward，非模型/graph/服务accuracy；18:50:46.006097Z exit0/68MiB0/端口free无GPU进程；后继185627服务无正信号，层收益不得外推。"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T185023Z-mapped-decode-sme-fix-timing](../../../experiments/framework/20261021T185023Z-mapped-decode-sme-fix-timing)
- 原命令：[command.txt](../../../experiments/framework/20261021T185023Z-mapped-decode-sme-fix-timing-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T185023Z-mapped-decode-sme-fix-timing-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T185023Z-mapped-decode-sme-fix-timing/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T185023Z-mapped-decode-sme-fix-timing/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T185023Z-mapped-decode-sme-fix-timing/worker.log)；[gpu.csv](../../../experiments/framework/20261021T185023Z-mapped-decode-sme-fix-timing/gpu.csv)；[exit-code](../../../experiments/framework/20261021T185023Z-mapped-decode-sme-fix-timing/exit-code)
- 相关说明：[2026-10-22-c3-coverage-and-metadata](../../../analysis/2026-10-22-c3-coverage-and-metadata.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
