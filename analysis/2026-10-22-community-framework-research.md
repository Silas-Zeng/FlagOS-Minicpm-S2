# 2026-10-22 开源社区框架机制筛选：下一项优先检查 blocking Event

本轮只做一手资料和冻结源码交叉阅读，未写 runtime、未 SSH、未上卡、未合并新框架。结论限本实例天数 BI-V150：16 SM、32 GiB、6 CPU quota、20 GiB 主机内存，MiniCPM5-2B BF16、42 层、GQA 16/2、head width 128。另一平台沐曦－曦云 C500 需要队友另验。

**下一项最值得做的是先查 Corex 的 blocking Event 实际契约，再只改变输入准备等待事件的主机等待方式。** 原事件所保护的异步传输、CPU buffer 复用和完成依赖全部保留。它有已合并的 vLLM 实现和本站逐步执行的同源挂点，改动面比 KV allocator 重写小；收益仍未知。本轮另外保留三条有明确源码依据的机制，不同时实施、不叠加变量。

| 顺序 | 可迁移机制 | 一手状态（截至本次查阅） | 本站最主要边界 |
| --- | --- | --- | --- |
| 1 | device Event 使用 blocking 主机等待 | vLLM PR #47081，2026-07-07 合并 | Corex 是否接收并真正执行 blocking 标志尚未证明；TP4 的收益不能外推本 TP1 |
| 2 | Attention 的真实 `num_seqs` 不参与整数属性特化 | vLLM PR #62357，2026-10-18 提交，仍 Open | 仅潜在减少运行时 JIT；官方 warmup/skip1 后可能没有收益 |
| 3 | KV 元数据批处理下沉到原生代码，保留所有权与异常契约 | SGLang PR #39627，2026-09-29 合并 | SGLang Rust TreeCore 不是 vLLM BlockPool；现成扩展也不支持本站 Torch/Corex 组合 |
| 4 | 受严格 guard 的已编译 Attention launch handle | Triton RFC #10140，2026-04-27 提交，仍 Open | 本站此前已有未实施的条件计划；只补社区依据，不算重新发现或已测收益 |

## 1. 优先项：保持事件依赖，只让主机等待可阻塞

[vLLM PR #47081](https://github.com/vllm-project/vllm/pull/47081) 把 V1 输入准备及异步输出事件改为 device CUDA blocking Event；[实际 diff](https://github.com/vllm-project/vllm/pull/47081/files) 使用 `torch.cuda.Event(blocking=True)`。PR 作者指出 generic `torch.Event(blocking=True)` 在其 CUDA 实验中没有兑现该标志，不能仅给 generic 构造器加参数就认为有效。作者的突出场景有 TP 集合通信竞争；本站 TP1 没有同样证据。这里只迁移“同一完成条件下改变 CPU 等待方式”的机制。

本站受测 runner 是以下原件，SHA **e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1**：

[实际 model_runner.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T214400Z-kv-full-restore-context16k-long-control/plugin-source/vllm_fl/worker/model_runner.py:750>)。

| 实际行 | 当前行为 | 最小接入含义 |
| --- | --- | --- |
| 756–758 | async scheduling 时创建 copy stream，`prepare_inputs_event = torch.Event()` | 首个候选只改变 758 的事件工厂/阻塞标志，其他 event 暂不混入 |
| 3823–3836 | `synchronize_input_prep` 在 3832 等上一轮事件；`finally` 在 3836 记录当前轮事件 | 原 contextmanager、异常传播、finally、record 的流与时点必须原样保留，不能删除等待 |
| 4162–4167 | 原 preprocess 的 with 在 `_update_states` 前进入上述 contextmanager | 这不是无关的 startup 事件，而是实际逐步 buffer 复用边界 |
| 314、340、348 | 异步输出事件构造、copy stream record、CPU 读取前 synchronize | 可作后继独立挂点；构造器已经 record 后不能再换一枚未记录的新事件 |

最小源码变换应只作用于一个全新 SQL+C3 隔离源树，锁定 e155 的原始字节与唯一构造行；不覆盖受测树，不与 KV 协议、a662 SAVE、`num_seqs` 变更叠加。device 工厂应由实际平台/绑定证明，目标是设备专用 `Event(blocking=True)`，不是全局 monkeypatch `torch.Event`。新源身份必须如实入 manifest；已有 exact-source guard 不得绕过。先局限 758，保留 314 和 435 的原异步输出路径有利于归因。

### Corex 尚缺的具体证据

[PyTorch 2.10 的 CUDA Event 文档](https://docs.pytorch.org/docs/2.10/generated/torch.cuda.Event.html) 提供 `blocking` 参数、延迟初始化及 record/synchronize 接口；这是上游 CUDA 契约，不证明本站 Corex 后端同样实现。已有实际 ABI 原件只截取了 Stream 指针接口和 memcpy 声明，没有 Event 的标志/等待实现：

[030314 ABI 原件](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/source-audits/20261022T030314Z-memcpy2d-abi/result.json>)，SHA **f9c348a60fa34469377fda671d2d57a42c108fca2554fd59963b6b7033ffb576**。

下一步只需纯读取证以下小段，不需要导入 Torch、载库或调用设备 API：

- 实际 `/usr/local/lib/python3.12/site-packages/torch/cuda/streams.py` 的 `Event.__new__`/`synchronize`，以及可取得的 generic Event/设备 Event 绑定，确认参数如何到达底层。
- 实际 Corex `/usr/local/corex-4.5.0/include/IX/ixrt/driver_types.h` 的 `ixEventBlockingSync` 等标志；`IX/ixrt/ix_runtime_api.h` 的 `ixEventCreateWithFlags`、record/query/synchronize 声明；`IX/mapping_cudart.h` 的对应映射。
- 实际安装头若存在，检查 `ATen/cuda/CUDAEvent.h`、`c10/cuda/impl/CUDAGuardImpl.h` 中 blocking 到事件 flag 的处理。声明/导出存在仍不能证明 CPU 真正睡眠，最终需要短设备判定。

不把 generic API 接受关键字、已有非 0 stream 正确性或 NVIDIA 文档当成 Corex blocking 能力证明。本轮已将精确缺口和既有路径交给 systems，避免再次全量采源。

### 最短证伪门与结束条件（尚未实现/执行）

1. 使用同一份实际输入准备 contextmanager 和真实 pinned staging buffer，保持 producer stream、record、下一步 synchronize、finally 顺序。安排事件尚未完成时进入等待，跨两步复用源 buffer，逐位核验每步传输结果、事件完成状态和原异常语义；不靠额外整卡同步掩盖缺失依赖，不改采样/N/RNG/请求顺序。
2. 相同工作量、同流、预热后短固定镜像窗口比较默认事件和 device blocking 事件。窗口外记录 v1 `cpu.stat`；窗口内单列等待线程 CPU 时间/进程 CPU 时间、wall 和设备完成时长。CPU 等待明显下降且 wall 不回退才是有价值信号；进程 CPU 时间不能直接等同主线程自旋。
3. 标志不支持/被忽略、完成或复用语义失败、wake-up 使 wall 变慢，都保存负结果后停止。若事件通常已完成、没有可测 CPU 等待，也应判本站机会不足，不扩大事件种类找最好样本。短门明确通过后只补必要服务命中与短 screen，不自动跑完整官方或重复长 pair。

6 CPU quota 让节省忙等有现实价值，但现有长服务 GPU 利用率约 95–96%，不能据此声称 CPU 是主瓶颈。035754 copy 门的进程 CPU 接近 wall 也混有提交和驱动等待，不证明服务的 3832 目前忙等。更低 CPU 占用本身不等于 TPS 提升；本候选只优先验证低成本、可否定的机会。

## 2. `num_seqs` 的 `do_not_specialize`：只消除不必要 JIT

[vLLM PR #62357](https://github.com/vllm-project/vllm/pull/62357) 明确只给 `kernel_unified_attention`、`reduce_segments` 的 `num_seqs` 加 `do_not_specialize`，针对整数等于 1/可被 16 整除等属性特化；不是把请求数改成固定值。其作者环境是新 vLLM/Triton 与 NVIDIA 设备，不能照搬该性能或缓存结果。

本站 [实际 unified Attention](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/remote-source/triton_unified_attention.py:178>) SHA **54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f**：178、662 是普通 `@triton.jit`，234、670 的 `num_seqs` 不是 constexpr，854 从真实 metadata 得到请求数。C3 的 prefix/suffix 数量会变化。实际 [Corex JIT](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/source-audits/20261021T183920Z-compiler-cache/installed-triton/spec/iluvatar/triton/runtime/jit.py:442>) SHA **66a168ae959e719186771e66815e807f1e449e66c5283ef596ec3eb0e35cb775**，442–463 的 binder 确实有参数级 `do_not_specialize` 分支，737 之后仍计算 specialization/cache key。

若后继实施，只改两个 decorator，保持真实 N、metadata、grid、所有数学和实参顺序。先证明官方 warmup 后真实路径还有该属性类别的 cache miss；若没有则收益为零。最短门针对 N=1/2/16 的必要 2D/3D/reducer 字节正确性与冷/热编译数，区分第一次 JIT、官方 skip1 后的计时，不扫 shape。它不能从“少一次 JIT”推导稳态 GPU kernel 加速。暂不与第一项合并。

## 3. 原生批量 KV housekeeping：借鉴边界，不移植整套 Rust cache

[SGLang PR #39627](https://github.com/sgl-project/sglang/pull/39627) 及其 [代码路径](https://github.com/sgl-project/sglang/pull/39627/files) 包括 `rust/sglang-radix-tree/src/{python_bindings,unified_tree_core,unified_lru_list}.rs`、`python/sglang/srt/mem_cache/rust_tree_core/adapter.py`。有价值的是原生批量状态操作仍保 ownership、异常与可见性边界。该 PR 的扩展范围限制为特定 Torch 2.11–2.13/CPU 或 CUDA 等配置；本站 Torch 2.10/Corex 不在此支持证据内，不安装现成扩展。

本站 [实际 BlockPool](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/source-audits/20261021T170854Z-scheduler-kv-c3/source/vllm/v1/core/block_pool.py:542>) SHA **3fc5dfe0ab7ccc6206f6eb7886b2aad15384f92708e6b9f7e5ec7838b7379abe**：542–595 分配/逐页驱逐，597–612 touch，614–635 有序释放/refcount/hash 分流。现成 `popleft_n/prepend_n/append_n` 已批量操作队列，699 的 free 数是 O(1)；226 的 cache_full_blocks 也会跳过已缓存部分。不能把所有 Python 页管理描述成重复全表扫描。

可迁移的窄机制是把确实热的连续页批次操作合为一次原生调用，同时保持 Python block 对象身份、`req_to_blocks` 列表别名、refcount、null/hash、free 顺序与指标。先读真实操作计数/CPU 时间才能选择切口；没有占比证据就停止，不先写完整 Rust allocator。当前约 1044 页是抢占恢复的一次大批次，decode 并非每步都处理 1044 页；FullAttention 每 16 token 的增页和已有 capacity fast reject 也限制其持续收益上界。必要 CPU 门是原/候选对同一实际操作序列的状态、失败和顺序完全相同，之后才一个原参数短服务 screen。此项潜力可能大、实现风险也高，排在低改动项之后。

## 4. 已编译 launch handle：只削 eager 主机路径

[Triton RFC #10140](https://github.com/triton-lang/triton/issues/10140) 提出 frozen launch handle/guarded hot path，2026-04-27 提交，仍是 RFC；它不是已合并的 Corex 能力或性能结果。本站原 [后继框架优先级报告](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-22-next-framework-priority.md:46>) 已保留同方向条件计划，本轮补一手佐证，不重复实现。

实际 66a JIT 的 754 binder、756 cache key、761 `get_corex_sme`、762 参数打包说明已编译后仍有 Python/配置处理。可以研究在完全相同 kernel/config/shape/stride/options/hooks/globals 身份下复用原 compiled handle，每次仍传真实指针/标量/当前流。本站 MM 入口曾用 `compiled[grid](*args)`，只证明该安装有接口，不证明 Attention 或跨层复用已经安全。

此处只瞄准 eager prefill/mixed 的真实 launch；完整 CUDA graph 回放已绕过的 Python 不再计入预算。不得套 NVIDIA `cuLaunchKernelEx` 或绕开 Corex SME、launch hooks、生命周期/used-global guard。最短门只一组真实层 metadata：原 JIT 热调用与同配置 handle 字节/事件/RNG相同并测主机时间；若热 CPU 占比很小或 guard/打包成本抵消，即停止。未证 host 预算前不宣称可得大收益。

## 来源许可、既有工作与交接边界

上面 vLLM、SGLang 的上游许可分别是 [Apache-2.0](https://raw.githubusercontent.com/vllm-project/vllm/main/LICENSE)、[Apache-2.0](https://raw.githubusercontent.com/sgl-project/sglang/main/LICENSE)；Triton 上游为 [MIT](https://raw.githubusercontent.com/triton-lang/triton/main/LICENSE)。后继若借代码需保原版权/许可/修改说明，另核实际 Corex 派生文件的许可；本轮没有复制新框架代码、安装新包或改运行文件。PR/RFC 状态按 2026-10-22 查阅记录，不把 Open 当已合并。

不重启已反证的 growth/full-reserve、terminal、短 R、WAITING 单步 fit；不把已测 dirty block table、C batch/2D SAVE 门再列为新候选。SWA/Mamba/MoE/多卡/多模态/稀疏 top-K 的优化与本站 dense GQA text scope 不同，不据标题迁移。采样、参数、FCFS 公平性或全局输出等价不能从这些机制自动推出。

另纠正 KV 生命周期范围：原 FULL `1aff` 的 `single_victim` 表示一个并发 host slot；`_drop` 会清 `victim=None`，`_wrap_preempt` 没有每 Engine 一生一次的上限。当前有限 32 请求轮中实际只发生一次 SAVE，不表示长负载永远一次。本轮 blocking Event 机会也不依赖这一次 SAVE。root 已回执 042225 真 SAVE42/FULL42/consumer16、32/0、DB 相同；该实测归独立原件验收，本轮不重跑或用它证明 Event 收益。

当前建议的唯一下一动作是 **Corex Event 的小范围纯读取证**；本报告中的四项均尚未新增 runtime/设备门，无新性能数字。能力证据通过后才由 root 决定第一项最短设备证伪，其他三项保留队列。
