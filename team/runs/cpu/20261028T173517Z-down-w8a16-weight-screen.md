<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T173517Z-down-w8a16-weight-screen

平台：CPU。本页只摘录既有登记；未记录字段不补猜。

## 登记 #448 · BI-V150特定形状GEMM

- **尝试**：CPU筛查down W8A16 K128量化权重与有限合成输出误差。
- **改动**：仅CPU评估对称分组量化误差，不运行CUDA、模型或官方准确率。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：本条所列source/result/manifest原件完整打包并按SHA256分块；组件/CPU筛查与官方成绩分开。
- **结果**：CPU筛查42层真实down权重；最大weight relative L2为0.007979，门只基于有限合成输出，不代表官方准确率或吞吐；未在服务启用量化。
- **是否保留**：仅保留研究结果；未启用量化，不进入比赛候选。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T173517Z-down-w8a16-weight-screen",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T17:35:19.582412+00:00",
  "profile_id": "shape-gemm",
  "phase": "CPU screening",
  "device": "CPU",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "shape_gemm_w8a16_cpu_weight_screen",
  "artifacts": "experiments/bundles/20261028T173517Z-down-w8a16-weight-screen",
  "conclusion": "CPU筛查42层真实down权重；最大weight relative L2为0.007979，门只基于有限合成输出，不代表官方准确率或吞吐；未在服务启用量化。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T173517Z-down-w8a16-weight-screen](../../../experiments/bundles/20261028T173517Z-down-w8a16-weight-screen)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
