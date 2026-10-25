<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T090542870699Z-gqa-identity-rescale-v2-b32-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #255 · GQA恒等rescale跳过

- **尝试**：仅当同组8头的finite最大值严格不变时省去rescale，其他分支与原reducer保留。N33/B40/S16及B32/S4分别完成8组数值/Graph检查，Graph ABBA耗时观察分别+2.308%/+1.058%；未见收益，不推进模型/官方。B32首次空padding验证器异常单列，独立v3修验证器后重测，未修改候选数学。均为随机输入组件，非实际激活重放。
- **改动**：相关实现 [kernel.diff](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/kernel.diff)；[worker.py](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/worker.py)；[padding-source.json](../../../experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/padding-source.json)；[worker.diff](../../../experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/source/worker.diff)；本轮准确变体以原件源码清单为准。
- **怎么测**：实际生产GQA＋reducer的B32/S4组件；首组padding检查异常，未执行完整Graph ABBA。
- **结果**：B32无padding，验证器空切片.all()触发ZeroDivisionError；完整数值检查和计时未形成，不判候选数值失败。
- **是否保留**：保留验证器失败；独立v3只修空padding检查，后继结果另列。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T090542870699Z-gqa-identity-rescale-v2-b32-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T09:05:42.870699+00:00",
  "profile_id": "gqa-identity-rescale",
  "phase": "GQA B32/S4组件验证器诊断",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_padding_checker_failed",
  "artifacts": "experiments/framework/20261025T090542870699Z-gqa-identity-rescale-v2-b32-component",
  "conclusion": "B32/S4无padding，验证器对active:B空切片调用FlagGems.all()触发ZeroDivisionError；完整checks与计时尚未形成，不能判候选数值失败或性能回退。原exit1、源/IR/traceback保留。独立v3只在active<B执行padding检查，数学candidate7bc22不变；后继结果单列，不覆盖本次失败。源码/native未变、DB恢复及清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T090542870699Z-gqa-identity-rescale-v2-b32-component](../../../experiments/framework/20261025T090542870699Z-gqa-identity-rescale-v2-b32-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T090542870699Z-gqa-identity-rescale-v2-b32-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T090542870699Z-gqa-identity-rescale-v2-b32-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T090542870699Z-gqa-identity-rescale-v2-b32-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T090542870699Z-gqa-identity-rescale-v2-b32-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T090542870699Z-gqa-identity-rescale-v2-b32-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
