<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T060209Z-qfragment-sourceproof-debug5-4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #209 · Q fragment 循环外保留

- **尝试**：把唯一BF16 prefill Attention的Q local_load移到唯一K循环外并保持fragment活跃。默认由提交代码启用，保留normal fallback与精确源码/ABI/IR检查；PR23已合入main。官方1536请求、两档各4轮验证中4K/16K为5313.59/3764.67 total tok/s，较PR15+PR21旧基线+3.80%/+9.56%；完整Math500 L3为100/105通过。实际选中且fallback0，shared65536→32768、循环内Q read0。DB种子相同但KV521840对521936，不包装为严格等KV单项因果。
- **改动**：相关实现 [qfragment-pr15-pr21-final.json](../../../analysis/qfragment-pr15-pr21-final.json)；[qfragment-adaptation.json](../../../analysis/qfragment-adaptation.json)；[biv150_q_fragment_service.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/biv150_q_fragment_service.py)；[compare_q_service_pair.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/compare_q_service_pair.py)；[q-fragment-service-pair.json](../../../analysis/q-fragment-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：前置debug3在normalized-over-gqa路径正确拒绝旧C2/源码行假设，fallback actual Q source location missing，候选未进入优化路径，不计性能负结果
- **是否保留**：保留适配失败/修复与选中证据；短诊断exit2，不作性能或准确率。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T060209Z-qfragment-sourceproof-debug5-4k",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T06:02:09Z",
  "profile_id": "q-fragment-hoist",
  "phase": "prefill_q_fragment_selection_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "51926ff8ea13a96ed4808e7f80cd7f353a6be3be",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "diagnostic_selected_cleanup_exit2_not_performance",
  "artifacts": "experiments/framework/20261024T060209Z-qfragment-sourceproof-debug5-4k",
  "conclusion": "前置debug3在normalized-over-gqa路径正确拒绝旧C2/源码行假设，fallback actual Q source location missing，候选未进入优化路径，不计性能负结果；修复后debug5出现Q_FRAGMENT_SELECTED、fallback0，shared65536→32768、循环内Q read=0。该短诊断run保留exit2与原始日志，只作适配证据，不作官方性能或准确率。详analysis/qfragment-adaptation.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T060209Z-qfragment-sourceproof-debug5-4k](../../../experiments/framework/20261024T060209Z-qfragment-sourceproof-debug5-4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261024T060209Z-qfragment-sourceproof-debug5-4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261024T060209Z-qfragment-sourceproof-debug5-4k/launch-command.json)；[command.txt](../../../experiments/framework/20261024T060209Z-qfragment-sourceproof-debug5-4k-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T060209Z-qfragment-sourceproof-debug5-4k/manifest.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261024-140405.json](../../../experiments/framework/20261024T060209Z-qfragment-sourceproof-debug5-4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261024-140405.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T060209Z-qfragment-sourceproof-debug5-4k/server.log)；[gpu.csv](../../../experiments/framework/20261024T060209Z-qfragment-sourceproof-debug5-4k/gpu.csv)；[exit-code](../../../experiments/framework/20261024T060209Z-qfragment-sourceproof-debug5-4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
