# 16K 容量与图生命周期：尚无超过 1 GiB 可回收证据

2026-10-21。本轮仅本地 CPU、已归档源码/日志与一手资料；未 SSH、未运行 GPU、未修改任何候选。SQL+C2 的 `073644` accuracy 由唯一 device owner 运行，本报告不使用其未完成结果。

## 判断

**目前不建议把“释放图生命周期浪费，回收 >1 GiB”升为实现主线。** 已有全局共享 pool、由大到小捕获和临时 profiling 状态清理；能按源码算清的输出、scratch、页表和输入缓存都太小。真实服务还有约 2.17 GiB 的权重/KV 之外 driver 占用，但没有 allocated/reserved/non-torch 分解，不能把它直接视作浪费。

有一个具体平台细节值得测量：GraphWrapper 虽调用 weak-ref，插件 `_C::weak_ref_tensor` 却注册为 identity fallback。它可能影响共享 pool 的内部复用，但仅最终输出本身远不到 1 GiB。要继续，应先测阶段内存账本和 allocator 状态，再决定是否实现真正弱引用/工作区生命周期调整。

## 本实例的内存账本

资源基数是实际单 device 的 **32768 MiB / 16 SM**。厂商 [ix-device-plugin](https://github.com/Deep-Spark/ix-device-plugin#split-gpu-board-to-multiple-gpu-devices)明确 BI-V150 一板可有两个 GPU 芯片；不能把全板 64 GiB 代入此实例。

主要服务证据来自 [SQL-only 日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072153Z-sql-reflection-screen/server.log>)、[SQL+C2 日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T073309Z-sql-decode-screen/server.log>)、各自 `gpu.csv` 和 [配置快照](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054501Z-mixed-gate/source/model-config.json>)。单位均为二进制 MiB/GiB。

| 项目 | MiB | 证据等级 / 限制 |
|---|---:|---|
| 实际可见总量 | 32768 | 每条 GPU CSV 都有；不含第二 die |
| 无服务时占用 | 68 | 多个 run pre/postflight；不是服务自身全部 context 开销 |
| 官方 0.85 对应预算 | 27852.8 | `total_memory * gpu_memory_utilization` 的源码计算；不是实时 device 占用上限 |
| 预算外 0.15 | 4915.2 | 保持官方参数；不能直接转作 KV 或算“可回收” |
| 模型 BF16 参数数据 | 4800.3320 | 按 config 推算 2,516,756,480 参数 ×2；checkpoint 日志 4.69 GiB 相符，但不等于实测 `model_memory_usage`，亦不含非参数 buffer |
| SQL-only KV 数据 | 21403.59375 | 521840 tokens ×43008 bytes/token；block16，无量化 |
| SQL+C2 KV 数据 | 21407.53125 | 521936 tokens，较前者多 96 tokens /3.9375 MiB；不能把它当候选增量收益 |
| 预算扣 KV 后的总 sizing 余项 | 6449.20625 /6445.26875 | SQL-only /SQL+C2；包含权重及 profiling 扣减，不能称 free cache |
| 上行再扣参数数据后的余项 | 1648.87422 /1644.93672 | 仅代数剩余；缺精确 weights/activation/non-torch 数据，不能宣称全是 peak activation 或全可释放 |
| 稳态 driver 总占用 | 28428 | 两次 SQL-only 和一次 SQL+C2 一致；B0 为28436；5秒采样不覆盖瞬时峰值 |
| 稳态可见空闲 | 4340 | `32768-28428`；低于预算外4915.2说明budget不是实时占用硬限 |
| driver 占用扣 KV 与参数数据 | 2224.07422 /2220.13672 | 约2.17GiB，混合了context、buffer、allocator缓存、图/driver状态等，不是可回收量 |

KV 公式是 `42 layers * 2(K,V) * 2 KV heads *128 *2 BF16 bytes =43008 bytes/token=42 KiB/token`。参数公式包含42层Q/K/V/O、三路MLP、两层norm，以及不共享的embedding/LM-head和最终norm；没有据checkpoint文件大小反推精确device storage。

CSV 的阶段信息只有粗包络：SQL+C2在15:33:45/50是6026 MiB；15:33:55为27778；15:34:00为27980；15:34:05及之后为28428。日志15:33:55报KV521936，随后约5秒捕获35图。末段增长约650MiB还混合捕获进度、sampler warmup与allocator缓存；没有准确capture前采样，因此它**不是graph大小的精确值或严格上界**。它也没有给出“图独占 >1GiB”的正证据。

## 已知 buffer 的数量级

当前编译范围为1..2048，capture配置最大512，实际35图；源码按 `max_num_reqs` 限制uniform decode，当前35对应 `[1,2,4,8,16,24,...,256]`。不要把配置51个尺寸全当实际捕获51图，也不要只按评测并发64裁图。

| 对象 | 数据量或上限推算 | 为什么不足以支持 >1GiB |
|---|---:|---|
| 图最终 hidden-state 输出 | 35图总B=4231，`B*2048*2` 合计 **16.52734MiB** | 即使每图强持有独立完整输出，也很小；没有把42层输出全部乘上去，FULL_DECODE_ONLY通常是外层整模型wrapper |
| Triton attention分段scratch | 一builder `64*16*16*(128+2)*4` = **8.125MiB** | 同backend/spec/Qheads的42层按group复用builder，常规无ubatching只有一builder；不能误算为42份独立scratch |
| 全长页表device端 | `256*8192*4` = **8MiB** | CPU镜像不是GPU显存；64活动行H2D约2MiB/步不等于持久GPU占用可省2MiB/步 |
| 持久inputs_embeds | `2048*2048*2` = **8MiB** | 即使当前text-only不用，也只有8MiB；合法embedding输入和图地址生命期需保留 |
| RoPE cos/sin | 标准路径 `131072*128*2` = **32MiB/唯一实例** | 上游按rope参数缓存模块，不能按42层无证据乘成1.3GiB；实际dtype/唯一storage仍需核实 |
| retained histogram top-p缓存 | 每请求 `(2*1+6+256)*4` =1056B；全部B1..256相加 **33.12891MiB** | 此值已是假设每个batch-size缓存均出现的保守数据量；不会成为GiB级对象 |
| LM-head / sampler FP32大矩阵 | B256,V130560时每份 **127.5MiB** | 多份logits/probs/noise/排序索引可能有较高瞬时峰值，但需按storage与生命周期核实，不能把源码所有临时变量大小相加 |

scratch与group证据见实际 [triton_attn.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/remote-source/triton_attn.py:124>) 和 [归档runner metadata分组](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/source/model_runner.py:6834>)。RoPE的模块缓存与BF16 buffer机制由 [v0.24 get_rope](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/model_executor/layers/rotary_embedding/__init__.py)及 [RotaryEmbeddingBase](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/model_executor/layers/rotary_embedding/base.py)支持；这是版本机制推算，尚无本实例storage清单。retained top-p源码是本地patch-check中 `vllm_fl/patches/biv150_top_p_triton.py`，与服务manifest的 `da77c411...` 对照后使用。

## 生命周期源码审计

1. **共享pool已经实现。** 保留 `GraphWrapper.__init__` 使用 `current_platform.get_global_graph_pool()`；runner `capture_model`由大到小捕获以复用pool。不能把“改用共享pool”当新实现。PyTorch 2.10的[图内存管理说明](https://docs.pytorch.org/docs/2.10/notes/cuda.html#graph-memory-management)解释capture地址须持续保留、独立图可顺序共享pool；活图仍需要的storage不能靠`empty_cache`释放。

2. **weak-ref旗标不能当运行时事实。** GraphWrapper默认`weak_ref_output=True`且`entry.output=weak_ref_tensors(output)`；但插件 [fallback registry](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/src/vllm-plugin-FL/vllm_fl/ops/_C_ops_registry.py:14>)注册`weak_ref_tensor=lambda t:t`。服务日志亦有native `vllm._C`缺失警告。[v0.24上游weak_ref_tensor](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/utils/torch_utils.py)调用该op。正常fallback路径因此保留原tensor；若另外后端覆盖注册则需运行时核实。本地没有发现Iluvatar覆盖。应测`id`/storage，不盲目删output或用Python weakref：replay返回仍必须有效、且不能跨图覆盖尚在采样使用的输出。

3. **临时profiling图不是现成的泄漏。** runner `profile_cudagraph_memory`用临时pool，finally清图、恢复pool、清dispatcher keys、清最小KV、gc+empty_cache。实际Iluvatar还因`WorkerFL.determine_available_memory`中的`current_platform.is_cuda()` guard而跳过该调用：PlatformFL只对vendor nvidia返回True。不能声称本机每次启动留下这套临时图，也不能把启用该估计误称增容；它可能扣除更多KV预算。

4. **workspace已经按ubatch复用并锁定。** [v0.24 WorkspaceManager](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/worker/workspace.py)持有每个ubatch一份workspace，满足已有容量则复用，捕获后runner调用`lock_workspace()`。尚无本实例workspace实际大小；不能一看到manager就声称可回收GiB。捕获后缩容/换storage会破坏图内地址或后续合法大shape。

5. **profile大峰值仍可能值得看，尚未证明可省。** `profile_run`跑max_num_tokens并执行sampler；dummy metadata设置top_k=vocab-1/top_p=.9、另一次带generator。此压力路径可能比常规top-p-only有更多中间量，但服务必须支持合法top-k/generator，不能只删除warmup压力或改KV budget掩盖真实峰值。只有实现实际生命周期/内存复用改进，并在完整合法路径验证不OOM，才可把新的较低peak用于sizing。

## 容量门槛与收益边界

以521840 tokens起算，block16且忽略prefix共享：

| 目标 | 额外KV tokens | 额外MiB |
|---|---:|---:|
| 32个纯16384-token prompt | 2448 | 100.40625 |
| 31个16384+1024完整请求 | 17808 | 730.40625 |
| 32个16384+1024完整请求 | 35216 | 1444.40625 |

所以不足1GiB也可能跨过某一相位的驻留门槛，但“省100MiB就全程32并发”不成立。省1GiB对应约24966个原始KV token、按16对齐至少需按page折算，仍低于32条完整长度所缺35216tokens。scheduler增量分配、实际输出、抢占、prefix共享会改变轨迹；最终证据应是同参数16K官方负载的KV使用、preemptions/排队轨迹与walltime。

更关键：当前KV预算在实际graph capture**之前**就确定，Iluvatar没有应用graph估计。因此若某候选只减少capture之后的占用，现有公式下KV容量不会自动增加。要转为容量收益，必须降低真正纳入sizing的合法peak/持久开销，或实现并验证通用的内存预算/生命周期机制；不能改0.85、手填更大KV bytes或按benchmark尺寸少捕图。

## 唯一建议的下一项最短诊断

等accuracy owner释放设备后，由同一owner另建诊断run，保持源/官方参数/capture覆盖，**只加阶段观测，不先加优化**：

- 在runner创建、load后、profile前/后、KV初始化后、每个capture前/后、sampler warmup后记录`mem_get_info`、allocated/reserved/current/peak、inactive_split与allocator backend。缺API明确记unsupported，不套NVIDIA graph-memory专用API到CoreX。
- 记录worker已有`model_memory_usage`、`peak_activation_memory`、`non_torch_memory`、`available_kv_cache_memory_bytes`、`cudagraph_memory_estimate`及capture返回值。它们不少仅DEBUG可见，避免为获取数字扩大官方基准日志或混入性能结果。
- 一次列出graph wrappers/entries实际数量、output shape/dtype/unique storage bytes、attention builders与scratch、workspace manager和hist cache的unique storage bytes。只读、无GPU `.item()`；统计data_ptr/storage并处理共享别名，不能逐tensor简单相加。
- 若CoreX支持allocator snapshot，在capture后、warmup后各保存一次以区分可用cached block与active graph-pool block；不支持则停止于已有计数。无需跑长benchmark来证明内存清单。

若确认图/fragmentation合计都不足几百MiB且合法profile峰值无冗余，此方向降级；不构建弱引用替代或allocator改造。若定位了>1GiB具体无后续用途的storage/高峰重叠，再提出一个实现改动，先bitwise+多shape replay/lifetime门，后用实际KV容量与16K端到端验证。**本轮没有这样的正证据，也没有新增候选。**

## 源码身份

归档host-profile runner SHA256 `dfd532de4a0b0bdb286aed0f42b4d6f2c3b2c2dcf65634f895577144473b68b9`（含profiling footer，不能充当当前服务runner hash）；实际下载triton backend `1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605`。本地保留插件参考checkout HEAD为`13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`，相关文件SHA：worker `f6188c637dfa93a249e815c5bd411a368fbcde3be16d6abd0a17cc05c652e514`，graph `91ba5a848e55630639ee241d8f8e8de1348d616a0b9dd1f0dc9e89ec7ebfec01`，platform `9b223ffbde59c47ba3c13602db709eea6b29ec368a084ae2b579d589649695d7`，fallback registry `f1f23f6402c8cffa7e76edf4a647a52f6c1a0406ac816735dc5272cc0f1c95a3`。这些文件不在最近service manifest逐项hash范围内，因此是固定base源码证据，实施前仍要核对实际服务文件；不把GitHub main当安装版本。
