<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T103226Z-pr24-467-mixed-token-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #260 · 当前基线正确性与恢复

- **尝试**：恢复候选PR48的f2ca8a7/tree5e07、527文件默认关闭native并同步缓存身份；原官方完整105为103/105（98.0952%），105 success/stop、0传输错误/空输出/cap。同源码原mixed也通过：4652输入、15tokens答85，计数299tokens正确。两轮均未设native关闭环境覆盖，实际FP关闭/installed False/FX0native，源码未变、DB与清理通过。PR48仍Draft，尚未合入main；原官方两档各四轮正在量化吞吐代价，未发布成绩或性能基线。

旧main526的99/105 reject和mixed特殊token错误保留；旧467/a42也复现，关闭旧版native后仅该边界恢复，排查范围收敛native路径及执行/内存差异，尚未定位具体kernel或单PR。新恢复候选通过不撤销历史失败，不恢复淘汰候选，不靠重复运行取最好成绩；raw诊断的main526来源标签保留，actual版本以各run state/manifest为准。
- **改动**：相关实现 [prefill-response.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/mixed-requests/prefill-response.json)；[prefill-tokens.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/mixed-requests/prefill-tokens.json)；[diagnostic-summary.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/diagnostic-summary.json)；[tokenizer-special-ids.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/analysis/tokenizer-special-ids.json)；[diagnostic_requests.py](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic-control/diagnostic_requests.py)；[accuracy-review.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/accuracy-review.json)；[state.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/state.json)；[archive-receipt.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/archive-receipt.json)；[math_500.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500/math500-level3/20261025_175201/reports/minicpm/math_500.json)；[state.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic-control/state.json)；[prefill-tokens.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/mixed-requests/prefill-tokens.json)；[evidence.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/model-path/evidence.json)；[state.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic-control/state.json)；[prefill-response.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/mixed-requests/prefill-response.json)；[evidence.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/model-path/evidence.json)；[accuracy-review.json](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500-control/accuracy-review.json)；[evidence.json](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500-control/model-path/evidence.json)；[biv150_native_w8a8.py](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500/source/plugin/vllm_fl/patches/biv150_native_w8a8.py)；[prefill-response.json](../../../experiments/framework/20261025T112705Z-native-safe-default-mixed/mixed-requests/prefill-response.json)；[evidence.json](../../../experiments/framework/20261025T112705Z-native-safe-default-mixed-control/model-path/evidence.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：恢复131603完整源码/native及新隔离缓存策略，freshserver原双请求与token返回字段不变；原失败/响应/实际图保留，无性能测量。
- **结果**：旧467/a42完整组合也失败：长题ID8、220后ID0重复1022次，length耗尽1024；计数正常，实际34native通过。
- **是否保留**：保留旧版同场景失败；直接回退该版本不能被视为已解决，不单独归因某PR。诊断原标签main526保留，实际state为467。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T103226Z-pr24-467-mixed-token-diagnostic",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T10:32:26.675229+00:00",
  "profile_id": "main-correctness",
  "phase": "旧467/a42完整组合原mixed token对照",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "1ad9a708ee77323372f0fa5975a04a52d294852c",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "old467_mixed_token_failed",
  "artifacts": "experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic",
  "conclusion": "恢复131603完整旧组合：1ad9/tree d1a9、467文件/native a42，沿旧策略关闭编译缓存并使用本run新私有缓存，实际backbone 34native通过。原双请求只返回token IDs，长题4652输入再次耗尽1024输出：ID8、220后ID0重复1022次，计数1至128正确。10:35:06 UTC语义失败exit1，源码/native未变、DB恢复及清理通过。旧组合也复现此场景，不能据历史100/105认为直接回退即可解决，亦不能单独归因某PR；当前main99/105未达标结论不变。逐字复用diagnostic模块的limitation仍标main526，实际版本以本run state/source/native为准，原件不改；HTTP重叠不代表证明每步mixed覆盖。重复私有编译缓存留完整包及逐项SHA清单，实际model-path图单独保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T103226Z-pr24-467-mixed-token-diagnostic](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/server.log)；[gpu.csv](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
