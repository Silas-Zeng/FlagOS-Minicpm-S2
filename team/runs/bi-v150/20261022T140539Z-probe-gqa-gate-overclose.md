<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T140539Z-probe-gqa-gate-overclose

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #135 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：4096 / 1024 / 64 / 64。
- **结果**：失败原因
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T140539Z-probe-gqa-gate-overclose",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T14:05:39+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "warm_probe_candidate_after_gate_fix",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "a8cbba5",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "failed_gate_too_strict_all_calls_fell_back",
  "artifacts": "experiments/operator/20261022T140539Z-probe-gqa-gate-overclose",
  "conclusion": "把审查项“门控必须 fail-closed”实现成“_GATE_KEYS 全部键都出现在调用点”之后跑的第一轮：4K 缩放暖探针第 1 个 repeat total 3557.73 tok/s、TPOT 68.59 ms，与控制臂同水平而不是候选的 48 ms；日志只有 FIRST_FALLBACK（dummy 256/256）而没有 FIRST_WIDTH，说明每次真实调用都被拒。原因是被审计的 triton_attn 后端调用传 31 个关键字、不传 qq_bias，该键由函数默认值给出。修复方式是把“安装期对签名断言全部键存在”和“运行期只要求调用点实际传递的键”分开（_RUNTIME_KEYS 排除 qq_bias），复测分两步：20261022T141457Z 因为补丁脚本没有真正写回文件，门控仍然是全键要求，4K 第 1 个 repeat 仍是 3557.51 / TPOT 68.60；20261022T142447Z 则是修复写入后 install() 里残留的局部 import inspect 遮蔽了模块级名字，引擎启动即 UnboundLocalError。两轮都不保留为性能数字，只保留失败原因。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T140539Z-probe-gqa-gate-overclose](../../../experiments/operator/20261022T140539Z-probe-gqa-gate-overclose)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/operator/20261022T140539Z-probe-gqa-gate-overclose/server.log)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
