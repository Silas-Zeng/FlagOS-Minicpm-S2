<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T142019Z-current-main-compute-order

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #205 · 计算顺序与采样顺序分离

- **尝试**：计算行重排以适配Attention路径，采样保持原请求顺序。当前适配队友normalized main328，仅改runner/helper两文件；代码4fca58ba/tree5c77。140324→141159短测表观约+6.59%，但KV521840→521936，gain=null。142019完整105题103正确（98.0952%）通过，但P分支0命中。144620原官方8轮全部成功，1536请求；原第2–4轮均值4K5116.68、16K3436.04 total tok/s，实际P N62/M2048/outside59。保留Draft方法候选：这是绝对性能，不能归因单项收益，也不能用吞吐命中弥补准确率P0。旧423的单pair+5.124857%、三题质量、结构映射与独立参考证据保留，不能替代新组合结果。
- **改动**：相关实现 [compute-order-current-main-official.json](../../../analysis/compute-order-current-main-official.json)；[compute-order-current-main-accuracy.json](../../../analysis/compute-order-current-main-accuracy.json)；[compute-order-current-main-pair.json](../../../analysis/compute-order-current-main-pair.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-main-profile/README.md)；[compute-order-math4-event-130351.json](../../../analysis/compute-order-math4-event-130351.json)；[compute-order-math4-event-125330.json](../../../analysis/compute-order-math4-event-125330.json)；[compute-order-service-retest-pair.json](../../../analysis/compute-order-service-retest-pair.json)；[compute-order-math4-summary.json](../../../analysis/compute-order-math4-summary.json)；[compute-order-structure.json](../../../analysis/compute-order-structure.json)；[compute-order-oracle-summary.json](../../../analysis/compute-order-oracle-summary.json)；[compute-order-oracle-085500.json](../../../analysis/compute-order-oracle-085500.json)；[compute-order-first-layer.json](../../../analysis/compute-order-first-layer.json)；[result.json](../../../experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json)；[README.md](../../../archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md)；[answer-summary.json](../../../experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json)；[compute-order-service-pair.json](../../../analysis/compute-order-service-pair.json)；[compute-order-accuracy.json](../../../analysis/compute-order-accuracy.json)；[framework_innovation.md](../../../docs/agent-work/framework_innovation.md)；[compute_order_review.md](../../../docs/agent-work/compute_order_review.md)；[completion.json](../../../experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：original_math500_level3 / 32768 / 8 / 105。
- **结果**：103/105（98.0952%）达到原95%门
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T142019Z-current-main-compute-order",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T14:20:20.133450+00:00",
  "profile_id": "compute_order",
  "phase": "current_main_official_math500_level3_accuracy",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "3283672b92fa30f93f652b242193999836a95f88",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "original_math500_level3",
  "output_len": "32768",
  "concurrency": "8",
  "num_prompts": "105",
  "profiler": "false",
  "status": "accuracy_pass_no_P_current_main",
  "artifacts": "experiments/accuracy/20261023T142019Z-current-main-compute-order",
  "conclusion": "103/105（98.0952%）达到原95%门；105成功、无transport/空最终答案，1题达到原输出上限(index83)。完整题集通过，但P分支0命中，不能据此证明该分支准确率。保留候选，使用同一冻结446源码进入官方吞吐。 728原件逐项核、729导入，完整446源码/清理通过；DB前后如实保留，见analysis/compute-order-current-main-accuracy.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T142019Z-current-main-compute-order](../../../experiments/accuracy/20261023T142019Z-current-main-compute-order)
- 原命令：[command.txt](../../../experiments/accuracy/20261023T142019Z-current-main-compute-order-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/accuracy/20261023T142019Z-current-main-compute-order/manifest.json)；[postflight-full.json](../../../experiments/accuracy/20261023T142019Z-current-main-compute-order/postflight-full.json)；[purpose.json](../../../experiments/accuracy/20261023T142019Z-current-main-compute-order-control/purpose.json)；[source-sha256.json](../../../experiments/accuracy/20261023T142019Z-current-main-compute-order-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/accuracy/20261023T142019Z-current-main-compute-order/result.json)
- 日志 / 采样：[server.log](../../../experiments/accuracy/20261023T142019Z-current-main-compute-order/server.log)；[gpu.csv](../../../experiments/accuracy/20261023T142019Z-current-main-compute-order/gpu.csv)；[exit-code](../../../experiments/accuracy/20261023T142019Z-current-main-compute-order/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
