<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T195932238481Z-native-k8-sme-mixed-build

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #522 · Attention 分流与 launch

- **尝试**：prefill、3D decode、mixed分流、可见prefix及重叠等路径；相关PR不等于各实验已包含或独立验证全部方法。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：16384 / — / — / —。
- **结果**：A/B CPU编译与真实SO反汇编通过；未运行attention/codec/reducer。
- **是否保留**：保留为组件候选；不作官方服务/准确率/新基线结论。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T195932238481Z-native-k8-sme-mixed-build",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T19:59:32.238481+00:00",
  "profile_id": "native-k8-sme-mixed",
  "phase": "mixed_sme_compile_only",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "899ce77470b0b539aebc108fd122f668c2d5894d",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "—",
  "concurrency": "—",
  "num_prompts": "—",
  "profiler": "false",
  "status": "native_k8_sme_mixed_compile_completed_cpu_only",
  "artifacts": "experiments/bundles/20261029T195932238481Z-native-k8-sme-mixed-build",
  "conclusion": "A/B 两库在 BI-V150 CoreX clang22 上 CPU compile-only 成功；未初始化 CUDA，未调用 attention、codec 或 reducer。A/B namespace 与 launcher 符号隔离，反汇编显示 B 的下一页 K SME 搬运在当前页 PV MMA 前发起并在后续消费前等待。此为编译/指令顺序证据，不是性能或模型服务成绩；保留为组件构建基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T195932238481Z-native-k8-sme-mixed-build](../../../experiments/bundles/20261029T195932238481Z-native-k8-sme-mixed-build)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T195932238481Z-native-k8-sme-mixed-build/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
