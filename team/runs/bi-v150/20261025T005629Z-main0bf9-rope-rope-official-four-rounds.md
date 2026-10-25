<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T005629Z-main0bf9-rope-rope-official-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #243 · RoPE与KV写入融合

- **尝试**：保持526的RoPE旋转数学与Q/K输出，在同一核追加完整KV写入。生产v2外置autotune元数据，四语义及实际42融合/0旧KV/34native图通过；性能筛选6完整轮未见净正信号，按用户要求早停并封存，不更新基线或追加105。组件正信号、首轮记录/模型失败和全部原始测量分别保留。
- **改动**：相关实现 [results.json](../../../experiments/framework/20261024T203032Z-rope-kv-component/results.json)；[state.json](../../../experiments/framework/20261024T203032Z-rope-kv-component/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T203032Z-rope-kv-component/archive-receipt.json)；[results.json](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/results.json)；[state.json](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/archive-receipt.json)；[state.json](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/state.json)；[source-diff.json](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/failed-posthoc/source-diff.json)；[0-computation_graph.py](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/failed-posthoc/0-computation_graph.py)；[archive-receipt.json](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/archive-receipt.json)；[state.json](../../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2-control/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 1280完整请求；后续不完整轮不计。
- **结果**：RoPE528原官方参数完成4K四轮5183.64/5678.16/5777.01/5777.66，暖均5744.28 tok/s，对526暖均约−0.25%；16K已完成3439.95/4008.32，首暖对对应4045.32约−0.91%。1280个完整请求成功，后续不完整轮不计入。01:37:15 UTC按无净正信号及用户收尾要求主动早停，01:37:21清理/sourc
- **是否保留**：原始证据和失败保留；是否进入模型/合并以本轮结论为准，不自动续测。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T005629Z-main0bf9-rope-rope-official-four-rounds",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T00:56:29Z",
  "profile_id": "rope-kv-fusion",
  "phase": "official_partial",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "1280完整请求；后续不完整轮不计",
  "profiler": "false",
  "status": "rope_official_screen_early_stopped",
  "artifacts": "experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds",
  "conclusion": "RoPE528原官方参数完成4K四轮5183.64/5678.16/5777.01/5777.66，暖均5744.28 tok/s，对526暖均约−0.25%；16K已完成3439.95/4008.32，首暖对对应4045.32约−0.91%。1280个完整请求成功，后续不完整轮不计入。01:37:15 UTC按无净正信号及用户收尾要求主动早停，01:37:21清理/source/native/DB恢复通过；原completed=false/KeyboardInterrupt保留。KV546432≠547536，不称严格因果或稳定负差；非完整两档四轮，不更新基线、不追加105或代码PR。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T005629Z-main0bf9-rope-rope-official-four-rounds](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds/benchmark-command.json)；[command.txt](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261025_085723.csv](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds/benchmark_results/raw_runs_20261025_085723.csv)；[summary_20261025_085723.csv](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds/benchmark_results/summary_20261025_085723.csv)；[result.json](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261025T005629Z-main0bf9-rope-rope-official-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
