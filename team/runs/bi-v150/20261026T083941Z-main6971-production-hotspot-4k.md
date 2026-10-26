<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261026T083941Z-main6971-production-hotspot-4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #318 · main6971 Graph真实热点诊断

- **尝试**：保持生产源码，复用PR62诊断工具；Graph采样可用，fresh native FX证明缺项保留。图内插桩时间只用于排序，不作正常耗时或官方成绩。
- **改动**：相关实现 [posthoc.json](../../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/actual/posthoc.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：冻结main6971/618文件身份检查；原Driver未进入workloads。
- **结果**：诊断adapter把Git mode120000符号链接解引用，源码身份检查在CPU阶段拒绝；未启动collector/服务/GPU。修为校验linktarget字节后另run执行，原失败保留。
- **是否保留**：保留入口失败；v2单独登记，不当模型错误或性能负。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261026T083941Z-main6971-production-hotspot-4k",
  "local_date": "2026-10-26",
  "utc_start": "2026-10-26T08:39:41Z",
  "profile_id": "main6971-graph-profile",
  "phase": "diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6971ef48615af97a1637405c71f96dd89969563e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "profile_preflight_symlink_failed",
  "artifacts": "experiments/profiles/20261026T083941Z-main6971-production-hotspot-4k",
  "conclusion": "诊断adapter把Git mode120000符号链接解引用，源码身份检查在CPU阶段拒绝；未启动collector/服务/GPU。修为校验linktarget字节后另run执行，原失败保留。"
}
```

</details>

## 原件与说明

- 原始目录：[20261026T083941Z-main6971-production-hotspot-4k](../../../experiments/profiles/20261026T083941Z-main6971-production-hotspot-4k)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
