<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T132239Z-main0915-gqa-kv-cg-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #271 · GQA KV读取缓存策略

- **尝试**：检查16K组件局部省时能否转为原官方服务收益。
- **改动**：团队main0915完整603仅4处KV load加.cg；KV547648对547536，DB后分析作为独立原件，原failed/残留running字段不改。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-kv-cg.md)。
- **怎么测**：原0813脚本RUNS4/SKIP_FIRST1与服务参数不变；团队main0915完整603仅4处.cg，13:37:32向所属owner SIGTERM。KV547648对547536；原server.log第68/398行证实Q-hoist/compute-order拒绝，13:37:37 finished、source/native/DB/清理通过。
- **结果**：4K冷/首暖4722.73/4944.66 tok/s，首暖对同轮5751.88为−14.03%；512成功，第三轮主动中断、16K未测。
- **是否保留**：保存全部已测及停止原件；旧候选Q-hoist/compute-order未启用而原main已启用，属优化组合不完整的混杂比较，不能判.cg本体无收益；修正集成后另作对照。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T132239Z-main0915-gqa-kv-cg-four-rounds",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T13:22:39+00:00",
  "profile_id": "gqa-kv-cg",
  "phase": "官方初筛负结果主动停止",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0915f01d5efc2b31af65182ddb87e2d2f62bab0c",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_cg_official_first_warm_negative",
  "artifacts": "experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds",
  "conclusion": "main0915完整603/treefd8a，仅4处GQA KV load加.cg，实际KV547648对性能参考547536。原官方4K冷/首暖4722.73/4944.66 tok/s，同轮参考4713.78/5751.88，首暖观察-14.03%；两轮512请求成功，第三轮已启动后主动SIGTERM中断，16K未测。13:37:37 finished，源码/native/DB恢复及清理通过；原stage=running和error保留，不是仍在运行。非完整官方成绩，不定新基线/PR，不判内核因果。独立DB后分析311非benchmark表共同key配置0变化，但57基线独有/5候选独有key和形状不同，不能称完全可比。后核既有日志：132239的server.log:68 Q_FRAGMENT_INSTALL installed=False、:398 COMPUTE_ORDER_SCOPE_REJECTED；换GQA SHA1043后两项身份仍锁2596，Q-hoist与compute-order均未启用。当期原main140749的:68/186/326确认两项启用。故此为优化组合不完整的混杂比较，原负成绩保留，不能据此判.cg本体整模无收益；待修正集成后另作对照。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T132239Z-main0915-gqa-kv-cg-four-rounds](../../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261025_212440.csv](../../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds/benchmark_results/raw_runs_20261025_212440.csv)；[result.json](../../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
