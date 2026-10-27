<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T043321686931Z-gqa-s2-incta-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #359 · S2同CTA归约

- **尝试**：首次编译失败；停止当前实现，无数值或性能结论。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T043321686931Z-gqa-s2-incta-hotspot-component/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：完整源码、命令、环境、失败日志及清理证据已回收。
- **结果**：S2两段同CTA/w2并在核内归约，拟省全局partial读写和一次启动；保持原page16、KV布局与逐段数学。实际CoreX在首个candidate的TritonGPUAccelerateMatmul阶段编译失败；checks/timings均空，未取得数值或性能结论。停止当前实现，不改编译器、门或重封包，不进入生产。main241/native14f/source2596
- **是否保留**：停止当前实现，不进生产。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T043321686931Z-gqa-s2-incta-hotspot-component",
  "local_date": "2026-10-27",
  "utc_start": "20261027T043321686931Z",
  "profile_id": "gqa-s2-incta",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "241220723a09061c182764f8f738e5ec01190367",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_s2_incta_compile_failed",
  "artifacts": "experiments/framework/20261027T043321686931Z-gqa-s2-incta-hotspot-component",
  "conclusion": "S2两段同CTA/w2并在核内归约，拟省全局partial读写和一次启动；保持原page16、KV布局与逐段数学。实际CoreX在首个candidate的TritonGPUAccelerateMatmul阶段编译失败；checks/timings均空，未取得数值或性能结论。停止当前实现，不改编译器、门或重封包，不进入生产。main241/native14f/source2596与新main56同GQA源码；DB已恢复、源码/native不变、9031空闲及GPU清理通过。全部39份原件已回收逐SHA核验。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T043321686931Z-gqa-s2-incta-hotspot-component](../../../experiments/framework/20261027T043321686931Z-gqa-s2-incta-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T043321686931Z-gqa-s2-incta-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261027T043321686931Z-gqa-s2-incta-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T043321686931Z-gqa-s2-incta-hotspot-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T043321686931Z-gqa-s2-incta-hotspot-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T043321686931Z-gqa-s2-incta-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
