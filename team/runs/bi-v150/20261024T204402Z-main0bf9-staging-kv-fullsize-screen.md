<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T204402Z-main0bf9-staging-kv-fullsize-screen

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #236 · PR25 与缓存修复后的 KV 保存恢复

- **尝试**：538 staging关闭回读，官方完整规模两档各两轮筛选。
- **改动**：本轮来源与原件见下方证据，限制见方法记录。
- **怎么测**：官方负载规模、每档两轮筛选；非官方四轮成绩；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 768。
- **结果**：538两轮：4K5544.36/5615.02，16K3845.32/4078.31，768成功；KV失配，只观察暖轮−2.38%/＋0.82%。
- **是否保留**：保留16K筛选信号，后续完整测量；KV失配不报因果收益，不更新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T204402Z-main0bf9-staging-kv-fullsize-screen",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T20:44:02Z",
  "profile_id": "pr25-kv-current",
  "phase": "fullsize_two_rounds",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "768",
  "profiler": "false",
  "status": "staging_screen_kv_mismatch",
  "artifacts": "experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen",
  "conclusion": "538 staging两档各两轮筛选，4K5544.36/5615.02、16K3845.32/4078.31 total tok/s，768请求全成功。暖轮相对526 R2观察4K−2.38%、16K＋0.82%；实际KV546528对基线547536，gain_calculated=false，只作绝对观察不宣称因果或稳定收益。21:13:53 UTC清理/source/native未变/DB恢复通过。保留16K正信号供后续完整测量，不更新accepted baseline，官方四轮与完整105结论待。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T204402Z-main0bf9-staging-kv-fullsize-screen](../../../experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen)
- 原命令：[command.txt](../../../experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen/manifest.json)；[source-sha256.json](../../../experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen-control/source-sha256.json)
- 原始结果：[raw_runs_screen.csv](../../../experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen/raw_runs_screen.csv)；[result.json](../../../experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen/server.log)；[gpu.csv](../../../experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen/gpu.csv)；[exit-code](../../../experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
