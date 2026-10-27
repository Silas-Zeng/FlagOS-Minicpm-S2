<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T103846792930Z-lm-head-temperature-r32-bn256-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #370 · LM-head温度epilogue融合

- **尝试**：新8d1a同源原官方4K/16K各四轮，暖均5971.44/4529.79 tok/s，对各自A观察+1.1634%/+0.0710%；两档KV不同，非严格因果或稳定收益，不定新基线。原105为103/105 valid/pass，但head32/64和Q32未覆盖，分支准确率未证。旧31094098与局部组件结果另列，不相加。

同融合基线上的R32 BN256扩展已完成：十门过，但完整ABBA Event慢2.6150%、wall快5.7801%，按nonpositive停止，不影响原BN64融合生产结果。

时间相近原A已补：4K暖均5923.116667、KV548288与8d1a B一致，B观察+0.8158%；两A漂移+0.3447%。支持小收益代码PR，保留波动/105分支覆盖/16K容量差异限制，不定稳定基线。
- **改动**：相关实现 [archive-receipt.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)；[comparison.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/archive-receipt.json)；[coverage-summary.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/coverage-summary.json)；[accuracy-review.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/accuracy-review.json)；[archive-receipt.json](../../../experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/comparison.json)；[archive-receipt.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/archive-receipt.json)；[comparison.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/comparison.json)；[archive-receipt.json](../../../experiments/official/20261027T105243Z-main56-control-4k-four-rounds/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实W＋合成hidden，完整eager ABBA；shared12→36KiB、regs21→37/spill0，无节流，73原件。
- **结果**：R32 BN256完整链Event慢2.6150%，wall快5.7801%；十门和资源门通过。
- **是否保留**：停止BN256，不扫参、不进模型；不取第一B当收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T103846792930Z-lm-head-temperature-r32-bn256-component",
  "local_date": "2026-10-27",
  "utc_start": "20261027T103846792930Z",
  "profile_id": "lm-head-temperature",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "lm_head_temperature_r32_bn256_nonpositive",
  "artifacts": "experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component",
  "conclusion": "R32真实head W130560×2048/合成hidden，A已测温度epilogue完整Sampler链，B仅BN64→256，BM32/BK64/w8/s1不变，F.linear只作数值参考。10项三方逐位/IDs/RNG/FP64/换值Graph/side/输入与资源门通过。唯一完整eager ABBA含分配及CPU：Event 2.342242837→2.403492689ms（耗时+2.615009%），wall 2.832578750→2.668851812ms（-5.780137%）；首个B较快但第二B反向，按完整汇总nonpositive_stop，不取单B当收益。shared12288→36864B、regs21→37，两臂spill0，无CPU节流/新增持久权重；资源变化不当因果或occupancy证明。停止BN256，不扫参/进模型/建代码PR，不改变8d1a当前生产与其官方成绩。原DB恢复、源码/native不变及清理通过，73份原件逐SHA归档。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T103846792930Z-lm-head-temperature-r32-bn256-component](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/worker.log)；[gpu.csv](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/gpu.csv)；[exit-code](../../../experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
