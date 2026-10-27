<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T084521Z-main6971-production-hotspot-4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #319 · main6971 Graph真实热点诊断

- **尝试**：保持生产源码，复用PR62诊断工具；Graph采样可用，fresh native FX证明缺项保留。图内插桩时间只用于排序，不作正常耗时或官方成绩。
- **改动**：相关实现 [posthoc.json](../../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/actual/posthoc.json)；[summary.md](../../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/posthoc-20261027/summary.md)；本轮准确变体以原件源码清单为准。
- **怎么测**：main6971/native14f，PR62诊断工具本站适配；3短warm＋1同负载warm＋1完整4K profile，c64、256请求、输出1024；生产源码和服务基准参数保留。
- **结果**：4K诊断256/256成功；Graph四samples、334bindings，API/数值/别名检查通过，实际prefill栈有效。无日志指向fresh FX，posthoc仍diagnostic_incomplete；正常退出、共享DB未变。不是官方吞吐/105。
- **是否保留**：保留可用Graph诊断，native FX缺口明示；分析实际热点，不把插桩时间当正常占比。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T084521Z-main6971-production-hotspot-4k",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T08:45:21.244028+00:00",
  "profile_id": "main6971-graph-profile",
  "phase": "diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "true",
  "status": "profile_graph_valid_missing_fresh_fx",
  "artifacts": "experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k",
  "conclusion": "4K诊断256/256成功；Graph四samples、334bindings，API/数值/别名检查通过，实际prefill栈有效。无日志指向fresh FX，posthoc仍diagnostic_incomplete；正常退出、共享DB未变。不是官方吞吐/105。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T084521Z-main6971-production-hotspot-4k](../../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/manifest.json)
- 原始结果：[puredecode-steps.csv](../../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/posthoc-20261027/puredecode-steps.csv)
- 日志 / 采样：[server.log](../../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/server.log)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
