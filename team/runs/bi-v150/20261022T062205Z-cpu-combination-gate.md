<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T062205Z-cpu-combination-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #118 · CPU metadata + async token 组合

- **尝试**：两种CPU准备方法的组合；方法正确性与短服务性能分别记录。
- **改动**：相关实现 [model_runner.py](../../../docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py)；[biv150_cpu_metadata.py](../../../patches/framework/biv150_cpu_metadata.py)；[biv150_async_token_update.py](../../../patches/framework/biv150_async_token_update.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：五case各11字段全过
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T062205Z-cpu-combination-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T06:22:05.830235+00:00",
  "profile_id": "CPU_metadata_async_token_combination",
  "phase": "actual_method_no_weights_correctness_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_same_chain_55_fields_graph4_dual_selection_RNG_pass",
  "artifacts": "experiments/framework/20261022T062205Z-cpu-combination-gate",
  "conclusion": "唯一实际本地审计07c12b13通过：55seal/10源/d505launcher-abfcgate/原e155+组合6f918/metadata0e961+async1bb85/实际依赖pin全核，真实方法同链fixture非模型。五case各11字段全过；selection实际decode62为1-1、mixed259为1-0、mixed952为1-1、mixed2048为1-0、prefill2048为1-1（有previous sampled tokens，非纯无历史prefill）。原event四步固定地址graph消费positions-seq-slots-inputIDs全部一致且位置与token变更，每步双delta1，总metadata9-async7，CPU-GPU RNG SHA同。launcher270063-controller270069-worker270073，仅内层唯一锁/worker/cleanup；06:22:26.210821Z外层exit0。CPU6-host20GiB-单BI-V150物理32GiB，DB实体只读重算52319474三SHAdc2c-0dc7-c05d前后同，06:22:26.205563Z后态68-0双栈闭无GPU进程/源不变；worker无Traceback-ERROR，原warnings留存。2035183B归档225a8539已待SCP43608exit0后整包核；无性能计时/完整service或accuracy/C500结论，不相加单项gain或继承103-105，不自动大测。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T062205Z-cpu-combination-gate](../../../experiments/framework/20261022T062205Z-cpu-combination-gate)
- 原命令：[command.json](../../../experiments/framework/20261022T062205Z-cpu-combination-gate-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T062205Z-cpu-combination-gate/manifest.json)；[postflight.json](../../../experiments/framework/20261022T062205Z-cpu-combination-gate-control/postflight.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T062205Z-cpu-combination-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T062205Z-cpu-combination-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T062205Z-cpu-combination-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T062205Z-cpu-combination-gate/exit-code)
- 相关说明：[2026-10-22-cpu-combination-062205-result](../../../analysis/2026-10-22-cpu-combination-062205-result.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
