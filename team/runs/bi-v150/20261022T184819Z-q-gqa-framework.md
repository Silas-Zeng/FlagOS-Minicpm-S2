<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T184819Z-q-gqa-framework

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #161 · Q-hoist + GQA 框架组合

- **尝试**：仅适配精确GQA包装的安装身份，保留两条算术路径与原服务参数；已获单pair正信号及独立101/105准确率通过，评测DB增长另列。
- **改动**：相关实现 [METHOD.md](../../../archive/ai/20261022-framework-kv/q-gqa-framework/METHOD.md)；[biv150_q_fragment_service.py](../../../archive/ai/20261022-framework-kv/q-gqa-framework/biv150_q_fragment_service.py)；[q-gqa-service-pair.json](../../../analysis/q-gqa-service-pair.json)；[accuracy-review.json](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework/accuracy-review.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 105。
- **结果**：组合准确率101/105（96.190476%）通过原官方Math500 Level3门，105 success、0 transport错误、0 output cap、无空答案
- **是否保留**：组合准确率通过；性能仍仅单pair，不据此声明稳定或完整官方成绩。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T184819Z-q-gqa-framework",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T18:48:19.262293+00:00",
  "profile_id": "q_gqa_framework",
  "phase": "official_math500_level3",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "105",
  "profiler": "false",
  "status": "complete_accuracy_pass",
  "artifacts": "experiments/accuracy/20261022T184819Z-q-gqa-framework",
  "conclusion": "组合准确率101/105（96.190476%）通过原官方Math500 Level3门，105 success、0 transport错误、0 output cap、无空答案；复用root判卷及逐289seal验收，不重复测评。使用已测Q+GQA414源、runnercc442/Q51fc/GQA1a814，原SERVER/评测脚本不改；Engine341334实际execute2 N8/M376原返回后Q/GQA各增42。KV521936，19:10:03 UTC退出0、414 live/archive无fail及设备清理。调优DB实际527表19702行→529表19769行，after物理9ca232/schema9535/logical552d，不能写DB稳定，也不能将527旧性能pair当作529后继基线；本轮不是性能成绩。此前+7.466632%仍仅单次同条件长pair，不冒称稳定统计或完整官方性能。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T184819Z-q-gqa-framework](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework)
- 原命令：[command.txt](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework-control/command.txt)；[launch.sh](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework/manifest.json)；[postflight-full.json](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework/postflight-full.json)；[source-sha256.json](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework/result.json)
- 日志 / 采样：[server.log](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework/server.log)；[gpu.csv](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework/gpu.csv)；[exit-code](../../../experiments/accuracy/20261022T184819Z-q-gqa-framework/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
