<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T114435Z-current-mixed-native-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #135 · 当前版本GPU热点

- **尝试**：复用原轨迹并按需补短native诊断；GPU路径占比只用于选择下一实验，不作吞吐成绩。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：可见kernel累计1063.156218ms：2D Attention640.380398ms/60.2339%，GEMM337.191759ms/31.7161%，3D2.6891%，reduce0.1245%
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T114435Z-current-mixed-native-diagnostic",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T11:44:37.430487+00:00",
  "profile_id": "current_mixed_gpu_hotspots",
  "phase": "bounded_native_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "true",
  "status": "complete_diagnostic",
  "artifacts": "experiments/framework/20261022T114435Z-current-mixed-native-diagnostic",
  "conclusion": "当前干净6f仅追加诊断，原服务参数，32成功0失败；真实三步均N2/M2048/P2047，下一execute入口停止，完整包含三次采样，1656 kernel。可见kernel累计1063.156218ms：2D Attention640.380398ms/60.2339%，GEMM337.191759ms/31.7161%，3D2.6891%，reduce0.1245%。本窗没有graph壳；只定位当前mixed热点，不是吞吐成绩或所有负载占比。DB前后同527/19608，源码仅runner追加，后态空闲，465原件封存通过。下一步只做未测2D w16单点最短A/B，CPU方向降为补充。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T114435Z-current-mixed-native-diagnostic](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic/launch-command.json)；[command.txt](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261022-194758.json](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261022-194758.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic/server.log)；[gpu.csv](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261022T114435Z-current-mixed-native-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
