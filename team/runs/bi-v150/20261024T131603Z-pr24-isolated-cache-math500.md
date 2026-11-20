<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T131603Z-pr24-isolated-cache-math500

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #216 · PR24 真实路径复验与 KV 诊断

- **尝试**：131603同源码隔离编译缓存后，实际新图有34个native调用（layer4..37），完整Math500 Level3为100/105通过；0请求错误/0空最终，83/99/101达到输出上限，101无可提取答案。该结果仅证明本轮路径与准确率，不报吞吐或精度提升。105037至124000六轮仍因旧AOT图失配撤回PR24模型资格；standalone9、CPU/trace观察与VERIFY1字节事实保留，旧Attention1.018秒不能作有效PR24预算，也不追溯恢复旧性能资格。默认缓存修复和PR25复验另记。
- **改动**：相关实现 [CURRENT_WORK.md](../../../CURRENT_WORK.md)；[accuracy-review.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/accuracy-review.json)；[active-graph-typed-assignment-check.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/active-graph-typed-assignment-check.json)；[computation_graph.py](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/active-graph/computation_graph.py)；[environment-overrides.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/environment-overrides.json)；[archive-receipt.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/archive-receipt.json)；[loaded-computation-graph.py](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/loaded-computation-graph.py)；[early-stop-request.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/early-stop-request.json)；[state.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/result.json)；[coverage.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/coverage.json)；[state.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/state.json)；[observer-manifest.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/observer-manifest.json)；[archive-receipt.json](../../../experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/archive-receipt.json)；[pr24-kv-diagnostic.json](../../../analysis/pr24-kv-diagnostic.json)；[pr24-resume-native-v2-114500.json](../../../analysis/pr24-resume-native-v2-114500.json)；[pr24-resume-native-failure.json](../../../analysis/pr24-resume-native-failure.json)；[pr24-resume-db-comparison.json](../../../analysis/pr24-resume-db-comparison.json)；[summary.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/summary.json)；[native-build-manifest.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/native-build-manifest.json)；[operator-check.json](../../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/operator-check.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：准确率门；输入 / 输出 / 并发 / 请求数：original_math500_level3 / 32768 / 8 / 105。
- **结果**：隔离缓存后实际34层native；Math500 Level3 100/105（95.2381%）通过，0请求错误/0空最终。仅本轮准确率，不恢复旧失配轮次资格、不报性能。
- **是否保留**：保留本实例实际native路径及完整准确率通过证据；3题输出上限、1题无可提取答案仍在105分母。旧六轮失配不恢复，默认缓存修复与性能另验。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T131603Z-pr24-isolated-cache-math500",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T13:16:04.368089+00:00",
  "profile_id": "pr24-main",
  "phase": "math500_level3_accuracy_isolated_cache",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "1ad9a708ee77323372f0fa5975a04a52d294852c",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "original_math500_level3",
  "output_len": "32768",
  "concurrency": "8",
  "num_prompts": "105",
  "profiler": "false",
  "status": "accuracy_pass_native_graph_verified",
  "artifacts": "experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500",
  "conclusion": "PR24同源码隔离编译缓存后，完整Math500 Level3为100/105（95.2381%）并通过准确率门；105评审success，0请求错误、0空最终答案，index83/99/101达到输出上限，index101无可提取答案但仍计入105分母。实际新图SHA e4ff31935bbec19fe13a631237262f6139e77da2a3eba0321a5d5609219a3a33含layer4..37共34个native调用；源main1ad9a708/tree d1a96e3f及native SO未变。使用VLLM_DISABLE_COMPILE_CACHE=1与独立VLLM_CACHE_ROOT/TORCHINDUCTOR_CACHE_DIR，官方serve与评测参数未改。driver/owner exit0，DB恢复207f1b，原始105预测/评审/配置/报告及运行图已保留；223个重复源码和4个SQLite二进制省略，完整467源映射和原包SHA见archive-receipt。不报性能或精度提升，不追溯恢复105037至124000旧AOT失配六轮资格；默认缓存修复与PR25后续复验另记。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T131603Z-pr24-isolated-cache-math500](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500)
- 原命令：[command.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500/manifest.json)；[source-sha256.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500/result.json)
- 日志 / 采样：[server.log](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500/server.log)；[gpu.csv](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500/gpu.csv)；[exit-code](../../../experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
