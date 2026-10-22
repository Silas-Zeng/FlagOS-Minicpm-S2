<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261021T183543Z-baseline-context16k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #85 · SQLite 反射及 SQL+C2/C3 组合

- **尝试**：目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。
- **改动**：相关实现 [biv150_sql_reflection.py](../../../patches/framework/biv150_sql_reflection.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 128 / 64 / 32。
- **结果**：32成功0失败/524288in4096out/120.484981575981s/4385.476040985142total/TTFT60874.430632247822ms；供CTA对照，KV521936不同于候选521840，描述比率不作严格容量归因，无新accuracy
- **是否保留**：保留作对照基线；不据此判断候选收益。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261021T183543Z-baseline-context16k",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-21T18:35:44.175524+00:00",
  "profile_id": "sql_mixed_clean_baseline",
  "phase": "short_context16k_service_pair",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_clean_control_kv_mismatch",
  "artifacts": "experiments/framework/20261021T183543Z-baseline-context16k",
  "conclusion": "独立审：32成功0失败/524288in4096out/120.484981575981s/4385.476040985142total/TTFT60874.430632247822ms；真实KV521936；DBbeforeafter实体1593/a0a590/90e9同51619270不变/CPU6/32768MiB/preempt0→0，post2026-10-21T18:40:20.990667+00:0068MiB0双栈闭无GPU进程；410源SHA/e155/bc51/原SERVER/context16K128out32reqc64seed721201；供CTA对照，KV521936不同于候选521840，描述比率不作严格容量归因，无新accuracy；详analysis/2026-10-22-mm-cta-service-comparison.json"
}
```

</details>

## 原件与说明

- 原始目录：[20261021T183543Z-baseline-context16k](../../../experiments/framework/20261021T183543Z-baseline-context16k)
- 原命令：[load-commands.json](../../../experiments/framework/20261021T183543Z-baseline-context16k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261021T183543Z-baseline-context16k/launch-command.json)；[command.txt](../../../experiments/framework/20261021T183543Z-baseline-context16k-control/command.txt)；[launch.sh](../../../experiments/framework/20261021T183543Z-baseline-context16k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261021T183543Z-baseline-context16k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261021T183543Z-baseline-context16k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261021T183543Z-baseline-context16k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261021T183543Z-baseline-context16k-control/source-sha256.json)
- 原始结果：[context-16k-infqps-concurrency64-minicpm-20261022-023900.json](../../../experiments/framework/20261021T183543Z-baseline-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261022-023900.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261021T183543Z-baseline-context16k/server.log)；[gpu.csv](../../../experiments/framework/20261021T183543Z-baseline-context16k/gpu.csv)；[exit-code](../../../experiments/framework/20261021T183543Z-baseline-context16k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
