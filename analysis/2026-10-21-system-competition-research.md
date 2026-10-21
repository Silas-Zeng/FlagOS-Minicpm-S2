# 整模型比赛与系统层优化：一手证据和下一步

研究日期：2026-10-21，Asia/Shanghai。仅做公开资料和本地证据阅读；没有连接远端、启动 GPU 作业或修改任何参考仓库。

## 结论

下一步优先验证 **KV block table 没有变化时跳过原样 H2D 复制**。dirty 时完整走原提交路径，保留原 GPU tensor 地址、原布局和原注意力实现。这个改动比继续修改算子数值路径更适合当前要求，也能用很小的验证发现错误。

之后的两个候选是 pure-decode 输入准备快路、确定性 logits/filter 阶段的子图捕获。两者均先要求本地计时证明相关 CPU 开销暴露在关键路径上。现有 async scheduling、decode graph 已经开启，不能把“开启异步/执行图”当作新增优化。

所有建议均保持官方启动参数、benchmark、模型、精度和现有采样参数；不按测试并发 64 硬编码，不合并新框架分支，不直接切到已有算子实现。下面的预计机制不是本设备的性能结论。

## 一手比赛/公开评测证据

| 来源与真实日期 | 观察到的机制 | 证据边界及本项目启发 |
|---|---|---|
| [AMD MLPerf Inference v5.0 技术报告](https://rocm.blogs.amd.com/artificial-intelligence/mi325x-accelerates-mlperf-inference/README.html)，2025-04-02 | 多步 decode 调度摊薄 CPU 工作；调度产生的实际形状决定 GEMM 与注意力效率。 | 这是 Llama2-70B 整模型提交经验，含不同精度、多卡和专用 harness。其超大 batch 策略与本项目的 16-SM 切片不等价；这里只借鉴减少每步重复 host 工作的机制。 |
| [AMD MLPerf Inference v5.1 技术报告](https://rocm.blogs.amd.com/artificial-intelligence/mlperf-inference-v5.1/README.html)，2025-09-09 | HipGraph 与 CPU 调度优化配合；报告还使用 Cython。 | 报告中 MI355X Llama2-70B MXFP4 是 Open/Offline 项，不能当作本项目 BF16、HTTP 服务的同条件成绩。没有单独消融可以把总收益归因给 Cython；不建议照抄其 `-Ofast`。 |
| [AMD MLPerf Inference v6.1 技术报告](https://rocm.blogs.amd.com/artificial-intelligence/mlperf-inf-v6.1/README.html)，2026-09-17；文中结果发布日期为 2026-09-16 | prefill/decode 使用不同计算路径，graph capture/warmup 覆盖实际 decode batch 形状；调度与在途工作配合。 | 是整模型 Closed 提交体系，但模型、MXFP4/FP8、8 卡或更多卡与这里不同。其 attention 25–28% 是 attention 局部改善，不是 MiniCPM 端到端提升；不迁移这些百分比。 |
| [vLLM GPT-OSS 优化报告](https://vllm.ai/blog/2026-02-01-gpt-oss-optimizations)，2026-02-01 | async scheduling 重叠 CPU 准备和 GPU；输出序列化也可能成为瓶颈。 | 属于框架团队公开性能报告，不是 FlagOS 比赛成绩。其高并发 stream interval 改动涉及输出行为，本项目不改该参数。异步本地已开启，剩下要查的是重叠之后仍暴露的工作。 |
| [vLLM Artificial Analysis 部署技术报告](https://vllm.ai/blog/2026-05-11-vllm-tops-artificial-analysis)，2026-05-11 | 小 batch 下消除很多细小 launch；算法选型同时服从 shape 与单图兼容约束。 | 属于公开服务评测的作者报告，包含量化、MoE 和投机等部分，不是可迁移的本地成绩。可复用的只有“先看执行图边界和形状，再决定是否需动算子”的方法。 |

上述不是单算子竞赛排行榜。反过来，单算子微基准的胜利也不能替代本项目整模型门槛；本仓库 decode attention 更快却导致 math_500 降到 83.8% 的负结果，已经说明这一点。

## 当前源码把机会限定在哪里

本地已知环境：官方插件 `13eb9be`、FlagGems `v5.3.5`、vLLM 0.24.0、BI-V150 单卡 32 GiB、MiniCPM5-2B BF16。参考是版本固定的一手源码，实施前仍需对照已安装文件，不能把 GitHub main 视作本地代码。

1. [`BlockTable` v0.24.0](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/worker/block_table.py)：CPU 管理 append/add/clear/move/swap，`commit_block_table(num_reqs)` 直接提交活动行前缀。
2. [`CpuGpuBuffer` v0.24.0](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/utils.py)：`copy_to_gpu(n)` 复制 `[:n]`，二维 tensor 的列宽随之全部复制。
3. [`GPUModelRunner` v0.24.0](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/worker/gpu_model_runner.py)：每步准备输入先提交 block table；通用输入路径构造 repeat/cumsum；`compute_logits` 和 sampling 在 model forward 之后。该版本已有异步事件保护和 GPU slot mapping，不能将它们重做后称为新增。
4. [`TRITON_ATTN` v0.24.0](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/backends/triton_attn.py)：支持 graph；分段 softmax buffer 及 kernel 分支与 query/KV heads、batch threshold、capture sizes 有关联。框架层“改形状”也可能改变底层执行路径，必须验证。

据 131072 最大长度、block16 推算，未被其他上限裁剪时列宽可达 8192 个 int32。64 行完整提交约 2 MiB/步，30 行约 0.94 MiB/步。这是源代码尺寸推算，**不是已确认的本地拷贝量**，必须用本地实际 tensor shape 或 memcpy bytes 核对。

旧 decode trace 中 memcpy 总共约 398 微秒/4 个被采样迭代，但 transformer graph 的内部 kernel 没有完整展开。不能拿这 398 微秒除以“可见 kernel 时间”来计算整模型占比；CPU profiler 开销也不能直接作为延迟预算。参见本地 `analysis/2026-10-21-bottleneck-profile.md`。

## 候选 1：zero-dirty block table 提交跳过

### 最小实现

- 每个 `BlockTable` 保留 CPU 修改代数或 dirty 状态；初始化为 dirty。
- 实际修改 CPU 表的 append/add/clear_row/move_row/swap_row 全部标记 dirty；`clear()`、重建、capture/dummy 初始化也正确重置状态。
- commit 时若可证明本次读取的 GPU 行前缀已与 CPU 一致，则直接返回；有 dirty 或无法证明时完整调用原 copy，不拆成很多小 memcpy。
- 不替换 GPU tensor、不改变 block size/stride、原 slot mapping、scheduler、图和 attention 都保留。
- 对 num_reqs 增长、capture 中 num_reqs_padded 增长保守回退；不能把“上次只提交 30 行”当作第 31 行已经同步。记录已同步行范围，或任何范围扩张都原样复制。

这个机制针对“持续 decode 大多数步没有分配新 block，也没有换行”的常见情况。block16 不意味着每一步都改表；但请求同相进入时可能同时在每 16 步发生块分配，dirty 时仍原样提交即可。

### 预期负结果

- 原 copy 被 CPU 准备或前序 GPU 工作完全隐藏，减少 bytes 却没有端到端收益。
- 高 churn/预填充阶段几乎每步 dirty，skip 比例低，标记逻辑反而添开销。
- 只漏标一个 row mutation 就会写错 KV；只验证稳定 batch 无法覆盖该风险。
- 若用逐行小 memcpy替代完整 copy，launch 数可能抵消字节收益，所以第一版不做它。

### 最短可反证验证

先 CPU：以独立镜像模拟 GPU 表，重放 add/append/clear/move/swap、`num_reqs` 收缩/扩张、clear 后重用和 capture padding，逐次 commit 比较会被读取的全部前缀。无修改时允许 skip，任何不一致即拒绝。

再由单一 device owner 串行做一组短服务验证：新鲜随机前缀，至少一个请求生成超过 16 token 以跨块边界；另一个短批次覆盖完成、加入和行压缩。检查请求成功、错误日志、dirty/skip/full-copy 次数，以及固定贪心提示输出与保留补丁相同。只要没有 skip 或出现错位，就停止扩大测试。

有正确性证据后才做很短的同参数 A/B decode 计时，分别记 H2D bytes/调用次数、prepare_inputs 暴露时间和服务耗时。小样本只用于筛除，不冒充官方分数。只有候选值得保留才跑官方 accuracy/性能门槛。

## 候选 2：pure-decode 输入准备快路

只对运行时已确认“每个活动请求恰好调度 1 个 token，纯文本、无投机、无特殊位置编码”的情况，复用恒等 `req_indices`、全零局部 query positions、单调 query offsets 等 buffer，省去通用 repeat/cumsum 和恒定数据重复上传。batch 成员顺序/大小、padding 或语义变化时重新准备或回退；常量长度由实际配置决定。

这不是增加 scheduler steps，也不改变任何请求的可运行时机。它承接 MLPerf 的“摊薄 host 工作”经验，同时避开在固定 vLLM V1 上引入多步 EOS、取消、输出和 KV 预留的一整套状态机风险。

最短反证：CPU 比较通用/快路的所有派生数组，覆盖 batch 大小变化和重排；随后仅记录几个稳定 decode step 的 prepare_inputs 非 profiler 计时。若数组一致但该工作本来完全重叠，或检测/分支开销更大，就终止。此方案预计收益小于旧 prefill 算子优化，不能许诺百分比。

## 候选 3：保留算法的确定性 logits/filter 子图

本地 model forward 已有 graph，LM head 和采样尾仍有图外 launch。可考虑捕获 **hidden states → 原 LM head → 原温度处理 → 已保留的 deterministic top-p filtering**，随机采样尾保持原代码。先不把 RNG、per-request generator、penalties、logprobs 或结构化输出放入新图；不匹配直接回退。

用真实 batch shape 和 dtype/语义作 key，建立有容量上限的缓存，不把 64 当上限。图输入用稳定小 hidden-state buffer，而不是每步复制完整 `[B,130560]` logits；输出和 top-p workspace 有明确生命周期。不得因为捕获而把不同请求数 padding 成同一采样 batch，改变 RNG 消耗顺序。

[PyTorch 官方 CUDA Graph 文档](https://pytorch.org/blog/accelerating-pytorch-with-cuda-graphs/)要求固定内存地址和保留输入输出引用；[vLLM v0.24 graph 设计](https://github.com/vllm-project/vllm/blob/v0.24.0/docs/design/cuda_graphs.md)已经按 batch/attention 支持情况分派图。这里是在既有机制旁补一个确定性后处理阶段，不是换框架或简单重新开启 `torch.compile`。

最短反证：仅在匹配路径对同一 hidden states 比较 eager/graph 的过滤后 logits 与有限值 mask，确认多次 replay 不引用旧输入；做一对固定 shape 的短计时并记录新增峰值内存。若 buffer copy、graph 内存或调用边界使时间不降，立即拒绝。当前 32 GiB 下增加图内存可能降低 KV 容量，导致 16K 可驻留请求减少，这是实质负结果。

## 不优先复试的方向

- 更大 batch/window、KV block64、关 prefix cache、重新开 sampler compile：已有本地负结果，不因其他硬件报告再扫描一遍。
- 改 graph capture 最大 batch 为 64：这是按测试约束收窄通用行为，不作为候选；已有图内存问题应按运行时配置与真实需求处理。
- 多卡负载均衡、prefill/decode 分离、TP 通信融合：本实例只有一张卡，缺少前提。
- 直接复用其他模型的量化、MTP/EAGLE 或换 framework/backend：不满足当前规则与用户范围。
- 跳过部分请求的逻辑、benchmark 专用 cache、放宽数值门槛：没有提案资格。

## 建议执行次序

1. 本地真实源码确认 → zero-dirty 最小补丁 → 另一 owner 交叉检视。
2. CPU 状态机验证 → 一组跨块边界短服务验证 → 短 A/B 筛选；失败即留存负结果。
3. 只有通过并显示价值，再运行官方所需 accuracy 与复现测量。任何 profiler run、短 smoke 都单独目录，不能混入官方 baseline。

每次实验保留唯一 UTC run ID、源码差异、启动参数、GPU/KV 容量、原始日志与失败；CPU 并行工作须在设备计时前停下，避免改变 host 负载。
