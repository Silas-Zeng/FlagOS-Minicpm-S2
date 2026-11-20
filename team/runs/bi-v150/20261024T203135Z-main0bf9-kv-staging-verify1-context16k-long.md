<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #232 · PR25 与缓存修复后的 KV 保存恢复

- **尝试**：验证staging保存/恢复接入真实模型的字节、同步与释放。
- **改动**：本轮源码、版本与原始结果见下方证据；方法边界见[方法记录](../../methods/pr25-kv-current.md)。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32；另4题语义。
- **结果**：538 VERIFY1：32成功、4/4语义与34native图、每向729415680字节通过，42 kernels＋43 DMA/向；KV547536，非性能/105。
- **是否保留**：保留538服务字节与语义资格，关闭回读后再筛性能；不更新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-24T20:31:35Z",
  "profile_id": "pr25-kv-current",
  "phase": "kv_staging_verify1",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32；另4题语义",
  "profiler": "false",
  "status": "kv_staging_service_verify1_pass",
  "artifacts": "experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long",
  "conclusion": "538 staging真实服务VERIFY1：32请求成功，4/4语义、真实34层新图5f0f8337/FP3c96d895通过；42层每方向729415680字节一致，每向42个kernel＋43次DMA，临时staging双向释放通过；实际KV547536。20:37:42 UTC清理、source/native未变和DB恢复成功。含VERIFY1回读，不计性能或完整105；保留进入关闭回读的筛选，下一轮未纳入本批。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long](../../../experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long/manifest.json)；[source-sha256.json](../../../experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261025-043731.json](../../../experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261025-043731.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261024T203135Z-main0bf9-kv-staging-verify1-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
