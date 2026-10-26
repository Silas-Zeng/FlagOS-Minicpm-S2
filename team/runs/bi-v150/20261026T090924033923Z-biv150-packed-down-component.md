<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T090924033923Z-biv150-packed-down-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #320 · BF16 down权重微块布局

- **尝试**：真实F.linear同配置的BF16位重排；首次停在SME假设，v2保留全部正确性后通过8项，但M2030完整Graph慢71.89%，停止。
- **改动**：相关实现 [source](../../../experiments/framework/20261026T090924033923Z-biv150-packed-down-component/source)；[source](../../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/source)；[result.json](../../../experiments/framework/20261026T092809453391Z-biv150-packed-down-component/result.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实layer0 down权重、合成M2030 BF16激活，原opaque/F.linear同配置与唯一无损微块布局；首次输入后停止。
- **结果**：真实F.linear选BM256/BN256/BK32/w16/s2；pack/unpack及首normal逐位一致。B dot useSme2→0，shared64→48KiB/reg97→98，在机制检查停止；未完成全部正确性、未计时。
- **是否保留**：原机制假设未实现；不当数学错误或性能负。后继独立v2保留数值门，以一次计时判断净效果。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T090924033923Z-biv150-packed-down-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T09:09:24.033923+00:00",
  "profile_id": "bf16-packed-down",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "packed_b_sme_not_retained",
  "artifacts": "experiments/framework/20261026T090924033923Z-biv150-packed-down-component",
  "conclusion": "真实F.linear选BM256/BN256/BK32/w16/s2；pack/unpack及首normal逐位一致。B dot useSme2→0，shared64→48KiB/reg97→98，在机制检查停止；未完成全部正确性、未计时。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T090924033923Z-biv150-packed-down-component](../../../experiments/framework/20261026T090924033923Z-biv150-packed-down-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261026T090924033923Z-biv150-packed-down-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261026T090924033923Z-biv150-packed-down-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261026T090924033923Z-biv150-packed-down-component/worker.log)；[gpu.csv](../../../experiments/framework/20261026T090924033923Z-biv150-packed-down-component/gpu.csv)；[exit-code](../../../experiments/framework/20261026T090924033923Z-biv150-packed-down-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
