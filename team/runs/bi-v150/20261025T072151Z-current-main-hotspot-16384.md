<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T072151Z-current-main-hotspot-16384

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #251 · 当前main526热点分析

- **尝试**：16K自然mixed4/FULL8独立诊断，原runner/P/Q/native和服务参数保留。mixed后2步Attention约68.08%可见GPU；FULL只见整图，不能拆内部占比。用于选择优化方向，不报吞吐收益。
- **改动**：相关实现 [072151-analysis-v2.json](../../../analysis/current-main-hotspot-20261025/072151-analysis-v2.json)；[072151-attribution-check.json](../../../analysis/current-main-hotspot-20261025/072151-attribution-check.json)；[analyze.py](../../../analysis/current-main-hotspot-20261025/analyze.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：mixed4中2D Attention总763.40ms，后2步均236.74ms/约68.08%可见GPU，GEMM稳定80.26ms/步
- **是否保留**：保留有效当前轨迹；优先验证prefill Attention候选，不把FULL图壳或几步比例外推成全负载预算。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T072151Z-current-main-hotspot-16384",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T07:21:51.426355+00:00",
  "profile_id": "current-main-hotspot",
  "phase": "16K自然mixed4与FULL8热点诊断",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "true",
  "status": "current_main_hotspot_completed",
  "artifacts": "experiments/profiles/20261025T072151Z-current-main-hotspot-16384",
  "conclusion": "当前main526/native14f，独立527观察源保留runner/P/Q/native字节，实际新FP/AOT/34native通过。原CLI下16K/1024/c64/64请求诊断完成；mixed4中2D Attention总763.40ms，后2步均236.74ms/约68.08%可见GPU，GEMM稳定80.26ms/步。FULL N33/bucket40后6整图均62.251ms，内部热点未知。copy/CPU空档不支持作为本轮主线；选择prefill Attention页访问路径，推进affine候选。profiler及自然prefill进度改变时长，不计官方收益或全负载比例；原件、clock/唯一correlation、清理/source/native/DB通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T072151Z-current-main-hotspot-16384](../../../experiments/profiles/20261025T072151Z-current-main-hotspot-16384)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/profiles/20261025T072151Z-current-main-hotspot-16384-control/source-sha256.json)
- 原始结果：[hotspot-16384-infqps-concurrency64-minicpm-20261025-152957.json](../../../experiments/profiles/20261025T072151Z-current-main-hotspot-16384/load/results/hotspot-16384-infqps-concurrency64-minicpm-20261025-152957.json)；[result.json](../../../experiments/profiles/20261025T072151Z-current-main-hotspot-16384/result.json)
- 日志 / 采样：[server.log](../../../experiments/profiles/20261025T072151Z-current-main-hotspot-16384/server.log)；[gpu.csv](../../../experiments/profiles/20261025T072151Z-current-main-hotspot-16384/gpu.csv)；[exit-code](../../../experiments/profiles/20261025T072151Z-current-main-hotspot-16384/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
