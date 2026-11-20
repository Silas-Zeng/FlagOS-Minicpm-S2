<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T061316901168Z-gqa-sme-span-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #312 · GQA同storage二维span

- **尝试**：核二维span是否降低原page16传输成本。
- **改动**：同storage二维视图与行单位地址，原reducer不变。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-sme-span.md)。
- **怎么测**：N33/B40/S16、KV16K，8类数值/Graph/FP64适用门与完整producer+reducer Graph ABBA。
- **结果**：GQA同storage二维backing-span及行单位寻址，N33/B40/S16、KV16K；8类数值/Graph/别名及适用FP64门通过，mask15→63但不证明SMEcopy实际启用。完整producer＋原reducer Graph Event1.277690→1.282553ms慢0.3806%，wall慢0.3994%；view创建在Graph计时外。负结果
- **是否保留**：停止，不扩形状或进模型；mask不当实际传输证明。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T061316901168Z-gqa-sme-span-hotspot-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T06:13:16.901168+00:00",
  "profile_id": "gqa-sme-span",
  "phase": "GQA同storage二维span传输组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_sme_span_negative_component",
  "artifacts": "experiments/framework/20261026T061316901168Z-gqa-sme-span-hotspot-component",
  "conclusion": "GQA同storage二维backing-span及行单位寻址，N33/B40/S16、KV16K；8类数值/Graph/别名及适用FP64门通过，mask15→63但不证明SMEcopy实际启用。完整producer＋原reducer Graph Event1.277690→1.282553ms慢0.3806%，wall慢0.3994%；view创建在Graph计时外。负结果停止，不扩形状或接生产；DB/source/native和清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T061316901168Z-gqa-sme-span-hotspot-component](../../../experiments/framework/20261026T061316901168Z-gqa-sme-span-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T061316901168Z-gqa-sme-span-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T061316901168Z-gqa-sme-span-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T061316901168Z-gqa-sme-span-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T061316901168Z-gqa-sme-span-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T061316901168Z-gqa-sme-span-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
