<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T152020Z-q-fragment-hoist-4k-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #148 · Q fragment 循环外保留

- **尝试**：把唯一BF16 prefill Attention的Q local_load移到唯一K循环外并保持fragment活跃。默认由提交代码启用，保留normal fallback与精确源码/ABI/IR检查；PR23已合入main。官方1536请求、两档各4轮验证中4K/16K为5313.59/3764.67 total tok/s，较PR15+PR21旧基线+3.80%/+9.56%；完整Math500 L3为100/105通过。实际选中且fallback0，shared65536→32768、循环内Q read0。DB种子相同但KV521840对521936，不包装为严格等KV单项因果。
- **改动**：相关实现 [qfragment-pr15-pr21-final.json](../../../analysis/qfragment-pr15-pr21-final.json)；[qfragment-adaptation.json](../../../analysis/qfragment-adaptation.json)；[biv150_q_fragment_service.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/biv150_q_fragment_service.py)；[compare_q_service_pair.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/compare_q_service_pair.py)；[q-fragment-service-pair.json](../../../analysis/q-fragment-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：wall2.464499437500→2.067650000000ms（缩短16.1026%），event2.358253240585→1.871338784695ms（缩短20.6473%），保留短KV局部正信号待真实服务验证
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T152020Z-q-fragment-hoist-4k-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T15:20:20.975042+00:00",
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
  "artifacts": "experiments/framework/20261022T152020Z-q-fragment-hoist-4k-gate",
  "conclusion": "同一Q fragment循环外保留方法，仅将D1/P2047合成fixture的KV16K改为4K，policy80d63不变。strict bits/完整KV/RNG/scale/新Q与输出指针/非默认流全过，误差0；真实TTGIR外提及LLVM循环内Q内存读0，shared64→32KiB、regs102→114、spill0。同worker32ABBA wall2.464499437500→2.067650000000ms（缩短16.1026%），event2.358253240585→1.871338784695ms（缩短20.6473%），保留短KV局部正信号待真实服务验证；不计为另一独立方法或与16K收益相加，无整模型准确率、服务、官方性能或C500结论。独立JIT缓存、原缓存未改、绑定已恢复；root46项seal全核复用。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T152020Z-q-fragment-hoist-4k-gate](../../../experiments/framework/20261022T152020Z-q-fragment-hoist-4k-gate)
- 原命令：[command.txt](../../../experiments/framework/20261022T152020Z-q-fragment-hoist-4k-gate-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T152020Z-q-fragment-hoist-4k-gate-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T152020Z-q-fragment-hoist-4k-gate/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T152020Z-q-fragment-hoist-4k-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T152020Z-q-fragment-hoist-4k-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T152020Z-q-fragment-hoist-4k-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T152020Z-q-fragment-hoist-4k-gate/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
