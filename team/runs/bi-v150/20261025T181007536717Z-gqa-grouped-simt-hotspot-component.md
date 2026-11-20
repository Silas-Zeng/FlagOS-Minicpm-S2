<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T181007536717Z-gqa-grouped-simt-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #285 · GQA grouped SIMT页内归约

- **尝试**：尝试避免小page16矩阵的TCU填充与布局开销。
- **改动**：QK/PV改FP32广播归约，保留P先BF16与原分页/尾mask/reducer；KV逻辑字节不减，w8增加SIMT算术和广播成本。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-grouped-simt.md)。
- **怎么测**：N33/B40/S16/KV16K/page16，baseline w1与candidate w8，原reducer不变；完整producer+reducer单ABBA，每窗16次Graph replay，关闭profiler。
- **结果**：8类原数值/FP64/Graph及实际SIMT机制通过；Event1.279744→44.634184ms（34.8774倍），wall34.6878倍。
- **是否保留**：保留明显负结果，停止整模与扫参，不推进已准备的模型入口；非数值错误，不授官方/105资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T181007536717Z-gqa-grouped-simt-hotspot-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-25T18:10:07.536717+00:00",
  "profile_id": "gqa-grouped-simt",
  "phase": "GQA grouped SIMT热点组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_grouped_simt_negative",
  "artifacts": "experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component",
  "conclusion": "从原生产GQA2596独立派生grouped SIMT：固定page16，将QK/PV改为FP32广播归约，保留P先BF16舍入与原reducer；组件candidate w8对baseline w1，N33/B40/S16/KV16K，不混cg/stride/log2。8类数值、FP64抽样、自臂换值Graph、guard/输入/RNG及实际w8/64lane无dot/MMA/无3D全局scratch机制门通过；特殊非有限输入保留原NaN模式，不称全输入finite。完整producer+reducer ABBA Event1.2797443867→44.6341838837ms（34.8774倍），wall1.2869175938→44.640352375ms（34.6878倍），明显无收益。候选VGPR83/SGPR87、两类spill0、shared16KiB，静态资源无spill不保证快。18:10:39 exit0，source/native/DB与所属进程清理通过；停止整模及参数扫描，不推进预备模型入口，不授官方/105资格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T181007536717Z-gqa-grouped-simt-hotspot-component](../../../experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
