<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T211121Z-direct-g8-4k-first-round-unbound

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #461 · BI-V150特定形状GEMM

- **尝试**：验证Direct-G8官方4K冷轮后的实际kernel绑定身份。
- **改动**：首轮256请求沿SDK fallback完成；首条SUCCESS后未取得Direct-G8 receipt，supervisor停止后续轮次。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原始成员、清单与压缩分块按SHA256核验；入口资格失败与完整官方负结果分开。
- **结果**：仅测一冷轮6005.43 tok/s/256成功；marker缺失，实际沿SDK fallback，停止后续轮次。登记为资格/接口失败，不是数值错误或候选收益。
- **是否保留**：保留接口绑定失败证据；不归类为数值错误。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T211121Z-direct-g8-4k-first-round-unbound",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T21:11:21+00:00",
  "profile_id": "shape-gemm",
  "phase": "official_4k_first_round_qualification_failed",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "",
  "status": "shape_gemm_direct_g8_first_round_bind_failed",
  "artifacts": "experiments/bundles/20261028T211121Z-direct-g8-4k-first-round-unbound",
  "conclusion": "仅测一冷轮6005.43 tok/s/256成功；marker缺失，实际沿SDK fallback，停止后续轮次。登记为资格/接口失败，不是数值错误或候选收益。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T211121Z-direct-g8-4k-first-round-unbound](../../../experiments/bundles/20261028T211121Z-direct-g8-4k-first-round-unbound)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T211121Z-direct-g8-4k-first-round-unbound/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T211121Z-direct-g8-4k-first-round-unbound/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
