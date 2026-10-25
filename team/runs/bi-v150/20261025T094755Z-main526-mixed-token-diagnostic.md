<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T094755Z-main526-mixed-token-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #258 · 主线复核与native备用方案

- **尝试**：PR48备用f2ca/tree5e07默认关闭native：原完整105为103/105，原mixed长题答85且计数正确；原官方4K/16K各四轮1536请求成功，弃首轮5271.89/3763.84 tok/s，Mean TTFT4281.63/137244.33ms。实际KV521936，FX0native，源码未变、DB恢复和清理通过。高于官方公告基线2028.01/915.15并满足TTFT要求；低于native-on性能参考5758.72/4045.20，但DB/KV不匹配，不能拆成单内核因果收益。保留备用，PR48仍Draft，不替换性能主线。

官方105使用temperature1/top_p.95，旧main99/105仅说明该轮未达门槛，不能据此认定代码缺陷；temperature0专项重复token另行保留，尚未定位具体kernel/PR。旧1ad9不含PR25也复现，不能直接撤回24/25。用户要求主力继续吞吐探索；团队main0915的原105复核独立进行，不用后续高分抹去旧轮。
- **改动**：相关实现 [prefill-response.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/mixed-requests/prefill-response.json)；[prefill-tokens.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/mixed-requests/prefill-tokens.json)；[diagnostic-summary.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/diagnostic-summary.json)；[tokenizer-special-ids.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/analysis/tokenizer-special-ids.json)；[diagnostic_requests.py](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic-control/diagnostic_requests.py)；[accuracy-review.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/accuracy-review.json)；[state.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/state.json)；[archive-receipt.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/archive-receipt.json)；[math_500.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500/math500-level3/20261025_175201/reports/minicpm/math_500.json)；[state.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic-control/state.json)；[prefill-tokens.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/mixed-requests/prefill-tokens.json)；[evidence.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/model-path/evidence.json)；[state.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic-control/state.json)；[prefill-response.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/mixed-requests/prefill-response.json)；[evidence.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/model-path/evidence.json)；[accuracy-review.json](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500-control/accuracy-review.json)；[evidence.json](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500-control/model-path/evidence.json)；[biv150_native_w8a8.py](../../../experiments/accuracy/20261025T110044Z-native-safe-default-math500/source/plugin/vllm_fl/patches/biv150_native_w8a8.py)；[prefill-response.json](../../../experiments/framework/20261025T112705Z-native-safe-default-mixed/mixed-requests/prefill-response.json)；[evidence.json](../../../experiments/framework/20261025T112705Z-native-safe-default-mixed-control/model-path/evidence.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：freshserver原双请求及首内容同步，仅加return_token_ids；长题4652输入/max_tokens1024，原JSON/SSE/token IDs全部保存。
- **结果**：原main mixed再次失败：长题ID8一次＋ID0重复1023次，词表为<think>＋<s>；计数正常。根因未定位，原exit1保留。
- **是否保留**：保留基线故障证据；不恢复淘汰候选，不归因M8或全部main，完整105独立判分。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T094755Z-main526-mixed-token-diagnostic",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T09:47:56.069484+00:00",
  "profile_id": "main-correctness",
  "phase": "原main526 mixed token正确性诊断",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "main_mixed_token_failed",
  "artifacts": "experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic",
  "conclusion": "原main526 freshserver重放原mixed双请求，仅增加return_token_ids。长题4652输入、length耗尽1024输出：ID8一次后ID0重复1023次，词表对应<think>及<s>；计数请求1至128正确、299输出。两侧原响应均收齐，语义失败明确保留，不是客户端仅漏显示普通文本，也不能据此确定错误层或归因M8 GEMM。源码tree8671/native14f及实际图身份与旧对照一致，起始DB207f、后态533c，源/native未变、DB恢复及清理通过，原exit1保留。根因未定位；此记录属于主基线正确性，不恢复已淘汰候选或宣称完整准确率通过，官方105结果另列。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T094755Z-main526-mixed-token-diagnostic](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/server.log)；[gpu.csv](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
