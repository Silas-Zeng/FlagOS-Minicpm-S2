<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T055026341574Z-gqa-two-page-t32-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #304 · GQA两页T32计算块

- **尝试**：验证本条所述固定形状和新增实现。
- **改动**：改动及精确命令见该run源码和manifest/command原件。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-two-page-t32.md)。
- **怎么测**：复用真实生产ABI/原数值门，新增改动单独验证；不重复旧测试。
- **结果**：page16/split/reducer不变，计算tile T32/w1/s1；8类数值、FP64抽样、换值Graph/输入/RNG均过。完整producer+reducer Event 1.279242→1.829472ms，慢43.01%；SGPR spill0→84、VGPR93→136、shared8→16KiB。停止，不扩形状或进模型；不能把循环减半当净收益。sour
- **是否保留**：不扩形状、不进模型；寄存器spill反证保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T055026341574Z-gqa-two-page-t32-hotspot-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T05:50:26.341574+00:00",
  "profile_id": "gqa-two-page-t32",
  "phase": "GQA两页T32真实热点组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_t32_component_negative",
  "artifacts": "experiments/framework/20261026T055026341574Z-gqa-two-page-t32-hotspot-component",
  "conclusion": "page16/split/reducer不变，计算tile T32/w1/s1；8类数值、FP64抽样、换值Graph/输入/RNG均过。完整producer+reducer Event 1.279242→1.829472ms，慢43.01%；SGPR spill0→84、VGPR93→136、shared8→16KiB。停止，不扩形状或进模型；不能把循环减半当净收益。source/native/DB/清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T055026341574Z-gqa-two-page-t32-hotspot-component](../../../experiments/framework/20261026T055026341574Z-gqa-two-page-t32-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T055026341574Z-gqa-two-page-t32-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261026T055026341574Z-gqa-two-page-t32-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T055026341574Z-gqa-two-page-t32-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T055026341574Z-gqa-two-page-t32-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T055026341574Z-gqa-two-page-t32-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
