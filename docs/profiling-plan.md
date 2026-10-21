# 性能剖析计划

本文只记录**天数 BI-V150** 的 profiling 方案与既有证据。
团队另一平台沐曦－曦云 C500 由队友负责，其方案和结论单独维护，不能直接套用本页设置。
双平台分工见 [README](../README.md)。

本文保留早期诊断方案，供团队理解既有 trace 和复现方法，不代表当前新增待执行任务。
性能探索已冻结；设备归属和已授权的在途收尾以 [`CURRENT_WORK.md`](../CURRENT_WORK.md) 为准。

## 目的

将性能测量与 profiling 分开。官方 benchmark 保持不变，不能混入 profiler 开销。
profiling 使用独立服务进程，模型、dtype、cache 大小、调度设置和编译模式与对照一致，
只额外加入 vLLM 诊断用的 `profiler-config`。

## Trace 设计

### Prefill

- 使用官方 BI-V150 参数启动服务，额外加入 torch profiler 配置。
- 在诊断负载前开始采集。
- 按目标输入长度提交 64 个并发请求，输出长度保持较短。
- 采集五个 worker iteration。早期 iteration 包含 chunked prefill；
  此处的短输出诊断不作为性能结果。

### Decode

- 提交与已观察活跃并发数相同的请求数，避免留下等待中的请求。
- 等待 engine 日志显示 prompt throughput 为零、running 请求数稳定。
- 到这一阶段后才开始采集。
- 输出 token 数应足以让负载在 trace 采集期间持续运行。
- 4K 目标并发为 64；16K 使用实测活跃请求数。实际可见设备为 32 GiB，
  KV cache 无法同时容纳 64 个完整 16K context，因此预期活跃请求数较低。

## Trace 设置

- 采集 CPU 和 CUDA/CoreX 活动。
- 记录 tensor shape 与 dtype。
- 关闭 Python stack 采集，控制 trace 大小。
- 计时 trace 关闭内存事件；需要时另取分配快照。
- 自动采集限制为五个 worker iteration。
- 每个 trace 目录保留准确服务命令和 profiler JSON。

## 主要工具

- `start_profiled_server.sh`：启动启用 profiler 的诊断服务。
- `profile_control.sh start|stop|wait`：控制两个官方 profiler HTTP endpoint。
- `profile_workload.py`：发送长度精确的 token prompt，不改官方 benchmark。
- `capture_profile_prefill.sh` 与 `capture_profile_decode.sh`：提供可重复相位采集的上层入口。
- `stop_managed_server.sh`：发送 SIGTERM 前，核实 PID 属于预期的 MiniCPM vLLM 进程。

## 派生证据

每个相位报告：

- 按累计设备时间排序的主要 kernel 及占比；
- 调用次数、平均耗时和最大耗时；
- tensor shape 与 dtype；
- 按自身耗时排序的主要 CPU operator；
- 同步调用及与 launch 相关的空隙；
- GEMM、Attention、KV 更新、归一化、激活、旋转位置编码、采样和数据搬运分组；
- 候选优化的累计占比，以及按 Amdahl 定律计算的收益上限。

## 安全与有效性

- 启用 profiler 的结果不能与未启用 profiler 的结果直接作数值对照。
- CPU 与设备时间线会重叠，不能相加它们的百分比。
- 只有记录模型、revision、负载 shape、batch size 和编译模式的 trace 才可接受。
- 最终服务命令不能依赖 `--profiler-config` 或任何新增运行参数。
