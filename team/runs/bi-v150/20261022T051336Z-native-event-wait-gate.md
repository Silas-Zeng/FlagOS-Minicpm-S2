<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T051336Z-native-event-wait-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #117 · Event / graph 能力与等待

- **尝试**：能力门、完成性及等待CPU的正负结果。
- **改动**：相关实现 [validate_event_wait_gate.py](../../../scripts/remote/validate_event_wait_gate.py)；[validate_native_event_wait_gate.py](../../../scripts/remote/validate_native_event_wait_gate.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wall9.419391/9.421018ms，无CPU下降证据，未接入服务
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T051336Z-native-event-wait-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T05:13:36.679504+00:00",
  "profile_id": "native_Corex_Event_three_route_wait",
  "phase": "isolated_gpu_native_Event_API_completion_and_wait_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_native_flags3_24trial_byte_close_pass_no_CPU_reduction",
  "artifacts": "experiments/framework/20261022T051336Z-native-event-wait-gate",
  "conclusion": "唯一本地实际系统审计365e6760通过：85seal/source5/f3133outer-7bacgate-327eadapter-ee01cpp/actualSDKcompile0-so1376f0e816256B/ldd-rpath-readelf/实际头identity及桥加载前后mapsd39、DB实体/sourcepost/cleanup全核。A generic/B typedblocking/C directCorexblocking flags3，显式非0同流；24trial各8次32MiB、144项完成性/host全字节/guard/源不变及RNG全过，early0，native settled-close成功、无failure-owner-device-sync救场。native两窗threadCPU9.434407/9.436430ms≈wall9.419391/9.421018ms，无CPU下降证据，未接入服务；六窗v1节流增量0，CPU6/56线程/32GiB保持。DB52319474物理dc2c-schema0dc7-logicalc05d三SHA前后同，05:13:44.418199Z68-0双栈闭无GPU进程，源码不变。root首次SCP37357未退出前读文件锁拒，最终write_stdin exit0解包85seal全过，非设备故障/无重跑。仅实际SDK flags3下局部等待行为，不断言驱动内部机制/服务gain；用户最后手头设备门完成，后续只维护GitHub及方法PR，不新研究/设备/服务/大测试。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T051336Z-native-event-wait-gate](../../../experiments/framework/20261022T051336Z-native-event-wait-gate)
- 原命令：[launch-command.json](../../../experiments/framework/20261022T051336Z-native-event-wait-gate-control/launch-command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T051336Z-native-event-wait-gate/manifest.json)；[source-sha256.json](../../../experiments/framework/20261022T051336Z-native-event-wait-gate-control/source-sha256.json)；[postflight.json](../../../experiments/framework/20261022T051336Z-native-event-wait-gate-control/postflight.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T051336Z-native-event-wait-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T051336Z-native-event-wait-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T051336Z-native-event-wait-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T051336Z-native-event-wait-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
