<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T103226Z-pr24-467-mixed-token-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #260 · 主线复核与native备用方案

- **尝试**：PR48备用f2ca/tree5e07默认关闭native：原完整105为103/105，原mixed长题答85且计数正确；原官方4K/16K各四轮1536请求成功，弃首轮5271.89/3763.84 tok/s，Mean TTFT4281.63/137244.33ms。实际KV521936，FX0native，源码未变、DB恢复和清理通过。高于官方公告基线2028.01/915.15并满足TTFT要求；低于native-on性能参考5758.72/4045.20，但DB/KV不匹配，不能拆成单内核因果收益。保留备用，PR48仍Draft，不替换性能主线。

官方105使用temperature1/top_p.95，旧main99/105仅说明该轮未达门槛，不能据此认定代码缺陷；temperature0专项重复token另行保留，尚未定位具体kernel/PR。旧1ad9不含PR25也复现，不能直接撤回24/25。用户要求主力继续吞吐探索；团队main0915/tree766b完整603文件的原105本轮100/105（95.2381%）通过，102 stop＋3 cap（94/99/101），0传输错误/空答案，actual34native、源码/native/DB恢复及清理通过。新结果与旧99/105并列保留；原mixed专项重复token仍未定位，不据此宣称mixed修复、稳定改善或全部合格基线。
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
