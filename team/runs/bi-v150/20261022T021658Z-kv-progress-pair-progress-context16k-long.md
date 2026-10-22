<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T021658Z-kv-progress-pair-progress-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #112 · 抢占请求选择与进展

- **尝试**：抢占瞬间观察、请求选择及其对照；失配结果也保留。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：218.51338428491727s/2549.299219464107total/TTFT62356.0446958727ms
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T021658Z-kv-progress-pair-progress-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T02:17:02.207675+00:00",
  "profile_id": "progress_victim_pair_progress_candidate",
  "phase": "short_context16k_long_progress_VERIFY0_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_B_progress_selected_pair_KV_and_memory_mismatch_no_gain",
  "artifacts": "experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long",
  "conclusion": "本agent唯一3f1 progress引用A be286a95实际exit0/pass/report90f3c896；418/72942-5d9a-84be-e155/共同6a39fb/6ffb-1aaf/原bc51-SERVER-long-seed721201/VERIFY0，32-0/524288in32768out/218.51338428491727s/2549.299219464107total/TTFT62356.0446958727ms仅绝对值。KV521840vs A521936、启动nonTorch1004535808vs1000341504/available22443583692.8vs22447777996.8，4MiB分项差不归因；DB四端52319474三SHAdc2c7646-0dc7a465-c05d7e31同，CPU6/32GiB/原args包installed与约定source差匹配，environment_matchfalse且3收益字段全null，不raw时差报gain。actualPID253818/profile1/父真list/三恢复；9候选selected原index21/output392/rem632不同于tail30/output319，failed20，真实一次选择；SAVE-FULL-DROP同selected rid/R16768-P1048-721158144B/SAVE26段1092/目的66段2772/0ZERO/fast462/runner6/consumer9/host释放，无回读，原preempt0→1。02:22:42.575452Z418源live/68-0双栈闭无GPU进程，测前和shutdown ERROR空/WARN留；动态R/consumer等不套015315或要求与A相等。本首对已按root决定结束，不追加盲复跑/第三run或追容量，无性能/新accuracy/公平结论。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T021658Z-kv-progress-pair-progress-context16k-long](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-102156.json](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-102156.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T021658Z-kv-progress-pair-progress-context16k-long/exit-code)
- 相关说明：[2026-10-22-progress-pair-startup-geometry](../../../analysis/2026-10-22-progress-pair-startup-geometry.md)；[2026-10-21-framework-experiments](../../../analysis/2026-10-21-framework-experiments.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
