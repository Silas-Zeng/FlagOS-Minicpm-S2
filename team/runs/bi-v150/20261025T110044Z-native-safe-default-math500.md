<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T110044Z-native-safe-default-math500

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #262 · 当前基线正确性与恢复

- **尝试**：恢复候选PR48的f2ca8a7/tree5e07、527文件默认关闭native并同步缓存身份；原官方完整105为103/105（98.0952%），105 success/stop、0传输错误/空输出/cap。同源码原mixed也通过：4652输入、15tokens答85，计数299tokens正确。两轮均未设native关闭环境覆盖，实际FP关闭/installed False/FX0native，源码未变、DB与清理通过。PR48仍Draft，尚未合入main；原官方两档各四轮正在量化吞吐代价，未发布成绩或性能基线。

旧main526的99/105 reject和mixed特殊token错误保留；旧467/a42也复现，关闭旧版native后仅该边界恢复，排查范围收敛native路径及执行/内存差异，尚未定位具体kernel或单PR。新恢复候选通过不撤销历史失败，不恢复淘汰候选，不靠重复运行取最好成绩；raw诊断的main526来源标签保留，actual版本以各run state/manifest为准。
- **改动**：相关实现 [prefill-response.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/mixed-requests/prefill-response.json)；[prefill-tokens.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/mixed-requests/prefill-tokens.json)；[diagnostic-summary.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/diagnostic-summary.json)；[tokenizer-special-ids.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/analysis/tokenizer-special-ids.json)；[diagnostic_requests.py](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic-control/diagnostic_requests.py)；[accuracy-review.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/accuracy-review.json)；[state.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/state.json)；[archive-receipt.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/archive-receipt.json)；[math_500.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500/math500-level3/20261025_175201/reports/minicpm/math_500.json)；[state.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic-control/state.json)；[prefill-tokens.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/mixed-requests/prefill-tokens.json)；[evidence.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/model-path/evidence.json)；[state.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic-control/state.json)；[prefill-response.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/mixed-requests/prefill-response.json)；[evidence.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/model-path/evidence.json)；[accuracy-review.json](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500-control/accuracy-review.json)；[evidence.json](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500-control/model-path/evidence.json)；[biv150_native_w8a8.py](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500/source/plugin/vllm_fl/patches/biv150_native_w8a8.py)；[prefill-response.json](../../../experiments/framework/20261025T112705Z-native-safe-default-mixed/mixed-requests/prefill-response.json)；[evidence.json](../../../experiments/framework/20261025T112705Z-native-safe-default-mixed-control/model-path/evidence.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原105题/采样/服务与评分器不变；清native环境覆盖，实际提交默认关闭及FP/FX/AOT身份、完整源码后态和DB恢复闭合。
- **结果**：f2ca/527默认关闭native：原完整105为103/105（98.0952%），105 success/stop，0传输错误/空输出/cap；actual FX0native。
- **是否保留**：保留本恢复候选完整准确率通过；不继承给未合并main，不恢复旧失败，吞吐代价仍在原官方测量中。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T110044Z-native-safe-default-math500",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T11:00:44+00:00",
  "profile_id": "main-correctness",
  "phase": "新527默认关闭native完整官方105准确率",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "f2ca8a7f46528c5fd4881fac466c4ba941500889",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_safe_default_accuracy_pass",
  "artifacts": "experiments/accuracy/20261025T110044Z-native-safe-default-math500",
  "conclusion": "恢复候选f2ca8a7/tree5e07、527文件，原官方Math500 Level 3完整105题103/105（98.0952%）通过。105请求success/stop，0传输错误、0空最终/提取、0输出达到上限；原脚本、题目与采样参数不变。清除native环境覆盖而不显式设0，验证提交源码默认关闭，实际FP native_enabled False、installed False及FX0native；本轮未加载native，不伪造native_unchanged字段。11:25:44 UTC owner completed、完整源码未变、DB恢复及清理通过。此结论仅属于PR48受测f2ca候选；当前main99/105未达标历史保留，同源码原mixed结果另列；原官方两档各四轮正在测量吞吐代价，尚无终态成绩，不据此声明全部修复或新性能基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T110044Z-native-safe-default-math500](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500)
- 原命令：[command.json](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500/manifest.json)；[source-sha256.json](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500/result.json)
- 日志 / 采样：[server.log](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500/server.log)；[gpu.csv](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500/gpu.csv)；[exit-code](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
