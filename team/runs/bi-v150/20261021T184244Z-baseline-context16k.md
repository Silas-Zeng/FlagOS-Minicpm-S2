<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T184244Z-baseline-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #87 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：耗时观察范围120.48498157598到120.763262667693秒，相对跨度约0.23096745%，非稳定噪声统计估计；KV521936仍不同于CTA候选521840
- **是否保留**：保留作对照基线；不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T184244Z-baseline-context16k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T18:42:45.895958+00:00",
  "profile_id": "sql_mixed_clean_baseline_repeat",
  "phase": "short_context16k_baseline_capacity_repeat",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_same_kv_baseline_repeat_candidate_pool_diff_retained",
  "artifacts": "experiments/framework/20261021T184244Z-baseline-context16k",
  "conclusion": "独立410源SHA/e155/原bc51/SERVER/seed721201；32成功0失败/524288in4096out/120.763262667693s/4375.370359560136total/TTFT61145.738579274621ms；KV521936仍不同于CTA候选521840；DB实体3hash同51619270不变/CPU6/32768MiB/preempt0→0/完整post2026-10-21T18:46:25.582645+00:0068MiB0双栈闭无GPU进程；两基线同KV耗时观察范围120.48498157598到120.763262667693秒，相对跨度约0.23096745%，非稳定噪声统计估计；不刷容量/不加假buffer，整体同物理32GiB描述信号保留、未分离KV池变化成本；见analysis/2026-10-22-mm-cta-service-comparison.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T184244Z-baseline-context16k](../../../experiments/framework/20261021T184244Z-baseline-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T184244Z-baseline-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T184244Z-baseline-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261021T184244Z-baseline-context16k-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T184244Z-baseline-context16k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T184244Z-baseline-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T184244Z-baseline-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T184244Z-baseline-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T184244Z-baseline-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261022-024602.json](../../../experiments/framework/20261021T184244Z-baseline-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261022-024602.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T184244Z-baseline-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261021T184244Z-baseline-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261021T184244Z-baseline-context16k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
