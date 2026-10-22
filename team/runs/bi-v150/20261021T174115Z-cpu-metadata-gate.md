<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T174115Z-cpu-metadata-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #76 · CPU metadata 复用

- **尝试**：复用已计算的CPU视图，写回原GPU缓冲区；回退和事件边界见原报告。
- **改动**：相关实现 [biv150_cpu_metadata.py](../../../patches/framework/biv150_cpu_metadata.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wallABBA原0.712748078125到0.65646540625ms省7.89657294%约56.282672us，仅method fixture非E2E/服务/accuracy
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T174115Z-cpu-metadata-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T17:41:15.531420+00:00",
  "profile_id": "cpu_metadata_exact_methods",
  "phase": "isolated_gpu_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "exact_method_gate_pass_independent_review",
  "artifacts": "experiments/framework/20261021T174115Z-cpu-metadata-gate",
  "conclusion": "独立10源SHA核实；b124/0e9615/0096/e155到50493；decode62/M259/M952/M2048/纯prefill2048五fixture各11checks全true，连续4次原event保护+固定地址graph消费/非陈旧验证通过，selected75/RNG timing不变/strictscope回退；32call方法wallABBA原0.712748078125到0.65646540625ms省7.89657294%约56.282672us，仅method fixture非E2E/服务/accuracy；17:41:34.453023Z exit0/postixsmi68MiB0无GPU进程/9031free"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T174115Z-cpu-metadata-gate](../../../experiments/framework/20261021T174115Z-cpu-metadata-gate)
- 原命令：[command.txt](../../../experiments/framework/20261021T174115Z-cpu-metadata-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T174115Z-cpu-metadata-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T174115Z-cpu-metadata-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261021T174115Z-cpu-metadata-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261021T174115Z-cpu-metadata-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261021T174115Z-cpu-metadata-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261021T174115Z-cpu-metadata-gate/exit-code)
- 相关说明：[2026-10-22-c3-coverage-and-metadata](../../../analysis/2026-10-22-c3-coverage-and-metadata.md)；[2026-10-22-cpu-combination-framework-review](../../../analysis/2026-10-22-cpu-combination-framework-review.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
