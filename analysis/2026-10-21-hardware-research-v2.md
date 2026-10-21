# BI-V150 hardware research, second pass

研究时间：2026-10-21，Asia/Shanghai。范围为资料检索、本地源码和历史日志阅读；本任务没有连接远端、启动 GPU 工作或修改运行环境。

## 新证据与适用边界

| 事项 | 证据与结论 | 对本实例的含义 |
|---|---|---|
| 板卡与 CUDA device 并非一一对应 | Iluvatar 的 [ix-device-plugin README](https://github.com/Deep-Spark/ix-device-plugin#split-gpu-board-to-multiple-gpu-devices) 明确以 BI-V150 举例：一板有两个 GPU 芯片，`splitboard=true` 时可向 Kubernetes 分别公布。厂商参与维护的 [llm-d 适配文档](https://llm-d.ai/docs/dev/getting-started/accelerators#iluvatar) 明确 32 GiB/die、64 GiB/board。 | 当前一个可见 device、32 GiB 与暴露单 die 相符；仍需实例资源配置才能确认具体分配方式。不要把 32 GiB 自动解释为任意虚拟分区，也不要按 64 GiB 全板容量或吞吐建模。 |
| 原生 warp 为 64 有编译器源码佐证 | [FlagTree Iluvatar compiler](https://github.com/flagos-ai/FlagTree/blob/main/third_party/iluvatar/backend/compiler.py) 的 `CorexOptions.warp_size=64`；[driver](https://github.com/flagos-ai/FlagTree/blob/main/third_party/iluvatar/backend/driver.py) 的 `get_current_target()` 返回 `GPUTarget("corex", capability, 64)`。 | 可用来检查框架生成的 launch 和布局是否有 32-lane 假设。4/8 warps 通常对应 256/512 threads。不能把 NVIDIA 的 occupancy、barrier、TMA 或 PDL 能力从 `sm71` 兼容标记直接推导过来。引用的 main 是研究资料，不是建议升级框架；安装版本仍需本地源码核对。 |
| PCIe/HBM 与当前实例带宽仍要分开 | 原有 [模力方舟部署平台文档](https://moark.com/docs/compute/clusters_gpu/iluvatar/iluvatar_BI-V150_gpu) 列出整板 HBM2e、PCIe 4.0 x16、64 GB；该站是平台文档，不应再称为芯片厂商原始说明书。 | 本轮没有找到足以证明当前 device 的实际 HBM 带宽、PCIe 协商宽度、DMA engine 数量的一手测量。不能按全板宣传带宽一半估算本实例，也不能把 H2D 时间当成 HBM 带宽。 |
| 图模式受镜像和后端共同影响 | llm-d 页面说其 CoreX 镜像默认 eager、需 `VLLM_ENFORCE_CUDA_GRAPH=1`；本项目 a9/a10 日志则已经明确 `enforce_eager=False`、`FULL_DECODE_ONLY` 和 35/35 graph capture。 | 外部镜像的环境变量不应搬进本实例。当前应优化图外路径与图内存，不能把“开启图”当作尚未做的工作。配置日志列了 51 个候选尺寸，但实际 capture 为 35 个；两种计数不能混用。 |
| CPU 可见核数不能代表配额 | 主负责人本轮只读采集确认 **cgroup v1**：`cpu.cfs_quota_us=600000`、`cpu.cfs_period_us=100000`，即 6 核 CPU 时间；累计 `nr_periods=339885`、`nr_throttled=888`、`throttled_time=3206440314906 ns`。[Linux CFS 文档](https://www.kernel.org/doc/html/latest/scheduler/sched-bwc.html) 说明其 quota/period 与累计计数含义。 | 累计节流只能证明过去发生过，不能据此断言当前瓶颈。112 个可见 CPU 不是可用配额。需用同一短负载前后的计数增量与 GPU 提交间隙联合判断，并注意祖先 cgroup 的限制。 |

## 优先假设一：减少 block-table 的重复 H2D

这是最明确的框架与 KV 接口共同问题，第一版可以完全不改 attention kernel。

[vLLM v0.24.0 BlockTable](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/worker/block_table.py) 中，`commit_block_table(num_reqs)` 调用 `copy_to_gpu(num_reqs)`；只按活动行裁剪，保留每行的最大上下文列数。当前 max-model-len 131072、block size 16 对应每行 8192 个 int32。已有 a3 trace 显示每步约 54–56 行、约 1.7–1.75 MiB 的同类上传，示例设备时间约 69.5 微秒。该 trace 的发现详见 `CURRENT_WORK.md`；不是新增性能测量。

建议第一版保留 GPU buffer 的容量、地址、stride，仅追踪 `append/add/move/swap/clear` 是否产生脏数据。**零脏时跳过上传；有脏时仍走原来连续的活动行全前缀上传路径。** 这与主负责人选择的最小候选一致，可缩小正确性验证范围。decode 的页表通常只在分配新 block 或请求变更时改变，不应把每步 positions/seq_lens 的变化误当成页表变化。

后续仅在第一版有收益且仍有充分瓶颈证据时，才考虑合并相邻脏行或缩短有效列。4K/16K 请求初始仅约 256/1024 列，而不是 8192 列；但这可能变成非连续拷贝或额外 packing，应单独测量。不要每行各发一次小 memcpy 把调用开销重新引入；本轮最短必要验证不扩展到这些方案。

必须覆盖请求完成后的行复用、move/swap、抢占与恢复、prefix sharing、跨 block 边界、异步上传源 buffer 的生命期。固定 GPU 地址避免破坏既有 graph replay；pinned host buffer 不能在 DMA 完成前被下一步改写。

**证据**：逐步记录脏行数、提交字节数和 memcpy 次数，检查图回放和输出一致，随后由设备负责人做相同负载串行 A/B。**反证**：上传被其他工作完全隐藏，或脏行管理/多个小 copy 抵消收益。用户最新要求是小而稳定的收益也保留，不以1%作为研发淘汰线。即使完全消除 69.5 微秒单次 copy，也不能据此许诺百分之几的整模型提升。

## 优先假设二：配额感知的 CPU 并行与元数据流水

本实例的 6 CPU 分配、112 可见核和 20 GiB RAM 限制，使“按宿主核数扩线程/固定大量 pinned memory”尤其值得检查。采用 cgroup quota、cpuset、线程状态与 GPU 提交间隙联合判断，不先做大范围参数扫描。

实施候选是让插件/worker 初始化尊重实际 CPU 配额，节制 tokenizer、OpenMP/MKL 的并行，并使用固定复用的 metadata staging buffer。保留官方服务参数，把策略做成通用资源探测代码；不修改系统 cgroup、不按官方并发硬编码。前端、engine 和 benchmark 在同 cgroup 时也会共享配额，比较必须固定客户端/服务的 CPU 工作布局。

**证据**：相同负载下 `cpu.stat` 增量、CPU pressure、线程数、每步 metadata 耗时、GPU submission gaps 同步改善。**反证**：没有配额节流，设备连续满载，或缩线程后 tokenization/调度成为瓶颈。此时不继续押注 host 调优。

对于拷贝重叠，[PyTorch 官方教程](https://docs.pytorch.org/tutorials/intermediate/pinmem_nonblock.html) 区分了“host 不阻塞”与“device 上 copy/compute 重叠”：需要 pinned source、独立 stream 和空闲 DMA engine。逐次 `pin_memory()` 本身会阻塞 host。CoreX 的实际重叠能力未在本轮验证，因此不能只增加 `non_blocking=True` 就宣称流水改善；优先减少多余工作，再用 event 管理复用 buffer 的生命周期。

## 优先假设三：图覆盖率与持久 buffer 的内存账本

当前已经是 `FULL_DECODE_ONLY`；模型主体图回放外仍有 metadata 和 sampler。按 [vLLM 图设计](https://docs.vllm.ai/en/latest/design/cuda_graphs/) 区分纯 decode、混合 prefill 和 fallback 后，先查每步图外 launch/sync 是否形成空洞，再考虑把稳定的后处理子路径单独捕获。若随机采样涉及 RNG，必须保证 replay 更新 RNG 状态并保持独立请求的正确性；不允许为了图捕获固定随机数或复用结果。

另建内存账本：model、KV、graph pool、workspaces、metadata buffer 各占多少，尤其比较 capture 前后 `mem_get_info` 和 KV token capacity。上游 [v0.24.0 GPUModelRunner](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/worker/gpu_model_runner.py) 已计算 graph capture 的内存差值，可围绕现有流程补诊断，不需要升级框架。

本模型为 42 层、2 KV heads、head dim 128、BF16，因此常规 K+V 每 token 是 `42*2*2*128*2=43008` bytes（42 KiB，不含分配/对齐开销）。一条 16K prompt 约 672 MiB KV；要让有效并发增加一条，通常需要这个量级的可用 KV 增量，再加输出余量。省出几十 MiB 的小 buffer 不足以自动跨过这个门槛。

**证据**：关键路径 graph 外 launch/sync 的缩短，或实际 KV token capacity/有效并发增加，并在相同运行参数下带来吞吐改善。**反证**：只有启动更快、图数量更少，但稳态速度和 KV 容量未变；或少捕获图导致合法大 batch fallback 更慢。不能按评测并发 64 裁掉更大图作为通用优化。

## 本轮建议顺序

cgroup 配额已由主负责人核实。先核对当前 block-table 代码，实现零脏跳过 H2D、有脏保留原路径；独立评审后由唯一 GPU owner 做最短必要正确性与串行 A/B。CPU 线程方案须有当前负载节流证据才实施。图/内存方案先建立账本，不扩展无证据的参数扫描。全部遵守现有赛规和官方参数。

保留原硬件笔记中已做过的短筛选结论，但其 4K/16K 同时负载不能彻底排除串行单场景收益。本轮不重跑 batch/page 参数穷举，也不把框架优化理解为禁止任何必要的小型 device 实现。
