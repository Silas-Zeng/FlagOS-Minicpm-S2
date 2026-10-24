<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T142819Z-pr25-cache-main-fullsize-two-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #219 · PR25 与缓存修复后的 KV 保存恢复

- **尝试**：以7596cc0为共同基点，比较原调度与单victim KV SAVE/FULL，保留官方服务参数。VERIFY1字节门通过，关闭回读后的两轮对照同KV546432、同初始DB：4K为+0.103%/+0.644%但无FULL覆盖，16K为+4.728%/−0.493%。筛选未见明显退化，尚未确认稳定收益；两侧调优增长不同，不换算为耗时。保留候选，按用户要求完成官方四轮及最终组合准确率后再下结论、确定新基线；不把本轮结果归给后续main集成。
- **改动**：相关实现 [pr25-kv-current-pair.json](../../../analysis/pr25-kv-current-pair.json)；[result.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/result.json)；[archive-receipt.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds-control/archive-receipt.json)；[source-manifest.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/source-manifest.json)；[coverage.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/coverage.json)；[semantic-validation.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/model-path/semantic-validation.json)；[archive-receipt.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds/result.json)；[state.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：官方负载规模、每档两轮筛选；非官方四轮成绩；输入 / 输出 / 并发 / 请求数：4096/16384 / 1024 / 64 / 256/128。
- **结果**：4K两轮5396.58/5730.67、16K两轮3565.12/3992.53 total tok/s；768请求全成功，KV546432。仅本组筛选基线，非官方四轮分数或优化收益。
- **是否保留**：保留两档全部原轮作本组筛选基线；不丢首轮、不以第二轮变快归因优化，不自动定为新官方基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T142819Z-pr25-cache-main-fullsize-two-rounds",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T14:28:20.665952+00:00",
  "profile_id": "pr25-kv-current",
  "phase": "fullsize_two_rounds_baseline",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "7596cc0eb14fdbfc56e42eb1cd68d0f37b890d93",
  "flaggems_commit": "",
  "input_len": "4096/16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256/128",
  "profiler": "false",
  "status": "fullsize_two_rounds_baseline_completed",
  "artifacts": "experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds",
  "conclusion": "PR25＋默认缓存身份修复的完整规模两轮基线：4K5396.58/5730.67、16K3565.12/3992.53 total tok/s，768请求全部成功，KV546432。保留官方serve/benchmark参数、两档各2轮，非官方四轮分数，也非优化收益；不丢首轮或把第二轮加速归因于KV方法。共同源码7596cc0/tree b37543af，SO14f4457a；P/Q命中且Q无回退。DB从共同fb035397种子增长25表/810行，其中MM新增48个选择条目，19条resolve_benchmarker警告不能等同调优次数/耗时；14:54:13累计12抢占既非末态也不能拆逐轮。driver/owner exit0，14:59:10 UTC清理、source/native未变并恢复原DB207f1b。保留作本组对照基线，候选结果另登记；详细命令、4轮原值和原包SHA见原件。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T142819Z-pr25-cache-main-fullsize-two-rounds](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds)
- 原命令：[command.txt](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/manifest.json)；[source-sha256.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_screen.csv](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/raw_runs_screen.csv)；[result.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/server.log)；[gpu.csv](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/gpu.csv)；[exit-code](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
