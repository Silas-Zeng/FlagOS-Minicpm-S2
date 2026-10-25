<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #261 · 当前main基线正确性

- **尝试**：固定main526/0bf9、native14f。完整官方105题为99/105（94.2857%），原review valid/reject，未达到至少100正确的门槛，当前main不具比赛基线准确率资格。105请求均成功、0传输错误，4题达到输出上限但不剔除分母。另有freshserver原mixed长题生成<think>后1023个<s>的已知错误，计数正常、精确同题旧串行正确。旧131603的完整467/a42组合使用新隔离缓存也复现同场景，长题ID8、220后ID0重复1022次，计数正常；不能认为直接回退该版本即可解决。同一旧组合仅关闭已有native开关后，实际图0 native、installed False，长题57tokens答85且计数正确。排查重点收敛到native路径及其执行/内存差异，尚不能锁定具体kernel或PR；此开关只作诊断，非完整准确率、性能或合规优化。两类问题分别留证，根因尚未定位，不据此归因某条PR，不靠反复运行取最好成绩，也不恢复淘汰候选。
- **改动**：相关实现 [prefill-response.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/mixed-requests/prefill-response.json)；[prefill-tokens.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/mixed-requests/prefill-tokens.json)；[diagnostic-summary.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/diagnostic-summary.json)；[tokenizer-special-ids.json](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/analysis/tokenizer-special-ids.json)；[diagnostic_requests.py](../../../experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic-control/diagnostic_requests.py)；[accuracy-review.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/accuracy-review.json)；[state.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/state.json)；[archive-receipt.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/archive-receipt.json)；[math_500.json](../../../experiments/accuracy/20261025T095054Z-main0bf9-main-math500/math500-level3/20261025_175201/reports/minicpm/math_500.json)；[state.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic-control/state.json)；[prefill-tokens.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/mixed-requests/prefill-tokens.json)；[evidence.json](../../../experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/model-path/evidence.json)；[state.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic-control/state.json)；[prefill-response.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/mixed-requests/prefill-response.json)；[evidence.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/model-path/evidence.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：旧467源码/SO不改，沿相同新隔离缓存、原双请求/采样，仅环境清洗后设既有native开关0；保存实际0 native图与installed False证据。
- **结果**：旧467仅关闭native后双请求通过：实际图0 native、installed False；长题57tokens答85，计数299tokens正确。
- **是否保留**：保留正确性隔离证据，重点收敛native路径及执行/内存差异；不归因具体kernel/PR，不作优化或提交资格，当前main99/105 reject不变。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T10:42:11.660782+00:00",
  "profile_id": "main-correctness",
  "phase": "旧467 native关闭原mixed正确性隔离",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "1ad9a708ee77323372f0fa5975a04a52d294852c",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "old467_native_off_mixed_pass",
  "artifacts": "experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic",
  "conclusion": "同旧467/a42完整源码与原双请求，保持新隔离编译缓存，只在环境清洗后设已有VLLM_FL_BIV150_NATIVE_W8A8=0；实际新backbone图0 native调用、安装日志installed False。长题4652输入/57输出答85，decode计数1至128正确/299输出，双请求通过；10:44:35 UTC completed true、源码/native文件未变、DB恢复及清理通过。与旧native-on的同场景失败对照，关闭native后本边界恢复，排查重点收敛到native路径及其执行/内存差异，尚不能归因具体kernel、单PR或证明因果机制。此开关仅正确性诊断，非性能、完整准确率或合规优化；当前main526官方99/105 reject不变，不据此形成提交资格。原diagnostic limitation的main526旧标签逐字保留，实际版本/关闭状态以本run state、日志和图为准。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/server.log)；[gpu.csv](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
