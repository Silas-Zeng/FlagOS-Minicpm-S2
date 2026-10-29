<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T164536162881Z-native-k8-sme-dispatcher-build

平台：CPU。本页只摘录既有登记；未记录字段不补猜。

## 登记 #515 · NativeK8 SME布局与lookahead组件探针

- **尝试**：完整页K-stage字节布局探针通过；lookahead两臂standalone compile/ASM顺序门通过。新增producer+原reducer组件4-case结果逐位数值/Graph/input门全通过，Event改善2.07–2.73%，但4K Q stride2560 wall反向慢2.10%。均为组件/编译证据，不代表attention完整正确性、官方吞吐、模型准确率或生产资格。
- **改动**：相关实现 [experiment-note.md](../../../analysis/publication-k8-sme-20261029/experiment-note.md)；[native_k8_sme_A.cu](../../../experiments/bundles/20261029T155955570211Z-native-k8-sme-pair-build/source/native_k8_sme_A.cu)；[native_k8_sme_B.cu](../../../experiments/bundles/20261029T155955570211Z-native-k8-sme-pair-build/source/native_k8_sme_B.cu)；[worker.py](../../../experiments/bundles/20261029T161341635355Z-native-k8-sme-component/source/worker.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：A/B dispatcher SO均编译成功
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T164536162881Z-native-k8-sme-dispatcher-build",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T16:45:36+00:00",
  "profile_id": "native-k8-sme",
  "phase": "dispatcher_pair_build",
  "device": "CPU",
  "vllm_commit": "899ce77470b0b539aebc108fd122f668c2d5894d",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_k8_sme_dispatcher_build_pass",
  "artifacts": "experiments/bundles/20261029T164536162881Z-native-k8-sme-dispatcher-build",
  "conclusion": "A/B dispatcher SO均编译成功；source/SO身份及实际IR/SASS归档，双臂动态符号隔离，编译未初始化GPU或调用operator。仅CPU build证据，无数值或性能结论。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T164536162881Z-native-k8-sme-dispatcher-build](../../../experiments/bundles/20261029T164536162881Z-native-k8-sme-dispatcher-build)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T164536162881Z-native-k8-sme-dispatcher-build/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
