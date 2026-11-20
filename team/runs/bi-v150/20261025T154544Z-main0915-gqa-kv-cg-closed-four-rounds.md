<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #280 · GQA KV读取缓存策略

- **尝试**：恢复原有优化组合后重新检查.cg局部省时能否转为模型收益。
- **改动**：保留4处.cg并同步Q-fragment/compute-order中受审源码身份；实际选中日志闭合，KV547648对参考547536，非严格同条件因果对照。 版本、命令和源码见下方原件；[方法记录](../../methods/gqa-kv-cg.md)。
- **怎么测**：原0813/RUNS4/SKIP_FIRST1及服务参数不变，0915完整603/treefbb3四处.cg＋三处关联身份修正；原日志确认两项优化启用，15:58:19向owner273504 SIGTERM，15:58:24清理完成。
- **结果**：Q-fragment与compute-order均实际选中；4K冷/首暖5073.26/5362.19 tok/s，512成功，首暖对历史/当期观察−6.7750%/−6.9386%。
- **是否保留**：按首暖负可停策略收尾，第三轮中断、16K/105不跑；KV不同不判严格因果，无模型净收益或新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T15:45:44+00:00",
  "profile_id": "gqa-kv-cg",
  "phase": "cg恢复原优化组合后官方初筛主动停止",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0915f01d5efc2b31af65182ddb87e2d2f62bab0c",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "gqa_cg_closed_first_warm_negative",
  "artifacts": "experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds",
  "conclusion": "团队main0915完整603/treefbb3，仅4处GQA KV load加.cg并更新Q-fragment/compute-order关联身份；原日志与stack-activation证实Q-fragment install+selected及compute-order selected均启用。原官方4K冷/首暖5073.26/5362.19 tok/s，TTFT10560.11/3709.50ms，两轮512 SUCCESS；首暖相对历史5751.88与当期5761.99观察-6.7750%/-6.9386%。按首暖负可停策略15:58:19向owner273504 SIGTERM，第三轮中断，16K/105不跑；15:58:24 finished、source/native/DB恢复、9031关闭及GPU68MiB/0%通过，driver已退出，owner仅零资源Z态。原failed/error/stage=running保留，不冒充完整四轮。KV547648对历史547536，非严格因果比较；恢复原优化组合后本轮仍未见模型净收益，不合并或定新基线，不回改旧.cg混杂成绩。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds](../../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds/benchmark-command.json)；[command.json](../../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261025_234745.csv](../../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds/benchmark_results/raw_runs_20261025_234745.csv)；[result.json](../../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
