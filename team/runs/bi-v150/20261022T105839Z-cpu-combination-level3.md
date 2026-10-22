<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T105839Z-cpu-combination-level3

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #130 · CPU metadata + async token 组合

- **尝试**：两种CPU准备方法的组合；方法正确性与短服务性能分别记录。
- **改动**：相关实现 [model_runner.py](../../../docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py)；[biv150_cpu_metadata.py](../../../patches/framework/biv150_cpu_metadata.py)；[biv150_async_token_update.py](../../../patches/framework/biv150_async_token_update.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：干净6f918组合首次完整Math500 Level 3：102/105（97.1429%）通过95%门
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T105839Z-cpu-combination-level3",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T10:58:39.123592+00:00",
  "profile_id": "cpu_combination",
  "phase": "official_math500_level3",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_accuracy_pass",
  "artifacts": "experiments/accuracy/20261022T105839Z-cpu-combination-level3",
  "conclusion": "干净6f918组合首次完整Math500 Level 3：102/105（97.1429%）通过95%门；105请求成功，0 transport错误/截断/空最终答案。原官方数据与脚本，exit0且cleanup_errors空；DB523表19474行变为527表19608行，后续性能对照使用新DB重新建基线。只属于此组合，不代用于新C3views/gather；原件267文件封存核验通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T105839Z-cpu-combination-level3](../../../experiments/accuracy/20261022T105839Z-cpu-combination-level3)
- 原命令：[command.txt](../../../experiments/accuracy/20261022T105839Z-cpu-combination-level3-control/command.txt)；[launch.sh](../../../experiments/accuracy/20261022T105839Z-cpu-combination-level3-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/accuracy/20261022T105839Z-cpu-combination-level3/manifest.json)
- 原始结果：[result.json](../../../experiments/accuracy/20261022T105839Z-cpu-combination-level3/result.json)
- 日志 / 采样：[server.log](../../../experiments/accuracy/20261022T105839Z-cpu-combination-level3/server.log)；[gpu.csv](../../../experiments/accuracy/20261022T105839Z-cpu-combination-level3/gpu.csv)；[exit-code](../../../experiments/accuracy/20261022T105839Z-cpu-combination-level3/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
