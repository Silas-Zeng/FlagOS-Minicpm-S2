<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T213244Z-direct-g8-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #463 · BI-V150特定形状GEMM

- **尝试**：检验Direct-G8实际绑定后的官方4K端到端影响。
- **改动**：原官方参数及服务流程完成四轮，首轮actualDirect receipt有效；DB/source/两SO及stack清理通过。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原始成员、清单与压缩分块按SHA256核验；入口资格失败与完整官方负结果分开。
- **结果**：四轮/1024请求完成：5418.24/6519.84/6726.82/6441.8 tok/s；首暖+1.218533%，弃首均值6562.82对PR105的6627.816667为−0.980665%。KV548432对548336不一致；虽actualDirect首轮有效且stack/恢复通过，不能声称严格因果收益。停止Direct-G8路线，不进入16K/105、不合并
- **是否保留**：保留官方完整负均值；不称严格因果收益，不进入16K/105、不合并或更新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T213244Z-direct-g8-4k-four-rounds",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T21:32:44+00:00",
  "profile_id": "shape-gemm",
  "phase": "official_4k_four_rounds_negative",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "",
  "status": "shape_gemm_direct_g8_official4k_full_negative",
  "artifacts": "experiments/bundles/20261028T213244Z-direct-g8-4k-four-rounds",
  "conclusion": "四轮/1024请求完成：5418.24/6519.84/6726.82/6441.8 tok/s；首暖+1.218533%，弃首均值6562.82对PR105的6627.816667为−0.980665%。KV548432对548336不一致；虽actualDirect首轮有效且stack/恢复通过，不能声称严格因果收益。停止Direct-G8路线，不进入16K/105、不合并、不更新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T213244Z-direct-g8-4k-four-rounds](../../../experiments/bundles/20261028T213244Z-direct-g8-4k-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T213244Z-direct-g8-4k-four-rounds/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T213244Z-direct-g8-4k-four-rounds/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
