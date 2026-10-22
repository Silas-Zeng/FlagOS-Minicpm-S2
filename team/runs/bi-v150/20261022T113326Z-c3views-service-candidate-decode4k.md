<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T113326Z-c3views-service-candidate-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #133 · C3重复视图清理

- **尝试**：复用mixed Attention中的视图，减少重复slice/unbind；短输入信号与大输入、真实服务结果分别记录。
- **改动**：相关实现 [biv150_c3_view_reuse.py](../../../patches/framework/candidates/biv150_c3_view_reuse.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：64成功0失败，38.964930220s、6937.9310696 tok/s，较112548表观+0.01769%
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T113326Z-c3views-service-candidate-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T11:33:27.661684+00:00",
  "profile_id": "c3_view_reuse_service",
  "phase": "actual_service_comparison",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_inconclusive_capacity_mismatch",
  "artifacts": "experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k",
  "conclusion": "仅runner接线+新C3views helper，真实EngineCore296715第37次execute中42次forward命中。64成功0失败，38.964930220s、6937.9310696 tok/s，较112548表观+0.01769%；DB一致但KV521936 vs521840，单轮微小差异且容量失配，不能认定因果收益。保留已测代码与单层短输入5.9714%信号，暂不集成或扩测，主线回GPU热点。观察失败隔离v2已互审，准确率不能借用6f组合。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T113326Z-c3views-service-candidate-decode4k](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-193524.json](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-193524.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T113326Z-c3views-service-candidate-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
