<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T205801248145Z-native-k8-sme-mixed-b-16384-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #526 · Attention 分流与 launch

- **尝试**：按首暖负向规则筛选Mixed N30/S4 SME B臂官方16K服务表现。
- **改动**：沿用main899共同服务，仅Mixed N30/S4/Q stride2048由B臂候选命中；负向首暖后受控早停。 版本、命令和源码见下方原件；[方法记录](../../methods/attention.md)。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 128。
- **结果**：16K只保留冷轮与首暖3871.73/4547.97，均128/128成功；首暖相对A首暖−0.0874%后受控早停，KV34277页；不是完整四轮或数值失败。
- **是否保留**：保留首暖负向早停原件；不补写未测轮次，不更新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T205801248145Z-native-k8-sme-mixed-b-16384-four-rounds",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T21:37:50.346333+00:00",
  "profile_id": "native-k8-sme-mixed",
  "phase": "official_16k_early_stop",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "899ce77470b0b539aebc108fd122f668c2d5894d",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "false",
  "status": "native_k8_sme_mixed_official16k_stopped_first_warm_negative",
  "artifacts": "experiments/bundles/20261029T205801248145Z-native-k8-sme-mixed-b-16384-four-rounds",
  "conclusion": "B保留冷轮与首暖共2轮，均128/128成功；首暖4547.97相对A首暖4551.95低0.0874%，监督器按规则主动SIGTERM早停。SIGTERM/KeyboardInterrupt及owner非零退出是受控早停，不是模型数值失败；不可冒充完整四轮。Mixed B marker与N30/S4/Q stride2048匹配，KV为34277页，3_6运行后DB SHA与A不同；无准确率或新基线资格。 Mixed selected marker记录数1（非总调用数）。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T205801248145Z-native-k8-sme-mixed-b-16384-four-rounds](../../../experiments/bundles/20261029T205801248145Z-native-k8-sme-mixed-b-16384-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T205801248145Z-native-k8-sme-mixed-b-16384-four-rounds/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
