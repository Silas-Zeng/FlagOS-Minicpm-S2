<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T101034477784Z-biv150-stream-read-reference-hotspot-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #325 · BI-V150连续流读取参考

- **尝试**：固定512MiB BF16连续流读＋128KiB checksum输出，三组Event中位约0.806800ms、逻辑读665.432GB/s；两次内容checksum、一次copy正确性及计时后checksum通过。仅连续流读参考，不是物理HBM或散页GQA硬上限，不是吞吐优化/官方成绩。DB/source/native与设备清理通过。同期补回main6971三个实际linear缓存文本，仍不伪装大M实际参数采集。
- **改动**：相关实现 [results.json](../../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/results.json)；[worker.py](../../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/source/worker.py)；[archive-receipt.json](../../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/archive-receipt.json)；[triton-cache](../../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/triton-cache)；本轮准确变体以原件源码清单为准。
- **怎么测**：单配置512MiB BF16连续流读＋128KiB checksum，每组16次Graph replay共三组；copy只核正确性不计带宽，profiler关闭。
- **结果**：连续流读参考665.432GB/s，checksum/copy检查通过；不是HBM硬上限或模型吞吐收益。
- **是否保留**：保留带宽参考及实际linear文本，用于预算；不替换比赛基线，不从连续读参考推GQA可实现收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T101034477784Z-biv150-stream-read-reference-hotspot-component",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T10:10:34.477784+00:00",
  "profile_id": "stream-read-reference",
  "phase": "reference",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "stream_read_reference_completed",
  "artifacts": "experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component",
  "conclusion": "固定512MiB BF16连续流读＋128KiB checksum输出，三组Event中位约0.806800ms、逻辑读665.432GB/s；两次内容checksum、一次copy正确性及计时后checksum通过。仅连续流读参考，不是物理HBM或散页GQA硬上限，不是吞吐优化/官方成绩。DB/source/native与设备清理通过。同期补回main6971三个实际linear缓存文本，仍不伪装大M实际参数采集。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T101034477784Z-biv150-stream-read-reference-hotspot-component](../../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/manifest.json)
- 原始结果：[results.json](../../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/worker.log)；[gpu.csv](../../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/gpu.csv)；[exit-code](../../../experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
