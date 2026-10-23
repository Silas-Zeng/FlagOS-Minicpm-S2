<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T142447Z-probe-gqa-engine-start-crash

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #139 · 专用 GQA decode attention kernel

- **尝试**：为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。
- **改动**：相关实现 [biv150_gqa_decode.py](../../../patches/framework/biv150_gqa_decode.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：4096 / 1024 / 64 / 64。
- **结果**：失败：`UnboundLocalError: cannot access local variable inspect where it is not associated with a value`（server.log 第 100、138 行，EngineCore 初始化阶段，KV cache 尚未分配，端口 9031 关闭）
- **是否保留**：未集成；失败或无收益记录保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T142447Z-probe-gqa-engine-start-crash",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T14:24:47+00:00",
  "profile_id": "gqa_decode_kernel",
  "phase": "server_start_crash_local_import_shadow",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "6f667fb",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "failed_engine_core_initialization",
  "artifacts": "experiments/operator/20261022T142447Z-probe-gqa-engine-start-crash",
  "conclusion": "门控键集真正写入后引擎启动即失败：`UnboundLocalError: cannot access local variable inspect where it is not associated with a value`（server.log 第 100、138 行，EngineCore 初始化阶段，KV cache 尚未分配，端口 9031 关闭）。原因是 install() 内仍保留原来的 `import inspect`，Python 把该名字视为函数局部，新增的安装期签名断言在其之前引用它就必然抛错。修复为删除局部 import 并在 scripts/debug_gate.py 里加同类静态检查；本轮不产生任何性能数字。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T142447Z-probe-gqa-engine-start-crash](../../../experiments/operator/20261022T142447Z-probe-gqa-engine-start-crash)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：[server.log](../../../experiments/operator/20261022T142447Z-probe-gqa-engine-start-crash/server.log)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
