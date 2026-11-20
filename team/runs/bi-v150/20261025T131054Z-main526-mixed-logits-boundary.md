<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T131054Z-main526-mixed-logits-boundary

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #270 · 主线复核与native备用方案

- **尝试**：在原mixed边界采集有界logits观察，不改采样或扩大排查。
- **改动**：main526仅加入口与观察模块两处，实际527/tree7ebc；原失败与快照缺失分别保留。 版本、命令和源码见下方原件；[方法记录](../../methods/main-correctness.md)。
- **怎么测**：main526+两处graph外有界观察改动（实际527/tree7ebc），native14f/原双请求；记录原响应、token与安装标记。未形成完整快照，不是原526无改动对照。
- **结果**：mixed长题仍ID8＋ID0×1023耗尽上限；快照未生成、分析FileNotFoundError，无法判断logits或根因。
- **是否保留**：保留原exit1及cleanup_errors；后态/DB/source/native通过，不扩大或重跑此诊断。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T131054Z-main526-mixed-logits-boundary",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T13:10:54.228268+00:00",
  "profile_id": "main-correctness",
  "phase": "有界logits观察失败留证",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "mixed_logits_snapshot_failed",
  "artifacts": "experiments/framework/20261025T131054Z-main526-mixed-logits-boundary",
  "conclusion": "main526+两处有界观察改动，实际527/tree7ebc，原native14f/双请求；计数正确，mixed长题ID8一次+ID0重复1023次，length耗尽1024，原exit1保留。安装标记存在但快照未生成，分析FileNotFoundError记在原cleanup_errors，不能据此判logits异常或定位根因。源码/native未变、DB恢复、9031关闭且设备无活动后态通过；保留失败诊断，不重跑、不恢复旧候选。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T131054Z-main526-mixed-logits-boundary](../../../experiments/framework/20261025T131054Z-main526-mixed-logits-boundary)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/framework/20261025T131054Z-main526-mixed-logits-boundary-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/framework/20261025T131054Z-main526-mixed-logits-boundary/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T131054Z-main526-mixed-logits-boundary/server.log)；[gpu.csv](../../../experiments/framework/20261025T131054Z-main526-mixed-logits-boundary/gpu.csv)；[exit-code](../../../experiments/framework/20261025T131054Z-main526-mixed-logits-boundary/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
