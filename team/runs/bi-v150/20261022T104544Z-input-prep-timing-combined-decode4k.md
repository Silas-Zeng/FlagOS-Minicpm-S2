<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T104544Z-input-prep-timing-combined-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #126 · 输入准备成本诊断

- **尝试**：当前组合的真实输入等待与预处理累计；诊断耗时不作为性能收益。
- **改动**：相关实现 [prepare_input_prep_timing.py](../../../scripts/remote/input-prep-timing-combined/prepare_input_prep_timing.py)；[biv150_input_prep_timing.py](../../../scripts/remote/input-prep-timing-combined/biv150_input_prep_timing.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：EngineCore288617最后快照256步，wait累计1.858095ms/max34.337us，preprocess累计4.553460970s，等待占0.0408%；诊断有计时扰动，不报性能收益
- **是否保留**：保留诊断结论；当前不据此实施输入同步优化。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T104544Z-input-prep-timing-combined-decode4k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T10:45:46.284032+00:00",
  "profile_id": "input_prep_timing_combined",
  "phase": "decode4k_wait_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "complete_partial_diagnostic",
  "artifacts": "experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k",
  "conclusion": "6f918组合真实服务64成功0失败。EngineCore288617最后快照256步，wait累计1.858095ms/max34.337us，preprocess累计4.553460970s，等待占0.0408%；这是部分累计非最终全负载。暂不支持优先改造输入同步；诊断有计时扰动，不报性能收益。代码413文件与DB前后相同，后态设备空闲，保留诊断和原件。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T104544Z-input-prep-timing-combined-decode4k](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261022-184739.json](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261022-184739.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T104544Z-input-prep-timing-combined-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
