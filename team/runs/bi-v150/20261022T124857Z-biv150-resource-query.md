<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T124857Z-biv150-resource-query

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #141 · 其它登记与控制记录

- **尝试**：没有足够字段继续归类的登记；不补猜实验结论。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：实际SDK只读属性查询exit0：BI-V150/32GiB/16SM/warp64
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T124857Z-biv150-resource-query",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T12:48:57Z",
  "profile_id": "biv150_resource_query",
  "phase": "read_only_device_attributes",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_readonly_not_perf",
  "artifacts": "experiments/framework/20261022T124857Z-biv150-resource-query",
  "conclusion": "实际SDK只读属性查询exit0：BI-V150/32GiB/16SM/warp64；每SM shared131072B、register262144、threads8192，每block threads4096/shared与optin131072B，L2 16MiB。19项属性全返回0，primary context前后inactive，前后68MiB0/双栈闭。仅硬件元数据，不是占用率或性能门；max blocks/SM和live kernel属性未观察。17seal逐SHA核验；collector57326及root runner归档，仅保SDK头SHA清单不上传原文。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T124857Z-biv150-resource-query](../../../experiments/framework/20261022T124857Z-biv150-resource-query)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：[exit-code](../../../experiments/framework/20261022T124857Z-biv150-resource-query/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
