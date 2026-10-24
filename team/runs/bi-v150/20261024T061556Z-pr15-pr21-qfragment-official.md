<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T061556Z-pr15-pr21-qfragment-official

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #207 · Q fragment 循环外保留

- **尝试**：把唯一BF16 prefill Attention的Q local_load移到唯一K循环外并保持fragment活跃。默认由提交代码启用，保留normal fallback与精确源码/ABI/IR检查；PR23已合入main。官方1536请求、两档各4轮验证中4K/16K为5313.59/3764.67 total tok/s，较PR15+PR21旧基线+3.80%/+9.56%；完整Math500 L3为100/105通过。实际选中且fallback0，shared65536→32768、循环内Q read0。DB种子相同但KV521840对521936，不包装为严格等KV单项因果。
- **改动**：相关实现 [qfragment-pr15-pr21-final.json](../../../analysis/qfragment-pr15-pr21-final.json)；[qfragment-adaptation.json](../../../analysis/qfragment-adaptation.json)；[biv150_q_fragment_service.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/biv150_q_fragment_service.py)；[compare_q_service_pair.py](../../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/compare_q_service_pair.py)；[q-fragment-service-pair.json](../../../analysis/q-fragment-service-pair.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：4096/16384 / 1024 / 64 / 256/128 x4。
- **结果**：第2–4轮均值4K5313.59、16K3764.67 total tok/s，较旧基线5118.99/3436.17为+3.80%/+9.56%
- **是否保留**：保留并已合并PR23；确认为最新BI-V150基准，KV失配边界随结果保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T061556Z-pr15-pr21-qfragment-official",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T06:15:56Z",
  "profile_id": "q-fragment-hoist",
  "phase": "official_throughput_best_baseline",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "4c57567d090bbb9aec1bbc2bef7847d3b4e5695a",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096/16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256/128 x4",
  "profiler": "false",
  "status": "official_pass_q_selected_no_fallback",
  "artifacts": "experiments/official/20261024T061556Z-pr15-pr21-qfragment-official",
  "conclusion": "PR15+PR21+Q fragment原官方两case各4轮全部成功，1536请求；第2–4轮均值4K5313.59、16K3764.67 total tok/s，较旧基线5118.99/3436.17为+3.80%/+9.56%。同起始DB种子但KV为521840对旧521936，作保守绝对对照；Q_FRAGMENT_SELECTED=1、fallback=0，shared65536→32768、LLVM循环内Q read=0。runtime commit4c57567/tree dd0554，已合并PR23；准确率另run为100/105。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T061556Z-pr15-pr21-qfragment-official](../../../experiments/official/20261024T061556Z-pr15-pr21-qfragment-official)
- 原命令：[benchmark-command.json](../../../experiments/official/20261024T061556Z-pr15-pr21-qfragment-official/benchmark-command.json)；[command.txt](../../../experiments/official/20261024T061556Z-pr15-pr21-qfragment-official-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261024T061556Z-pr15-pr21-qfragment-official/manifest.json)
- 原始结果：[raw_runs_20261024_141652.csv](../../../experiments/official/20261024T061556Z-pr15-pr21-qfragment-official/benchmark_results/raw_runs_20261024_141652.csv)；[summary_20261024_141652.csv](../../../experiments/official/20261024T061556Z-pr15-pr21-qfragment-official/benchmark_results/summary_20261024_141652.csv)；[result.json](../../../experiments/official/20261024T061556Z-pr15-pr21-qfragment-official/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261024T061556Z-pr15-pr21-qfragment-official/server.log)；[gpu.csv](../../../experiments/official/20261024T061556Z-pr15-pr21-qfragment-official/gpu.csv)；[exit-code](../../../experiments/official/20261024T061556Z-pr15-pr21-qfragment-official/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
