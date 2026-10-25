<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #278 · GQA四页T64计算块

- **尝试**：以固定w4检验T64资源压力能否缓解。
- **改动**：仅将T64候选num_warps固定4；实际mma仍[4,1]而非N方向[1,4]，不把warp数量等同成功布局变化。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-four-page-t64.md)。
- **怎么测**：N33/B40/S16、KV16K/page16，四页T64固定num_warps=4与原生产GQA+reducer；原8类边界、独立FP64及Graph ABBA，未改原数值合同。
- **结果**：8类数值/Graph/FP64门通过；Event1.278072→2.105123ms慢64.7108%，wall慢64.3265%；SGPR spill92/shared32K。
- **是否保留**：明确负，不进入4K或模型；原IR供CPU布局分析，不授官方/105资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T15:29:40.014266+00:00",
  "profile_id": "gqa-four-page-t64",
  "phase": "GQA四页T64固定w4组件对照",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_four_page_t64_w4_negative",
  "artifacts": "experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component",
  "conclusion": "T64固定num_warps=4补测，检验更多warp能否缓解原T64资源压力；N33/B40/S16、KV16K，原reducer保留。8类数值/Graph/FP64抽样门通过。Graph ABBA Event1.278072→2.105123ms慢64.7108%，wall1.284125→2.110157ms慢64.3265%。候选VGPR113、SGPR104/SGPR spill92/shared32K，实际mma布局仍[4,1]而非期望[1,4]，不能称实现N方向分摊；actual occupancy未测。15:30:11 clean exit0、source/native未变、DB恢复、9031free/free32700MiB。明确负，停止，不进入4K或模型测试；不授官方或105资格，原IR留给CPU布局分析。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component](../../../experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
