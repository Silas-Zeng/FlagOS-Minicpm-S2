<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T135941Z-q-fragment-hoist-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #147 · Q fragment 循环外保留

- **尝试**：同一方法的KV16K/4K局部门与真实服务配对分别记录；保留单轮正信号，TTFT变化及准确率边界同时展示。
- **改动**：相关实现 [biv150_q_fragment_service.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/biv150_q_fragment_service.py)；[compare_q_service_pair.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/compare_q_service_pair.py)；[q-fragment-service-pair.json](../../../analysis/q-fragment-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wall11.028873859375→8.811432640625ms（缩短20.1058%），event10.930427551270→8.604556560516ms（缩短21.2789%），保留局部正信号待真实服务验证
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T135941Z-q-fragment-hoist-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T13:59:41.242388+00:00",
  "profile_id": "q_fragment_hoist",
  "phase": "actual_layer_q_fragment_lifetime",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_positive_single_layer_signal",
  "artifacts": "experiments/framework/20261022T135941Z-q-fragment-hoist-gate",
  "conclusion": "2D Attention的Q dot-layout local_load移到KV循环外并保留Q fragment；原w8/BM128/T64/s1，不叠Vlate/cache。D1/P2047/KV16K真实backend合成上界fixture，strict bits/完整KV/RNG/scale/新Q与输出指针/非默认流全过，误差0；真实TTGIR外提及LLVM循环内Q内存读0，shared64→32KiB、regs102→114、spill0，不据此宣称occupancy倍增。同worker32ABBA wall11.028873859375→8.811432640625ms（缩短20.1058%），event10.930427551270→8.604556560516ms（缩短21.2789%），保留局部正信号待真实服务验证；无整模型准确率、服务或官方性能结论。独立JIT缓存、原缓存未改、绑定已恢复；root46项seal全核复用。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T135941Z-q-fragment-hoist-gate](../../../experiments/framework/20261022T135941Z-q-fragment-hoist-gate)
- 原命令：[command.txt](../../../experiments/framework/20261022T135941Z-q-fragment-hoist-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T135941Z-q-fragment-hoist-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T135941Z-q-fragment-hoist-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T135941Z-q-fragment-hoist-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T135941Z-q-fragment-hoist-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T135941Z-q-fragment-hoist-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T135941Z-q-fragment-hoist-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
