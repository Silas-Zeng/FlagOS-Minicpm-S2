<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #181 · KV 二维 FULL 恢复

- **尝试**：保留原页序、私有页资格和完成事件，合并H2D提交；独立单层字节门与真实42层事务分开记录，调用数下降不当作性能收益。
- **改动**：相关实现 [README.md](../../../archive/ai/20261022-framework-kv/q-gqa-kv-restore-pitch/README.md)；[kv-pitched-restore-method.json](../../../analysis/kv-pitched-restore-method.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32成功0失败，完整来源/原参数/DB544四端/真实FULL事务及consumer/无回读/清理均通过
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T22:35:40+00:00",
  "profile_id": "kv_restore_pitched",
  "phase": "restore_pitched_VERIFY0_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_confounded_KV_no_gain",
  "artifacts": "experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long",
  "conclusion": "候选425仅改FULL的H2D搬运，168.202863297s、3311.810447700 total tok/s，569原件全核；实际FULL672提交、原SAVE/所有权/完成事件保留。代码与正确性证据保留候选，不默认集成、暂不追加大测或accuracy。原bc51长16K+1024/c64/32请求/seed721201、VERIFY0、finiteunset；双方32成功0失败，完整来源/原参数/DB544四端/真实FULL事务及consumer/无回读/清理均通过。唯一失配为KV521840 vs 521936，31项门30真1假，gain=null；不重启凑容量，不确认收益。详analysis/q-gqa-kv-restore-pitched-verify0-pair.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-063948.json](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-063948.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
