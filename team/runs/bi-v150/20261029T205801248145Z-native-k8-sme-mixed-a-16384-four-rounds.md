<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T205801248145Z-native-k8-sme-mixed-a-16384-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #525 · Attention 分流与 launch

- **尝试**：筛选Mixed N30/S4 SME A臂在官方16K服务中的吞吐表现。
- **改动**：沿用main899共同服务，仅Mixed N30/S4/Q stride2048由A臂候选命中；保留原官方服务参数。 版本、命令和源码见下方原件；[方法记录](../../methods/attention.md)。
- **怎么测**：原官方吞吐对照；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 128。
- **结果**：16K四轮总吞吐3906.33/4551.95/4548.63/4545.77，弃首暖4548.78；128/128每轮成功，KV34271页，未测准确率。
- **是否保留**：保留完整官方四轮记录；DB/KV条件及配对限制见本轮，暂不更新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261029T205801248145Z-native-k8-sme-mixed-a-16384-four-rounds",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-29T20:58:29.758470+00:00",
  "profile_id": "native-k8-sme-mixed",
  "phase": "official_16k_screen",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "899ce77470b0b539aebc108fd122f668c2d5894d",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "128",
  "profiler": "false",
  "status": "native_k8_sme_mixed_official16k_completed_four_rounds",
  "artifacts": "experiments/bundles/20261029T205801248145Z-native-k8-sme-mixed-a-16384-four-rounds",
  "conclusion": "A完成4轮官方16K，每轮128/128成功；Total tok/s为3906.33/4551.95/4548.63/4545.77，弃首轮均值4548.78。运行中出现一次N30/S4/Q stride2048 Mixed A host-selection marker（非请求覆盖数）；KV为34271页，3_6调优DB运行后SHA改变。无准确率或新基线资格。 Mixed selected marker记录数1（非总调用数）。"
}
```

</details>

## 原件与说明

- 原始目录：[20261029T205801248145Z-native-k8-sme-mixed-a-16384-four-rounds](../../../experiments/bundles/20261029T205801248145Z-native-k8-sme-mixed-a-16384-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261029T205801248145Z-native-k8-sme-mixed-a-16384-four-rounds/manifest.json)
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
