<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T230741Z-allocator-noop-candidate-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #183 · KV 分配器无状态快返

- **尝试**：普通decode不新增页或完整块哈希时返回原空分配结果；保留新页、哈希、恢复与非RUNNING原路径，CPU片段和服务配对分别记录。
- **改动**：相关实现 [README.md](../../../archive/ai/20261022-framework-kv/next-kv-noop-allocate/README.md)；[allocator-noop-service-pair.json](../../../analysis/allocator-noop-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：64成功0失败，原参数/DB544四端/完整422→423源码/实际QGQA/新快返及清理等30项通过，唯一same_KV失败：521936→521840，gain=null
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T230741Z-allocator-noop-candidate-decode4k",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T23:07:41+00:00",
  "profile_id": "allocator_noop",
  "phase": "candidate_decode4k",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_confounded_KV_no_gain",
  "artifacts": "experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k",
  "conclusion": "仅init+helper423；Engine381092实际ARMED与多请求FIRST_SELECTED，快返原empty且保fallback，488原件全核。双方64成功0失败，原参数/DB544四端/完整422→423源码/实际QGQA/新快返及清理等30项通过，唯一same_KV失败：521936→521840，gain=null。实测36.510461919→36.839126302秒；未显示可确认服务收益，不默认集成、不追加大测/准确率或重启凑容量；保留CPU净省、代码和完整失败/边界证据。详analysis/allocator-noop-service-pair.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T230741Z-allocator-noop-candidate-decode4k](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261023-070935.json](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261023-070935.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T230741Z-allocator-noop-candidate-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
