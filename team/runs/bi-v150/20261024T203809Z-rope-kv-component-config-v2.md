<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T203809Z-rope-kv-component-config-v2

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #234 · RoPE与KV写入融合

- **尝试**：修记录器后完整验证42层RoPE＋KV融合，与原combo＋KV writer对照。
- **改动**：本轮源码、版本与原始结果见下方证据；方法边界见[方法记录](../../methods/rope-kv-fusion.md)。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 独立组件；非模型请求。
- **结果**：42层字节/guard/变输入Graph通过；M2048/32/64 Graph总wall约5.070→4.791、0.899→0.864、0.982→0.896ms，仅局部组件。
- **是否保留**：保留正信号供模型接线，模型准确率/端到端尚待。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T203809Z-rope-kv-component-config-v2",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T20:38:09Z",
  "profile_id": "rope-kv-fusion",
  "phase": "rope_kv_component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "独立组件；非模型请求",
  "profiler": "false",
  "status": "rope_component_positive_signal",
  "artifacts": "experiments/framework/20261024T203809Z-rope-kv-component-config-v2",
  "conclusion": "RoPE→KV v2独立42层组件完成，M/actual为2048/2018、32/32、64/63；Q/K逐bit、全部KV/guard/未选页、负slot/padding、V原输入及两次变输入Graph均通过。含CPU metadata/prepare的Graph总wall中位分别5.070314→4.791159、0.898830→0.863847、0.981573→0.896179ms；eager三shape也改善。20:38:27 UTC清理/source检查通过。合成激活、固定各case actual_rows与M、两臂重新热编译；未证明实际模型Graph接线、完整105或端到端收益。保留局部正信号供独立模型候选，原首次失败保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T203809Z-rope-kv-component-config-v2](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/worker.log)；[gpu.csv](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/gpu.csv)；[exit-code](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
