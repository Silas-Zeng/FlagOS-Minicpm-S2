<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T200440454229Z-native-k8-sme-mixed-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #523 · Attention 分流与 launch

- **尝试**：prefill、3D decode、mixed分流、可见prefix及重叠等路径；相关PR不等于各实验已包含或独立验证全部方法。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / — / — / —。
- **结果**：组件Event省7.7811%、wall省7.4730%，A/B输出逐位一致；不外推服务或基线。
- **是否保留**：保留为组件候选；不作官方服务/准确率/新基线结论。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T200440454229Z-native-k8-sme-mixed-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T20:04:40.454229+00:00",
  "profile_id": "native-k8-sme-mixed",
  "phase": "mixed_sme_component_screen",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "899ce77470b0b539aebc108fd122f668c2d5894d",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "—",
  "concurrency": "—",
  "num_prompts": "—",
  "profiler": "false",
  "status": "native_k8_sme_mixed_component_completed_screen",
  "artifacts": "experiments/bundles/20261029T200440454229Z-native-k8-sme-mixed-component",
  "conclusion": "BI-V150 N30/S4、Q pitch 2048 的 producer+原 reducer 隔离组件中，8个ABBA/BAAB顺序窗口（每臂4个，每窗8次） Event 均值 A 0.630725ms、B 0.581648ms（观察省7.7811%）；wall A 0.699091ms、B 0.646848ms（观察省7.4730%）。A/B partial、maximum、summation、reduced output逐位一致；混合边界、满16K、变Q、guard、只读及计时后复核通过。仅为组件局部观察：无独立FP64 oracle、actual writer/fullstep、Graph、官方服务或准确率；不更新基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T200440454229Z-native-k8-sme-mixed-component](../../../experiments/bundles/20261029T200440454229Z-native-k8-sme-mixed-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T200440454229Z-native-k8-sme-mixed-component/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
