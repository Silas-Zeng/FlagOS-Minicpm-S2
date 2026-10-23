<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T155446Z-q-fragment-hoist

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #151 · Q fragment 循环外保留

- **尝试**：同一方法的KV16K/4K局部门与真实服务配对分别记录；保留单轮正信号，TTFT变化及准确率边界同时展示。
- **改动**：相关实现 [biv150_q_fragment_service.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/biv150_q_fragment_service.py)；[compare_q_service_pair.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/compare_q_service_pair.py)；[q-fragment-service-pair.json](../../../analysis/q-fragment-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：Q fragment已测413源码首次完整Math500 Level 3：101/105（96.1905%）通过95%门
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T155446Z-q-fragment-hoist",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T15:54:47.090058+00:00",
  "profile_id": "q_fragment_hoist_accuracy",
  "phase": "official_math500_level3",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_accuracy_pass",
  "artifacts": "experiments/accuracy/20261022T155446Z-q-fragment-hoist",
  "conclusion": "Q fragment已测413源码首次完整Math500 Level 3：101/105（96.1905%）通过95%门；105请求成功、0 transport错误、1题(index83)到32768输出上限、无空最终答案。原脚本/原参数、实际N8/M349步骤42层命中，不能据此报全程覆盖。DB前后527表19702行三SHA一致；413 live及归档源码通过，关闭阶段EngineDeadError/ResourceWarning保留，清理完成，285原件逐seal核验。保留短服务+1.71126%单轮信号与准确率，未报稳定/全量性能；算子工作交接，主线转KV调度。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T155446Z-q-fragment-hoist](../../../experiments/accuracy/20261022T155446Z-q-fragment-hoist)
- 原命令：[command.txt](../../../experiments/accuracy/20261022T155446Z-q-fragment-hoist-control/command.txt)；[launch.sh](../../../experiments/accuracy/20261022T155446Z-q-fragment-hoist-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/accuracy/20261022T155446Z-q-fragment-hoist/manifest.json)；[postflight-full.json](../../../experiments/accuracy/20261022T155446Z-q-fragment-hoist/postflight-full.json)；[source-sha256.json](../../../experiments/accuracy/20261022T155446Z-q-fragment-hoist-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/accuracy/20261022T155446Z-q-fragment-hoist/result.json)
- 日志 / 采样：[server.log](../../../experiments/accuracy/20261022T155446Z-q-fragment-hoist/server.log)；[gpu.csv](../../../experiments/accuracy/20261022T155446Z-q-fragment-hoist/gpu.csv)；[exit-code](../../../experiments/accuracy/20261022T155446Z-q-fragment-hoist/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
