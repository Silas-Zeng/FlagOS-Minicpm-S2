<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T130457Z-prefill-v-late-cache-v2-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #144 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wall慢0.27180%、event仅快0.02373%，不能认定收益，当前不集成；负结果不外推其他A+B
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T130457Z-prefill-v-late-cache-v2-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T13:04:58.061004+00:00",
  "profile_id": "prefill_v_late_cache",
  "phase": "actual_layer_cache_preference_isolation",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_no_wall_gain",
  "artifacts": "experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate",
  "conclusion": "修正actual spec身份后，同worker原版/A默认Vlate/B仅PREFER_SHARED三臂严格正确性通过。32次/窗的原-A-B-B-A-原中，wall原11.091868/A11.227600/B11.258116ms；B较原慢1.49883%，B对A wall慢0.27180%、event仅快0.02373%，不能认定收益，当前不集成。A/B独立module/function但同binary和资源；setter rc0只说明接受，carveout rc801不可观察，原maxdynamic均128KiB且未修改。原绑定恢复，38原件全核；负结果不外推其他A+B。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T130457Z-prefill-v-late-cache-v2-gate](../../../experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate)
- 原命令：[command.txt](../../../experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
