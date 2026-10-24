<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T145945Z-pr25-cache-kv-verify1-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #220 · PR25 与缓存修复后的 KV 保存恢复

- **尝试**：以7596cc0为共同基点，比较原调度与单victim KV SAVE/FULL，保留官方服务参数。VERIFY1字节门通过，关闭回读后的两轮对照同KV546432、同初始DB：4K为+0.103%/+0.644%但无FULL覆盖，16K为+4.728%/−0.493%。筛选未见明显退化，尚未确认稳定收益；两侧调优增长不同，不换算为耗时。保留候选，按用户要求完成官方四轮及最终组合准确率后再下结论、确定新基线；不把本轮结果归给后续main集成。
- **改动**：相关实现 [pr25-kv-current-pair.json](../../../analysis/pr25-kv-current-pair.json)；[result.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/result.json)；[archive-receipt.json](../../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds-control/archive-receipt.json)；[source-manifest.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/source-manifest.json)；[coverage.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/coverage.json)；[semantic-validation.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/model-path/semantic-validation.json)；[archive-receipt.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds/result.json)；[state.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务KV全字节VERIFY1与独立4题语义/实际编译图检查；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32/0；R16960、每方向729415680字节一致，SAVE504/FULL2688。另同服务4/4语义正确、实际34层native图；VERIFY1不计性能或完整准确率。
- **是否保留**：保留KV字节、真实模型路径和4题语义门；允许进入关闭VERIFY回读的性能对照，完整组合准确率另验。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T145945Z-pr25-cache-kv-verify1-context16k-long",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T14:59:47.177576+00:00",
  "profile_id": "pr25-kv-current",
  "phase": "kv_verify1_context16k_long",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "7596cc0eb14fdbfc56e42eb1cd68d0f37b890d93",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "kv_verify1_model_path_pass",
  "artifacts": "experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long",
  "conclusion": "在7596cc0基点显式加入单victim KV SAVE/FULL并启用VERIFY1全字节回读：32成功0失败，coverage.valid；R16960/1060页，每方向729415680字节一致，SAVE504次（420 linear＋84 pitched）、FULL2688次、zero0，恢复后17个scheduled token消费者到达。另同服务4/4语义正确、实际新图34个native层4..37，图SHA2472ed1d；不能据scope计数或消费者到达替代完整答案准确率。候选tree0a11ffec/493文件，SO14f4457a；KV547536，Q命中且无回退，P本轮未观测，不记P失败。driver/owner exit0，15:05:46 UTC source/native未变、原DB207f1b恢复。保留KV机制与小样本模型路径门；VERIFY1含回读不计性能，不能与KV546432的完整规模基线直接比较，待关闭VERIFY的完整规模候选及必要组合准确率。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T145945Z-pr25-cache-kv-verify1-context16k-long](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/manifest.json)；[source-sha256.json](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/source-sha256.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
