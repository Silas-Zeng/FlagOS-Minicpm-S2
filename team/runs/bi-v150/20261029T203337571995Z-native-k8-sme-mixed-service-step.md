<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T203337571995Z-native-k8-sme-mixed-service-step

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #524 · Attention 分流与 launch

- **尝试**：验证Mixed N30/S4候选的encode_append、producer与原reducer全步数值边界。
- **改动**：仅覆盖Q stride2048的N30/S4；A/B输出逐位一致并通过独立FP64复核，无性能计时。 版本、命令和源码见下方原件；[方法记录](../../methods/attention.md)。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：16384 / 未记录 / 未记录 / 未记录。
- **结果**：Mixed真实encode_append→producer→原reducer；N30/S4十个全步case通过，A/B输出逐位一致并通过独立FP64复核；没有性能计时。
- **是否保留**：保留为N30/S4有限形状正确性证据；没有服务性能、准确率或基线资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T203337571995Z-native-k8-sme-mixed-service-step",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T20:33:37.571995+00:00",
  "profile_id": "native-k8-sme-mixed",
  "phase": "mixed_fullstep_correctness",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "899ce77470b0b539aebc108fd122f668c2d5894d",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_k8_sme_mixed_fullstep_correctness_pass",
  "artifacts": "experiments/bundles/20261029T203337571995Z-native-k8-sme-mixed-service-step",
  "conclusion": "main899 声明载体上的 Mixed K8 SME A/B 全步正确性检查：实际 encode_append→A/B producer→原 reducer，N30/S4、Q stride2048；5个KV长度（16384、16385、17407、17408、17409）×2个Q phase，共10 case。A/B八个输出逐位一致，独立FP64门重算通过，预期cache写入及输入只读/guards检查通过，owner exit0且清理完成。仅为有限形状正确性证据；没有writer/fullstep性能计时、官方服务、Graph或准确率结果，不更新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T203337571995Z-native-k8-sme-mixed-service-step](../../../experiments/bundles/20261029T203337571995Z-native-k8-sme-mixed-service-step)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T203337571995Z-native-k8-sme-mixed-service-step/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
