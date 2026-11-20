<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T211606Z-rope-kv-model-verify

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #238 · RoPE与KV写入融合

- **尝试**：528 RoPE融合首次真实服务，四语义及实际编译图/来源门。
- **改动**：本轮来源与原件见下方证据，限制见方法记录。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 4语义；非官方性能/105。
- **结果**：4/4语义正确，但图门跨submod误拒且新增.best_config；source_unchanged=false、completed=false，原失败保留。
- **是否保留**：保留失败与posthoc原件；cache位置和parser修复后另验，不能追溯恢复资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T211606Z-rope-kv-model-verify",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T21:16:06Z",
  "profile_id": "rope-kv-fusion",
  "phase": "rope_kv_model_verify",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "4语义；非官方性能/105",
  "profiler": "false",
  "status": "rope_model_source_and_parser_failed",
  "artifacts": "experiments/framework/20261024T211606Z-rope-kv-model-verify",
  "conclusion": "RoPE首次模型528/tree57bb四语义全部正确（含4908-token prefill），但旧图parser未跨submod传播Q/K/dep而拒绝；source目录另新增.best_config，原source_unchanged=false、completed=false、exit1和cleanup_errors保留。DB已恢复、native未变、设备进程已清理；不是数值或性能负结果，也不是模型资格通过。failed-posthoc保留实际FX/来源差异；后续CPU解析修正不追溯恢复本轮资格，cache位置与parser修复需新来源的新服务门。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T211606Z-rope-kv-model-verify](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify/server.log)；[gpu.csv](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify/gpu.csv)；[exit-code](../../../experiments/framework/20261024T211606Z-rope-kv-model-verify/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
