<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T134407482450Z-gqa-kv-stride-main-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #272 · GQA stride常量折叠

- **尝试**：用constexpr stride减少分页地址计算的整数乘法。
- **改动**：仅5个K/V stride声明为constexpr，原缓存策略、数学与reducer保留；alternate stride校验不同值的新JIT和原Graph仍绑定正确。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-kv-stride.md)。
- **怎么测**：实际原GQA+reducer、N33/B40/S16与KV16K；只改5个stride为constexpr，不混.cg。原8组边界、额外13项换stride/图绑定与关闭profiler的Graph ABBA。
- **结果**：8组数值/Graph及alternate-stride13项通过；整数mul27→13，Event1.277992→1.278517ms，wall1.284104→1.283520ms，无净收益。
- **是否保留**：保留机制和无收益结果，收口；不扩形状或进入模型，不创建优化PR。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T134407482450Z-gqa-kv-stride-main-hotspot-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T13:44:07.482450+00:00",
  "profile_id": "gqa-kv-stride",
  "phase": "GQA stride常量组件对照",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_stride_no_net_gain",
  "artifacts": "experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component",
  "conclusion": "仅将GQA的5个K/V stride声明为constexpr，保留原cache策略、数学和reducer。N33/B40/S16、KV16K原8组数值/Graph边界与alternate-stride13项通过；总整数mul27→13、页地址关联mul12→0。Graph ABBA Event1.277992→1.278517ms（省-0.0410%），wall1.284104→1.283520ms（省+0.0454%），无可确认净收益。source/native/DB恢复及清理通过；只保留机制及负结果，不扩形状或进入模型。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T134407482450Z-gqa-kv-stride-main-hotspot-component](../../../experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
