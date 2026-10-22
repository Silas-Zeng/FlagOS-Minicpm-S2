<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T045818Z-event-wait-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #116 · Event / graph 能力与等待

- **尝试**：能力门、完成性及等待CPU的正负结果。
- **改动**：相关实现 [validate_event_wait_gate.py](../../../scripts/remote/validate_event_wait_gate.py)；[validate_native_event_wait_gate.py](../../../scripts/remote/validate_native_event_wait_gate.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：Event、B cuda.Event默认、C cuda.Event(blocking=True)，非0显式流/每trial8次32MiBpinned D2H/六窗ABCCBA各4trial，共24trial144checks及RNG全过，early_complete总0，完成后无额外同步才核host全字节/guard/endquery，之后独立源回读不掩盖失败
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T045818Z-event-wait-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T04:58:18.350054+00:00",
  "profile_id": "corex_Event_three_route_wait",
  "phase": "isolated_gpu_Event_API_completion_and_wait_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_Event_24trial_byte_pass_no_typedblocking_CPU_reduction",
  "artifacts": "experiments/framework/20261022T045818Z-event-wait-gate",
  "conclusion": "唯一实际本地系统审计b21fb342通过：61seal/source2/outer32a075-gate67090/契约41ba与实际11现存源pin（2cpp缺失照存）/实际mappedlibd39d/CLI/CPU6-56线程-32GiB/DB实体/双idle-post-sourcepost全核。三route A torch.Event、B cuda.Event默认、C cuda.Event(blocking=True)，非0显式流/每trial8次32MiBpinned D2H/六窗ABCCBA各4trial，共24trial144checks及RNG全过，early_complete总0，完成后无额外同步才核host全字节/guard/endquery，之后独立源回读不掩盖失败。六窗wall均值ms9.429327/9.428015/8.688993/9.428666/9.427978/9.430027，wait-threadCPU均约9.44ms，typedblocking无CPU下降信号；逐trial threadCPU高于wall均保留，最大比1.464，首C低wall不当收益。每窗v1nr_throttled/throttled_time增量0；DB52319474三SHAdc2c-0dc7-c05d前后同，04:58:26.010254Z68-0双栈闭无GPU进程/source不变。仅EventAPI完成性与等待局部行为，不证模型暴露wait或服务gain；本地首审误套quota_us字段后改actual raw.quota/period续审，非设备失败/无重跑，原件不改。按用户只完成手头native对照后维护GitHub，不新研究/自动服务或大测试。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T045818Z-event-wait-gate](../../../experiments/framework/20261022T045818Z-event-wait-gate)
- 原命令：[launch-command.json](../../../experiments/framework/20261022T045818Z-event-wait-gate-control/launch-command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T045818Z-event-wait-gate/manifest.json)；[source-sha256.json](../../../experiments/framework/20261022T045818Z-event-wait-gate-control/source-sha256.json)；[postflight.json](../../../experiments/framework/20261022T045818Z-event-wait-gate-control/postflight.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T045818Z-event-wait-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T045818Z-event-wait-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T045818Z-event-wait-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T045818Z-event-wait-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
