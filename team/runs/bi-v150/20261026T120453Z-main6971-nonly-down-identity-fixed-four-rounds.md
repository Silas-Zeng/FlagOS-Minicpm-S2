<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #334 · BF16 down N方向分组布局

- **尝试**：N128单层M64省10.55%、M32省3.63%；精确身份修复后的M64-only官方4K暖均5719.8133（观察+1.1145%），16K首暖4005.55（观察−2.7652%）后停。六轮1280 SUCCESS、旧prefill栈/新FX42闭合；KV516320、1008MiB常驻副本，保留混合结果，不合并/定基线/跑105。旧v1身份失配与大M两种负布局分别保留。
- **改动**：相关实现 [result.json](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/result.json)；[worker.py](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/archive-receipt.json)；[candidate.py](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/result.json)；[worker.py](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/result.json)；[worker.py](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/result.json)；[worker.py](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/result.json)；[2048-original_linear.ttgir](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/2048-original_linear.ttgir)；[2048-n256_linear.ttgir](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/2048-n256_linear.ttgir)；[archive-receipt.json](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/archive-receipt.json)；[raw_runs_20261026_192922.csv](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/benchmark_results/raw_runs_20261026_192922.csv)；[performance-stop-decision.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/performance-stop-decision.json)；[posthoc-after-stop.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/posthoc-after-stop.json)；[prefill-activation.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/prefill-activation.json)；[archive-receipt.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/archive-receipt.json)；[raw_runs_20261026_200712.csv](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/benchmark_results/raw_runs_20261026_200712.csv)；[performance-stop-decision.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/performance-stop-decision.json)；[posthoc-after-stop.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/posthoc-after-stop.json)；[prefill-activation.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/prefill-activation.json)；[archive-receipt.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/archive-receipt.json)；[2026-10-26-local-to-e2e-budget.md](../../../analysis/2026-10-26-local-to-e2e-budget.md)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方benchmark/服务参数，4K/16K输入、1024输出、并发64、请求256/128；M64原已测kernel/helper/runner不变，只修compute-order精确runner身份。4K完成四轮，16K完成冷/首暖后按对应首暖比较停止；不重测未变基线，不继承105。
- **结果**：4K四轮暖均5719.8133（对5656.77观察+1.1145%）；16K首暖4005.55（对4119.46观察−2.7652%）后停，六轮1280 SUCCESS。修复后旧prefill栈/FX42有效，KV516320；混合结果，无105/新基线。
- **是否保留**：保留组件及4K正信号和完整负载原件；本M64-only双权重组合16K首暖负，停止后继，不合并或定新基线。容量压力是已有日志支持的可能解释，未独立隔离因果；准确率未跑、不继承103/105。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T12:04:53+00:00",
  "profile_id": "bf16-nonly-down-official",
  "phase": "official_four_plus_two_round_early_stop",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096/16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256/128",
  "profiler": "false",
  "status": "nonly_down_identity_official_mixed_no_baseline",
  "artifacts": "experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds",
  "conclusion": "N-only M64精确runner身份修复v2，原compute-order/normalization/Q-hoist及新42pack/FX42实际闭合，posthoc valid/prefill_valid=true。4K四轮4899.30/5700.44/5672.77/5786.23 tok/s，弃冷暖均5719.813333对5656.77观察+1.114476%；16K冷/首暖3642.71/4005.55，首暖对4119.46观察−2.765168%后主动停止，六轮1280 SUCCESS。KV516320对548336；4K日志KV最高62.6%、Running最高64，16K最高100%、Running最高31，基线前两轮最高33；双方日志未发现抢占/重算记录，无独立计数。本轮M64调用分布未采，旧16K小M窗口仅历史参考；1008MiB副本及容量/调度差异公开，不声称严格布局因果。保留4K正/16K负混合结果，停止本轮后续16K/105，不合并、不定新基线；source/native/DB/清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_200712.csv](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/benchmark_results/raw_runs_20261026_200712.csv)；[summary_20261026_200712.csv](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/benchmark_results/summary_20261026_200712.csv)；[result.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/exit-code)
- 相关说明：[2026-10-26-local-to-e2e-budget](../../../analysis/2026-10-26-local-to-e2e-budget.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
