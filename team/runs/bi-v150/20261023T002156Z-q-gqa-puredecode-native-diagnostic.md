<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261023T002156Z-q-gqa-puredecode-native-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #185 · 当前版本GPU热点

- **尝试**：复用原轨迹并按需补短native诊断；GPU路径占比只用于选择下一实验，不作吞吐成绩。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：末次2109execute/252mixed，q1共4032、outside及未入plan均52（1.28968%），此前局部零遗漏判断已更正
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261023T002156Z-q-gqa-puredecode-native-diagnostic",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-23T00:21:56+00:00",
  "profile_id": "q_gqa_puredecode_native",
  "phase": "current422_puredecode_and_mixed_coverage",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "true",
  "status": "diagnostic_complete_no_performance_verdict",
  "artifacts": "experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic",
  "conclusion": "490原件已封存导入，独立reader与mixed摘要各运行一次。8 CPU步/8 GPU graph同PID、时钟和完整映射通过，N=M=31；graph中位52.3947ms，下一图已提前50.798–51.199ms提交；五内侧间隔2.0620–2.1179ms，可见GPU1.9035–1.9332ms，未覆盖0.1582–0.1985ms不是idle或收益。末次2109execute/252mixed，q1共4032、outside及未入plan均52（1.28968%），此前局部零遗漏判断已更正；无K加权、非forward、未保证全负载覆盖。DB前后554表/20517行三hash不变，exit0且最后device68MiB/0。"
}
```

</details>

## 原件与说明

- 原始目录：[20261023T002156Z-q-gqa-puredecode-native-diagnostic](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic)
- 原命令：[load-commands.json](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic/load-commands.json)；[launch-command.json](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic/launch-command.json)；[command.txt](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic/manifest.json)；[postflight-full.json](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic/postflight-full.json)；[purpose.json](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-082607.json](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-082607.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic/server.log)；[gpu.csv](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic/gpu.csv)；[exit-code](../../../experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
