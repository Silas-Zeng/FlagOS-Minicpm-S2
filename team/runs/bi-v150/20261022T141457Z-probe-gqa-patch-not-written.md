<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T141457Z-probe-gqa-patch-not-written

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #138 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：4096 / 1024 / 64 / 64。
- **结果**：失败，同时暴露“改动未落地也算改过”的流程缺陷
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T141457Z-probe-gqa-patch-not-written",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T14:14:57+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "warm_probe_candidate_gate_still_closed",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "a8cbba5043953f5a4416ae927d56519a111e1ea8",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "failed_validation_fix_never_written",
  "artifacts": "experiments/operator/20261022T141457Z-probe-gqa-patch-not-written",
  "conclusion": "以为已经修好门控后的第一次复测：4K 缩放暖探针第 1 个 repeat total 3557.51、TPOT 68.60 ms，与 #124 控制臂同水平；server.log 无 FIRST_WIDTH。根因不在服务而在改动流程：拆分键集的补丁脚本只做了字符串替换、没有 write_text，实际提交 23e6968 只含 `+import inspect`。该轮因修复未生效而失败，同时暴露“改动未落地也算改过”的流程缺陷；本轮及 20261022T142447Z 一起作为失败留档，之后 debug_gate.py 加了离线门控评测与 install() 局部导入遮蔽静态检查。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T141457Z-probe-gqa-patch-not-written](../../../experiments/operator/20261022T141457Z-probe-gqa-patch-not-written)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/operator/20261022T141457Z-probe-gqa-patch-not-written/server.log)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
