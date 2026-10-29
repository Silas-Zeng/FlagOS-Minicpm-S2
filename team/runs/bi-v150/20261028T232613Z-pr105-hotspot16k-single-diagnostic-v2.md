<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T232613Z-pr105-hotspot16k-single-diagnostic-v2

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #471 · BI-V150特定形状GEMM

- **尝试**：对PR105 16K/128请求运行一次带采集器的冷态覆盖诊断。
- **改动**：128/128完成；driver/owner/collector成功并完成清理；posthoc缺fresh FX图证，非官方性能测量。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：BI-V150 PR105树f1658、814源文件；16K输入/1024输出/128请求；driver/owner/collector为0，posthoc为1，native GQA生产回执覆盖。
- **结果**：PR105 16K单次冷态采集诊断完成128/128；driver/owner/collector exit 0，生产GQA selected/captured覆盖，source/SO/DB/清理门通过。posthoc exit 1且fresh FX图证缺项；保留诊断与trace，不作为官方成绩或稳态吞吐。
- **是否保留**：保留单次冷态profile和原始trace；不补伪造FX证据，不当作官方成绩或稳态收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T232613Z-pr105-hotspot16k-single-diagnostic-v2",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T23:26:13.805348+00:00",
  "profile_id": "shape-gemm",
  "phase": "profile_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b3b87d2a1c13448bd8c6bc24e8045c0458b8b9dd",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "cuda",
  "status": "profile_diagnostic_completed_posthoc_fresh_fx_missing",
  "artifacts": "experiments/bundles/20261028T232613Z-pr105-hotspot16k-single-diagnostic-v2",
  "conclusion": "PR105 16K单次冷态采集诊断完成128/128；driver/owner/collector exit 0，生产GQA selected/captured覆盖，source/SO/DB/清理门通过。posthoc exit 1且fresh FX图证缺项；保留诊断与trace，不作为官方成绩或稳态吞吐。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T232613Z-pr105-hotspot16k-single-diagnostic-v2](../../../experiments/bundles/20261028T232613Z-pr105-hotspot16k-single-diagnostic-v2)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T232613Z-pr105-hotspot16k-single-diagnostic-v2/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T232613Z-pr105-hotspot16k-single-diagnostic-v2/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
