<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T223155Z-rope-kv-model-verify-v2

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #240 · RoPE与KV写入融合

- **尝试**：保留实际526旋转表达式与Q/K输出，在同核追加KV写入；组件正信号保留。211606模型四语义正确，但跨submod图门误拒且源码目录新增.best_config，原source_unchanged=false/completed=false不改判，修复后须新服务门。

最新收尾：RoPE生产v2/tree4e2f52ce四题语义正确（含4908-token prefill），实际42层融合、0旧KV writer、同fusion Q/K/dep与34层native图/FP/AOT通过。22:33:41 UTC源/native未变、DB恢复和清理成功；修复为外置autotune元数据与真实跨submod解析。保留进入性能；本轮不是完整105或吞吐成绩，211606原失败保持。
- **改动**：相关实现 [results.json](../../../experiments/framework/20261024T203032Z-rope-kv-component/results.json)；[state.json](../../../experiments/framework/20261024T203032Z-rope-kv-component/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T203032Z-rope-kv-component/archive-receipt.json)；[results.json](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/results.json)；[state.json](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/archive-receipt.json)；[state.json](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/state.json)；[source-diff.json](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/failed-posthoc/source-diff.json)；[0-computation_graph.py](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/failed-posthoc/0-computation_graph.py)；[archive-receipt.json](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/archive-receipt.json)；[state.json](../../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2-control/state.json)；[archive-receipt.json](../../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2-control/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 4语义。
- **结果**：RoPE生产v2/tree4e2f52ce四题语义正确（含4908-token prefill），实际42层融合、0旧KV writer、同fusion Q/K/dep与34层native图/FP/AOT通过。22:33:41 UTC源/native未变、DB恢复和清理成功；修复为外置autotune元数据与真实跨submod解析。保留进入性能；本轮不是完整105或吞吐成绩，2
- **是否保留**：保留本轮原件与边界；收尾不重复测试，后继仅按实际资格继续。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T223155Z-rope-kv-model-verify-v2",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T22:31:55Z",
  "profile_id": "rope-kv-fusion",
  "phase": "rope_kv_model_verify",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "4语义",
  "profiler": "false",
  "status": "rope_v2_model_gate_pass",
  "artifacts": "experiments/framework/20261024T223155Z-rope-kv-model-verify-v2",
  "conclusion": "RoPE生产v2/tree4e2f52ce四题语义正确（含4908-token prefill），实际42层融合、0旧KV writer、同fusion Q/K/dep与34层native图/FP/AOT通过。22:33:41 UTC源/native未变、DB恢复和清理成功；修复为外置autotune元数据与真实跨submod解析。保留进入性能；本轮不是完整105或吞吐成绩，211606原失败保持。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T223155Z-rope-kv-model-verify-v2](../../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2/server.log)；[gpu.csv](../../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2/gpu.csv)；[exit-code](../../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
