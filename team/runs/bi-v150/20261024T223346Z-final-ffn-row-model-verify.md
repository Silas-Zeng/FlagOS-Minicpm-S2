<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T223346Z-final-ffn-row-model-verify

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #241 · 末层FFN/o_proj选行与模型对照

- **尝试**：原FFN527及unbacked v3均遇mixed长题不完成；原main526同mixed也失败、精确同请求serial通过，不能归因选行，根因未确认。v3解决S1的AOT检查节点问题并通过三语义；不恢复模型资格、不进性能。原失败保留，不为通过候选强改框架。
- **改动**：相关实现 [results.json](../../../experiments/framework/20261024T204020Z-final-ffn-row-prune/results.json)；[state.json](../../../experiments/framework/20261024T204020Z-final-ffn-row-prune/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T204020Z-final-ffn-row-prune/archive-receipt.json)；[results.json](../../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/results.json)；[state.json](../../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/archive-receipt.json)；[state.json](../../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify-control/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 4串行+2并发。
- **结果**：FFN527四串行语义均正确但均fallback，随后真实mixed已选择M2048/S2；并发长prefill响应只见未闭合think，1024输出token耗尽/finish_reason=length，未得到85，模型门失败。22:37:26 UTCsource/native未变、DB恢复和清理通过。保留原SSE/响应/源码，不进入性能或优化PR；组件逐bit通过不能替代
- **是否保留**：保留本轮原件与边界；收尾不重复测试，后继仅按实际资格继续。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T223346Z-final-ffn-row-model-verify",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T22:33:46Z",
  "profile_id": "final-ffn-row-prune",
  "phase": "final_ffn_model_verify",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "4串行+2并发",
  "profiler": "false",
  "status": "final_ffn_mixed_semantic_failed",
  "artifacts": "experiments/framework/20261024T223346Z-final-ffn-row-model-verify",
  "conclusion": "FFN527四串行语义均正确但均fallback，随后真实mixed已选择M2048/S2；并发长prefill响应只见未闭合think，1024输出token耗尽/finish_reason=length，未得到85，模型门失败。22:37:26 UTCsource/native未变、DB恢复和清理通过。保留原SSE/响应/源码，不进入性能或优化PR；组件逐bit通过不能替代模型验证，具体根因尚未定位。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T223346Z-final-ffn-row-model-verify](../../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify/server.log)；[gpu.csv](../../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify/gpu.csv)；[exit-code](../../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
