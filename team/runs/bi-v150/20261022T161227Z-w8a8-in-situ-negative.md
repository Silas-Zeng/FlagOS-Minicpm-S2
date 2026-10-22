<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T161227Z-w8a8-in-situ-negative

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #144 · int8 与 W8A8 决策测量

- **尝试**：真实形状上的 int8 GEMM、W8A16、_int_mm+融合 epilogue 及 QDQ 精度模拟；负结果与候选并存，不混用证据级别。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 16。
- **结果**：即 int8 链在服务里比 bf16 **慢约 47%**，prefill 与 decode 同时变差
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T161227Z-w8a8-in-situ-negative",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T16:12:27+00:00",
  "profile_id": "int8_decision",
  "phase": "warm_probe_16k_in_situ",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "db55579",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "16",
  "profiler": "false",
  "status": "complete_negative_in_situ",
  "artifacts": "experiments/operator/20261022T161227Z-w8a8-in-situ-negative",
  "conclusion": "W8A8 真正执行后的首个端到端结果，**负结果**。前三轮之所以显示“精确零效果”，是因为 torch_compile_cache 热命中，运行时跑的还是旧 bf16 图；清缓存后先暴露不可追踪代码（`str(tuple(x.shape))` → Unsupported、动态 token 数上的 for 分块 → ConstraintViolation），最终把整条链（含小 M 回退）包进 `torch.library.custom_op(\"biv150_fl::w8a8_linear\")` 才启动成功。执行后的 16K 缩放暖探针（16384x1024x64x16，3 repeat 的第 1 个，valid=1）：total **1721.67 tok/s**、TPOT **112.72 ms**、TTFT 41231 ms，而同一实例、同一探针、kernel-only 是 3236.25 / 56.35 ms。即 int8 链在服务里比 bf16 **慢约 47%**，prefill 与 decode 同时变差。GPU KV 也从 521936 掉到 486464（−6.8%）。与孤立微测（M=2048/8192 快 1.22–1.54x）方向相反，最可能是每次层调用都要走一次 custom op 的 Python 分发：126 层 × 每步一次，TPOT 的 +56 ms 与这个量级吻合。结论：在这套 fullgraph 编译栈里，把逐层 GEMM 换成“Python custom op + 多 kernel”不成立；若还要继续，必须换成编译器能原生捕获的算子（C++/原生 Triton op，无 Python 分发），或只在 eager prefill 段生效并承担对应的 prefill 回归。本轴暂不进入提交，补丁保持默认关闭。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T161227Z-w8a8-in-situ-negative](../../../experiments/operator/20261022T161227Z-w8a8-in-situ-negative)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
