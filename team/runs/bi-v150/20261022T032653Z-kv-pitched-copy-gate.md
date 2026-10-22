<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T032653Z-kv-pitched-copy-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #113 · KV 二维 SAVE 复制

- **尝试**：保留KV字节和逻辑顺序的正等差复制；单层信号与真实42层诊断分开看。
- **改动**：相关实现 [biv150_kv_pitched_copy.py](../../../patches/framework/candidates/biv150_kv_pitched_copy.py)；[biv150_kv_pitched_bridge.cpp](../../../patches/framework/candidates/biv150_kv_pitched_bridge.cpp)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：两case18checks/计后5checks/CPU-GPU RNGtrue，独立CPU页号+offset pattern payloadSHA均复算同，源及两端guard/完整输出通过；首case8call ABBA wall7.415286/0.672265/0.681895/1.454229ms，event0.652492/0.628267/0.628109/0.652680ms，仅C batch+2D组合单层信号，基线wall波动大不报稳定收益/2D独立贡献/42层服务或E2E
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T032653Z-kv-pitched-copy-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T03:26:53.269434+00:00",
  "profile_id": "kv_pitched_SAVE_C_batch_one_layer",
  "phase": "isolated_gpu_API_byte_and_microtiming_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_two_actual_geometry_one_layer_byte_stream_pass_wall_unstable",
  "artifacts": "experiments/framework/20261022T032653Z-kv-pitched-copy-gate",
  "conclusion": "本agent唯一实际本地stdlib证据审计pass/reporteff32911；86seal/7source/c8c0-818e-0a4d/outer3ffe/c95f/实际ABI f9c3与loadedlibd39d/compile exit0及so9e33ecbf15936B/ldd-rpath-readelf全核；非0Torch stream94118921500112与同流event，maxpitch2147483647。两真实SAVE页序一层构造：R16928/P1058/17334272B原37call→11（2linear9pitched），R16768/P1048/17170432B原26call→6（2linear4pitched），fallback0；两case18checks/计后5checks/CPU-GPU RNGtrue，独立CPU页号+offset pattern payloadSHA均复算同，源及两端guard/完整输出通过。首case8call ABBA wall7.415286/0.672265/0.681895/1.454229ms，event0.652492/0.628267/0.628109/0.652680ms，仅C batch+2D组合单层信号，基线wall波动大不报稳定收益/2D独立贡献/42层服务或E2E。CPUquota6/Torchthreads56/host20GiB外层v1观察非峰值，worker memory空非零用量；DB52319474物理dc2c7646-schema0dc7a465-logicalc05d7e31前后同，03:27:06.831936Z后态68-0双栈closed无GPU进程，source-post无变。首审相对Path URI错误仅本地修正保留未写假pass，未重设备/旧测试；非accuracy/默认集成。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T032653Z-kv-pitched-copy-gate](../../../experiments/framework/20261022T032653Z-kv-pitched-copy-gate)
- 原命令：[launch-command.json](../../../experiments/framework/20261022T032653Z-kv-pitched-copy-gate-control/launch-command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T032653Z-kv-pitched-copy-gate/manifest.json)；[source-sha256.json](../../../experiments/framework/20261022T032653Z-kv-pitched-copy-gate-control/source-sha256.json)；[postflight.json](../../../experiments/framework/20261022T032653Z-kv-pitched-copy-gate-control/postflight.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T032653Z-kv-pitched-copy-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T032653Z-kv-pitched-copy-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T032653Z-kv-pitched-copy-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T032653Z-kv-pitched-copy-gate/exit-code)
- 相关说明：[2026-10-22-kv-pitched-copy-032653-result](../../../analysis/2026-10-22-kv-pitched-copy-032653-result.md)；[2026-10-22-kv-pitched-copy-032653-hardware](../../../analysis/2026-10-22-kv-pitched-copy-032653-hardware.md)；[2026-10-22-kv-pitched-save-worker-boundary](../../../analysis/2026-10-22-kv-pitched-save-worker-boundary.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
