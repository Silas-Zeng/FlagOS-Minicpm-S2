<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T112706Z-main6971-nonly-down-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #332 · BF16 down N方向分组布局

- **尝试**：N128单层M64省10.55%、M32省3.63%；精确身份修复后的M64-only官方4K暖均5719.8133（观察+1.1145%），16K首暖4005.55（观察−2.7652%）后停。六轮1280 SUCCESS、旧prefill栈/新FX42闭合；KV516320、1008MiB常驻副本，保留混合结果，不合并/定基线/跑105。旧v1身份失配与大M两种负布局分别保留。
- **改动**：相关实现 [result.json](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/result.json)；[worker.py](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/archive-receipt.json)；[candidate.py](../../../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/candidate.py)；[result.json](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/result.json)；[worker.py](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/result.json)；[worker.py](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/result.json)；[worker.py](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/source/worker.py)；[archive-receipt.json](../../../experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/archive-receipt.json)；[result.json](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/result.json)；[2048-original_linear.ttgir](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/2048-original_linear.ttgir)；[2048-n256_linear.ttgir](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/2048-n256_linear.ttgir)；[archive-receipt.json](../../../experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/archive-receipt.json)；[raw_runs_20261026_192922.csv](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/benchmark_results/raw_runs_20261026_192922.csv)；[performance-stop-decision.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/performance-stop-decision.json)；[posthoc-after-stop.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/posthoc-after-stop.json)；[prefill-activation.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/prefill-activation.json)；[archive-receipt.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/archive-receipt.json)；[raw_runs_20261026_200712.csv](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/benchmark_results/raw_runs_20261026_200712.csv)；[performance-stop-decision.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/performance-stop-decision.json)；[posthoc-after-stop.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/posthoc-after-stop.json)；[prefill-activation.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/prefill-activation.json)；[archive-receipt.json](../../../experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/archive-receipt.json)；[2026-10-26-local-to-e2e-budget.md](../../../analysis/2026-10-26-local-to-e2e-budget.md)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方benchmark与服务参数，4K输入/1024输出/c64/256请求，原定每档四轮；保留候选默认启用及1008MiB常驻权重，不隐去KV成本。复用未变基线，完成冷/首暖后按对应5533.03筛选，低于即停，不运行16K或105。
- **结果**：4K冷/首暖4758.57/5440.33 tok/s，512 SUCCESS；首暖对5533.03观察−1.675393%后主动停。pack42/FX42/M64已证；compute-order源SHA拒绝，prefill未闭合，KV516320；无16K/105。
- **是否保留**：停止旧v1原样运行；该组compute-order回退，不能作N-only净收益判定。保留原结果；精确身份修复作为新源码独立官方对照，尚未证明收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T112706Z-main6971-nonly-down-four-rounds",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T11:27:06+00:00",
  "profile_id": "bf16-nonly-down-official",
  "phase": "official_two_round_early_stop",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "nonly_down_official_first_warm_negative",
  "artifacts": "experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds",
  "conclusion": "M64-only N128布局候选原官方4K冷/首暖4758.57/5440.33 tok/s，两轮512 SUCCESS；首暖对5533.03观察下降1.675393%，按规则主动SIGTERM早停，owner exit1不是框架错误，11:39:06清理及DB/source/native恢复通过。新路径pack42层/1056964608B、真实FX42个opaque和首次M64编译选中已证；KV516320对548336，低于理论523760。prefill全栈未闭合：compute-order因model_runner固定源SHA不匹配明确scope拒绝回原路，虽normalization/Q-hoist实际选中仍prefill_valid=false，不能作只改变N-only的严格因果比较。停止本模型候选；无16K/105/完整四轮或新基线，不继承103/105。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T112706Z-main6971-nonly-down-four-rounds](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/benchmark-command.json)；[command.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261026_192922.csv](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/benchmark_results/raw_runs_20261026_192922.csv)；[result.json](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/exit-code)
- 相关说明：[2026-10-26-local-to-e2e-budget](../../../analysis/2026-10-26-local-to-e2e-budget.md)；[2026-10-26-local-to-e2e-review](../../../analysis/2026-10-26-local-to-e2e-review.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
