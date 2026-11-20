<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T160148Z-native-direct-q-v2-4k-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #442 · 完整官方吞吐对照

- **尝试**：按原官方4K四轮口径筛选direct-Q v2。
- **改动**：direct-Q v2官方构建；原benchmark与服务参数、1024请求及四轮规则不变。 版本、命令和源码见下方原件；[方法记录](../../methods/official.md)。
- **怎么测**：原4K官方脚本、服务参数及四轮弃首轮口径；路径资格、恢复和清理均通过。
- **结果**：官方4K四轮完整、1024请求成功；弃首暖均6537.81，对基线6627.816667为−1.358014%；首暖+0.424135%，故跑满。
- **是否保留**：保留完整负结果并停止direct-Q；KV548432对548336不匹配，不作严格因果，不跑16K/105、不改基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T160148Z-native-direct-q-v2-4k-four-rounds",
  "local_date": "2026-10-28",
  "utc_start": "20261028T160148Z",
  "profile_id": "native-q32-direct-q-v2-official-4k",
  "phase": "official",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "256",
  "profiler": "false",
  "status": "native_q32_direct_q_v2_official4k_complete_negative",
  "artifacts": "experiments/official/20261028T160148Z-native-direct-q-v2-4k-four-rounds",
  "conclusion": "官方4K完成原四轮、1024请求成功；首暖6468.67对6441.35 +0.424135%，按规则跑完；弃首三轮均6537.81对6627.816667 -1.358014%。路径资格、恢复清理通过。KV548432对548336不匹配，不作严格因果；direct-Q本组停止，不跑16K/105、不改基线。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T160148Z-native-direct-q-v2-4k-four-rounds](../../../experiments/official/20261028T160148Z-native-direct-q-v2-4k-four-rounds)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
