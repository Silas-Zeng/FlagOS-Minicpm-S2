# 第二轮：混合 Attention 分流的反证与图内 GEMM 审计

日期：2026-10-21，Asia/Shanghai。本研究 agent 只做 CPU 源码审计与本地结果阅读，没有 GPU、远端、推送操作。下述真卡数据由唯一 device owner 产生。

## 当前优先级：主攻图内 GEMM，mixed 分流降为尾块候选

mixed 分流原提案是保持 GEMM、RoPE 和 KV 写为整批，只在 Attention 内把单 token 前缀与多 token 后缀分开执行。源码证明存在形状浪费，**真卡最短筛选没有证明常见满 chunk 有较大收益**，因此先不支付完整框架补丁和 accuracy 扫描的成本。仅保留长 KV、小 prefill 尾块的条件候选。

下一步转向被 graph 隐藏的真实 GEMM 时间和实际选中实现。CPU 审计未发现新的、可证明有大收益的纯框架 GEMM 形状改动；下面明确记录已排除的重复融合/拆 batch 思路，不为了保留“框架路线”而硬凑候选。

实施不改变官方启动参数、benchmark、模型、精度、采样参数和 scheduler 的准入决策，不按并发 64 或指定输入长度硬编码，不合并新框架、不启用现成量化/投机。提交内容应是真实的混合 Attention 分解、metadata 和输出 alias 实现，不能只写一个切换现成 backend 的环境变量。

## 已下载的最短真卡反证

Run ID：`20261021T035611Z-mixed-dispatch`。设备负责人保留的远端证据目录是 `/workspace/experiments/minicpm-s2/framework/20261021T035611Z-mixed-dispatch/`，本地副本是 `experiments/framework/20261021T035611Z-mixed-dispatch/`。

一手文件：`manifest.json`、`results.json`、`gpu.csv`、`exit-code`，以及 `source/benchmark.py`、`source/original.py`、`source/helpers.py`、`source/transform.py`、`source/direct_decode.py`。manifest 记录源码 SHA256、准确命令和设备信息；开始为 2026-10-21 03:56:11 UTC，结束 03:56:24 UTC，exit code 0，端口 9031 空闲、起始空闲显存 32700 MiB，BI-V150 32 GiB、16 SM。

实际 mixed 测试调用保留原 Attention 函数两次，不采用 direct-decode 变体。每个形状预热两次、五次计时取中位数；是非 graph 单层实验。metadata normalization 和 slice 准备移到计时外，故结果是对真实框架集成偏有利的机会筛选，不能声称等于服务收益。

| KV 长度 | decode 请求 D | prefill token P | whole 中位数 ms | split 中位数 ms | 延迟降低 |
|---|---:|---:|---:|---:|---:|
| 4096 | 63 | 1985 | 3.974296 | 3.955988 | 0.461% |
| 4096 | 63 | 127 | 2.039400 | 2.051873 | **-0.612%** |
| 16384 | 29 | 2019 | 13.718111 | 13.622354 | 0.698% |
| 16384 | 29 | 127 | 4.732004 | 4.408543 | 6.836% |

表中的百分比统一为 `(whole-split)/whole`，不是吞吐提升。全体 prefill 输出均 finite、与 whole **bitwise equal**。decode 输出均 finite，但不 bitwise equal：四行最大绝对差依次为 `0.00244140625`、`0.001953125`、`0.00048828125`、`0.00048828125`。这没有通过官方 accuracy，也没有 FP32 reference 证明；不能把有限值检查说成精度已过关。

结论是：masked 数学比例不等于真实 latency。典型满 2048-token chunk 仍被大 prefill 工作支配，decode 独立分段和额外 launch 的净效果小于 1%；4K 短尾块甚至倒退。16K/P127 显示一个需要未来真实命中频率支持的窄机会，尚不足以解释整模型大提升。下面保留源码设计供以后查阅，当前不集成。

## 源码身份

- 固定插件 base：`13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`。
- 实际安装 runner 快照：`tmp/remote-source/model_runner.py`。
- 固定 base runner：`tmp/src/vllm-plugin-FL/vllm_fl/worker/model_runner.py`，`git diff` 显示该文件无改动。两份 runner 用 UTF-8 读取、归一化换行后，7673 行完全一致。
- runner 本身从较早 vLLM runner 适配而来，当前运行在 vLLM 0.24.0；以下 runner 行号按上述插件文件，不拿上游 runner 行号替代。
- Attention backend 一手参考是 [vLLM v0.24.0 Triton backend](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/backends/triton_attn.py)。正式修改前应再与设备的实际 backend 文件核对。
- 本地 `patches/upstream-vllm-0.24-triton_unified_attention.py` 含诊断 override 与已保留 prefill 政策。审计中不把它当作未修改 upstream 文件；重点核对了实际 launch 分支。

## 调用链与问题

1. `ModelRunnerFL._update_states`，1505–1509：`condense()` → `_may_reorder_batch()` → `refresh_metadata()`。
2. `_prepare_inputs`，约 1960–2275：按当前 `InputBatch.req_ids` 展平 token，生成 `query_start_loc`、`seq_lens`、slot mapping 和 logits indices。
3. `_build_attention_metadata`，2280 起：从 CPU 现有长度构造 CommonAttentionMetadata；同类层共享 metadata/builder。
4. `execute_model`，4209 起：构建输入、选择整批 graph mode、准备 attention metadata，然后调用模型。QKV/输出投影和 MLP 仍按整批执行。
5. Triton backend `forward`，上游约 580–624：一次 `unified_attention` 传入整批 `max_query_len`、Q、sequence lengths、block table、output。
6. 本地 `unified_attention`，约 885–900：只要 `max_seqlen_q > 1` 就匹配已保留的 MiniCPM prefill 策略，`BLOCK_M=128`、`BLOCK_Q=16`、KV tile 64。
7. 同文件约 1000–1015：`max_seqlen_q > 1` 排除 3D segmented softmax，整批采用 2D。

因此 `Q=[1,...,1,P]` 中只要 `P>1`，所有单 token 请求的 Attention 也进入上述 prefill 形状。GQA=8 时，单 token 只有 8 个有效 query/head 行；BM128 将大量矩阵行掩掉。分离 decode 后恢复 BM16 和原 16-segment 路径，既减少无效行又恢复 context 维并行。

不能把 8/128 直接换算成 16 倍端到端加速：原 decode BM16 也有 8/16 的有效行，prefill 的大块仍是有用计算，split 多了一次 Attention launch 和 decode reduction。内存、指令吞吐和 occupancy 也不随有效行比例线性变化。

## 可最小实现的边界

### 第一版：先不重排请求

只在 CPU `query_start_loc_cpu` 证明存在正长度的连续单 token 前缀、后面有多 token 请求时启用。设前缀请求数 `D`，其 token 数 `T=cu[D]`；这些请求全为 1 token 时 `T=D`。不满足就原路径。

这个首版不改请求顺序、sampling metadata、RNG 调用次数或各行的 RNG 分配，适合先证明分流收益。它不承诺覆盖所有 mixed batch。需要更多覆盖时，再使用现成安全重排机制。

### 后续覆盖：builder threshold=1

插件已有 `_may_reorder_batch`（1125–1148），由 `calculate_reorder_batch_threshold`（7025–7043）取各 builder 最小阈值。Triton builder 的默认继承值是 None；设实例的 `reorder_batch_threshold=1` 可以在输入构建前复用已有机制，无需修改 scheduler。

[v0.24 reorder 实现](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/backends/utils.py#L586)按 decode → short extend → long extend → fresh prefill 分区，并调用 `InputBatch.swap_states`。注意 fresh prefill 内可能有 query_len=1 的请求出现在多 token 请求之后，**不能假定阈值 1 会把所有长度 1 的请求都放到最前**。只切实际连续前缀，其余仍交给 prefill 后缀即可。

[InputBatch.swap_states](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/worker/gpu_input_batch.py#L518)同步维护 request IDs、token/length 状态、block table、采样参数、logits processor 更新和 per-request generator 映射。不要手工只重排 Q 或 block table。

### 切片规则

| 项 | decode 子批 | prefill 子批 |
|---|---|---|
| query/output | `[:T]` | `[T:N]` |
| query offsets | `cu[:D+1]`，原点必须是 0 | `cu[D:] - T`，原点归一化为 0 |
| seq_lens | `[:D]` | `[D:R]` |
| block table | `[:D]`，保留原 stride | `[D:R]`，保留原 stride |
| max query length | 1 | CPU 后缀真实最大值 |
| max sequence length | 可由已有 CPU 长度取前缀最大值 | 同理取后缀最大值；使用安全整批上界也不能低估 |
| KV cache | 共用原 K/V cache | 共用原 K/V cache |
| output | 写原 output 的前缀视图 | 写原 output 的后缀视图 |

最危险的错误是切 Q 之后保留全局 prefill offset `T`：kernel 的 sequence 查找、query load 和 output write 会错位。归一化只在 metadata builder 中做一次；不要在 42 层的 `forward` 中各做一次 GPU subtraction，更不能 `.cpu()`/`.item()` 从 device 回读判定边界。

后缀多请求时减的是整段 offsets 向量。不要把每条 prefill 的 offsets 都重置为 0，也不要改 seq_lens：其值仍是 context + 本轮 query。由此 causal mask 中 `context_len=seq_len-query_len` 保持不变。

### KV 写和 alias

当前 Triton backend 声明 `forward_includes_kv_cache_update=False`，`forward` 读取 cache；`do_kv_cache_update` 是独立入口。最小改动可在 backend `forward` 内对已构建的两个 metadata 调用原 forward 两次，传入原 output 的不重叠视图；不能把整个 Attention layer、RoPE、KV update 或 QKV GEMM 再调用两遍。

两段 forward 在相同 device stream 上顺序执行。decode segmented scratch 可以复用 builder 的原 buffer，因为前缀 D 不超过原支持阈值时容量足够，prefill 2D 不读写这份 scratch。不应为每层新建分段 buffer。D 超过原 3D 阈值时让原函数自然选 2D，不强制塞进大小不足的 scratch。

Q/output 第一维切片保留 stride，kernel 已显式读取 stride；无需 `.contiguous()`。block table 只切行，也保留原列宽与 stride。缓存页号无需重编号。返回值仍为整批原 output，不能 concat 两个新 tensor，也不能把子批 output 当作整批输出返回。

## graph、RNG 与精度风险

- 当前固定启动为 FULL_DECODE_ONLY。mixed `max_query_len>1` 本来不使用整批 decode graph；只给真实 mixed metadata 设置 split 信息，纯 decode/prefill、capture/dummy 和 unsupported 路径保持原行为，不用增加/删减 graph sizes。
- 原 kernel 已支持 decoder 因果/窗口/量化等多种能力；首版只给已验证的 dense BF16 causal、单卡、无 cascade、无额外 MM-prefix/特殊 mask 的路径启用。其他特性原样 fallback，不能遗漏对 alibi、sinks、descale、window、softcap 等参数的转发。
- **不重排首版**不更改 sampling 行顺序或 RNG 消耗。但 decode 输出由原 mixed 2D 变为原 decode 3D，softmax 归约次序仍会改变，不能因此宣称 token 完全一致。
- **启用重排后**，per-request generators 会随请求移动；未设 request seed 的全局 RNG 噪声会按新行号分配。分布可以正确，原 seed 下每请求逐 token 一致不能保证。
- 本仓库曾有随机 BF16 attention 小误差却使 math_500 降到 83.8% 的真实负结果。split 必须先有单层严格误差检查，再短 greedy/seeded 服务检查；值得保留才跑官方 accuracy。绝不能以“只是框架切片”豁免数值验证。
- 普通重排不会改变 scheduler 已选 token 数；但会影响原始请求的物理行位置。异步 `prev_req_id_to_index`、采样参数和 block table 都必须沿现成 batch-update 协议刷新，不能缓存跨 step 的 D 或视图。

## 最短可证伪实验

由唯一 GPU owner 串行运行，先单层，不先跑整模型/accuracy。

1. 第一对真实 mixed 形状：`Q=[1]*31+[2017]`，总 token 2048，16Q/2KV/head128、BF16、block16。decode context 可用 4095 或 16383，prefill context 选使最终 seq_len 不越界的值；真实上下文若已采集应优先使用。
2. 同一份 Q、非连续随机页号 block table、随机 K/V cache，分别运行原 whole mixed call 与 split call。两者都使用已保留 prefill 策略，split decode 使用未调参的原 decode 策略。
3. 一个很小的 FP32 dense causal reference 验证 decode 和 prefill 各选几行；记录 max/mean abs 与相对误差、非有限值。prefill 段预期通常可与原 mixed 输出逐元素相同，decode 段与原纯 decode 调用应相同，二者均不得污染对方 output sentinel。若差异与纯 decode 本身无关，先查 offset/stride。
4. 只做足够稳定的一组 warmup + 短重复计时，包含两个 kernel 调用/归约但不含首次编译。记录 `T_whole` 与 `T_decode+T_prefill`，以及额外 launch。若 split 不快或没有混合形状实际出现证据，就先不整合。
5. 一个极小边界矩阵：D=0、全 decode 均原路；`Q=[1,1,7,9]` 验证多个 prefill offsets；不连续 `Q=[7,1,9]` 必须 fallback（第一版）；batch 行移位后再构建 metadata。CPU 可以先完成这些索引/alias 断言。

不必立刻扫描 D/P/所有 KV 长度。首对通过且有明显信号，再补 D=1/P较短的负例，检验 launch 开销是否使小 mixed batch 回退更合理；阈值必须来自通用真实 shape 成本，不是 benchmark 名称。

收益可以用 `speedup = 1 / (1 - f_mixed_attention * (1 - 1/r))` 做上界评估，其中 r 是整层 mixed Attention 的实测加速，f 是这类 mixed Attention 在未加 profiler 的总服务时间占比。42 层重复这份浪费，所以单层的节省可以累积；但 mixed 占比未知，不能从纯 16K prefill 的 93% 历史占比推定。

## 其他候选的反证和上限

### partial-prefill logits/sample 跳过

固定 base 确实存在：`_prepare_inputs` 2225–2233 为每个请求取一个末 token logits；`execute_model` 4435–4436 做 LM head；`sample_tokens` 4537 附近调用 sampler；`_bookkeeping_sync` 3703 起丢弃未完成 prefill 的采样，并回退 per-request generator offset。

但它**不是给整个 2048-token chunk 都算 130560 词表**。常见单条 chunk 只多一个无效 logits row；16K/2048 时每请求约 7 次无效 tail，4K 时约 1 次。保留 top-p 已很快，按当前证据预期小于混合 Attention 分流。跳过全局 RNG 消耗还会改变后续噪声；保留 RNG 生成但跳过 LM-head/filter 可以更接近原语义，却进一步压低节省上限。它不适合作为本轮主攻。

### graph padding

57→64 最多消除 7/64=10.94% 的按 token 线性工作，30→32 是 6.25%；这些都不是整模型增益上限，因为权重读取和底层 GEMM tile 可能完全相同，padding 的 attention KV 也可能被 mask。精确 shape 图增加内存和捕获复杂度，低优先于 mixed 分流。

### 真实 KV 容量门槛

常规 BF16 KV 每 token：`42 layers * 2(K,V) * 2 KV heads * 128 * 2 bytes = 43008 bytes`。

以已有 521936-token capacity 为例：

| 目标 | 超出现容量的 token | 额外常规 KV |
|---|---:|---:|
| 32 个纯 16384-token prompt | 2352 | 96.47 MiB |
| 32 个 prompt 且各至少一个输出槽 | 2384 | 97.78 MiB |
| 30 个 16384+1024-token 完整请求 | 304 | 12.47 MiB |
| 31 个 16384+1024-token 完整请求 | 17712 | 726.47 MiB |
| 32 个 16384+1024-token 完整请求 | 35120 | 1440.47 MiB |

因此“还差约 100 MiB 就到 32 个初始 prompt”成立，但不等于 32 个请求全程驻留；scheduler 是增量分配，还要考虑抢占、输出增长和 prefix 共享。上述只算 KV 数据，没有把对齐/预留当作 0。

`WorkerFL.determine_available_memory` 约 557–574 仅当 `current_platform.is_cuda()` 才估计 graph memory；本插件 Iluvatar 的 `is_cuda()` 为 False。因此只减少 capture 数量不会自动增加返回的 KV 预算。想声称容量收益，必须看到实际 non-KV peak 下降、重新 sizing 后 token capacity 增加，不能直接增加 KV bytes 或变更 0.85 利用率参数。

本轮无需为这条尚未建立完整账本的路线先做内存大改。

## CPU 续审：没有新的大收益纯框架 GEMM 形状点

审计覆盖固定插件 runner、dispatch/compilation 注册，以及与当前 Llama 架构对应的 [vLLM v0.24 Llama 模型](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/model_executor/models/llama.py)、[Linear 方法](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/model_executor/layers/linear.py)、[unquantized GEMM 分派](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/model_executor/layers/utils.py)。公共 v0.24 模型/Linear 文件仍需设备实际文件比对，不能只凭版本号宣布 runtime kernel 已确定。

### 已经做过的融合，不能再算新机会

LlamaAttention 已用 `QKVParallelLinear` 一次计算 Q/K/V；LlamaMLP 已用 `MergedColumnParallelLinear` 合并 gate/up。其 forward 分别是 `qkv_proj → split → RoPE → Attention → o_proj` 和 `gate_up_proj → SiluAndMul → down_proj`。checkpoint loader 也已将 q/k/v、gate/up 权重堆叠。

根据已知 MiniCPM 配置，TP=1 时每层主要 GEMM 形状为：

| 运算 | M | K | N |
|---|---:|---:|---:|
| QKV | 该 step 的 token 数/graph padded token 数 | 2048 | 2560 |
| O projection | 同上 | 2048 | 2048 |
| gate+up | 同上 | 2048 | 12288 |
| down | 同上 | 6144 | 2048 |

不能再把三个 QKV GEMM 合并、两个 gate/up GEMM 合并当作新实现。TP=1 不存在通过去掉 TP AllReduce 来获得收益的前提。QKV 的 split 是 view，不等于每层重复复制整块权重或激活。

### 没有发现可无代价扩大的 batch

runner 已将同一步各请求的 token 展平在同一个 M 维。prefill 与 decode 也已经共享整批投影；按请求类型拆 GEMM 会减少 M、增加 launch，并可能重复读同一权重。层与层之间、当前 token 与下个 token 之间存在 Attention/MLP/采样依赖，不能直接把 42 层或多个 decode step 当成独立 batch 堆到一个 GEMM。

graph padding 可造成 M 的冗余，但前文已给出有限上限；底层 tile 可能使精确 M 与 padding M 耗时相同。扩大 scheduler token batch 已有本地短筛负结果，缺少新的实际 kernel 证据时不重复扫描，更不能把改变官方启动参数当作方案。

### 未确认每步有真实权重搬运

本地 FlagGems Iluvatar `linear` 参考实现中有 `weight.contiguous()`，但当加载后的 Parameter 已连续时该操作不会复制权重。源码没有证明每步存在重新 pack/transpose/host-to-device 权重传输。不能据此编造“做一次预打包即可消除每层搬运”的大收益。

如果真实 kernel profile 后发现权重 stride、transpose/copy 或重复预处理，则在 `process_weights_after_loading` 保存可复用 layout 才有具体意义；在此之前仅是有条件检查项。本轮不做这种补丁。

### 支持下一步 GEMM 的具体接口，而非另提大框架补丁

未量化的默认调用链是 `UnquantizedLinearMethod.apply` → `dispatch_unquantized_gemm` → `F.linear`；编译后可能变成 Inductor 选择的 `mm_kernel`，FlagGems interception 也可能改变实际实现。固定插件只注册 OOT quant linear，不能据此断言 BF16 dense GEMM 已走同一算子库。

因此下一步先确认 **服务图中真正使用的 kernel 与 M/N/K/stride**。现有 `scripts/remote/bench_decode_gemm.py` 直接调用 `F.linear`；若没有复现服务的 compile/dispatch 上下文，它只能测那条 Python 调用路径，不能自动代表图内 GEMM。应将真实选中实现与同形状 isolated timing 对上，再决定针对算子实现、稳定 weight layout 或融合做改动。

有实际 kernel 后，在 `UnquantizedLinearMethod.apply`/模型层接口提交 shape-aware 自实现 kernel 是清楚的集成点；但只改分派到已有 vendor GEMM 不满足当前“实际实现变化”的要求。新 kernel 的 dtype、归约和随机输出敏感性仍需保留 gate。这个集成点不是本轮新发现的框架大收益，收益应归于后续真正测出的实现。

当前明确结论：**没有证据支持再实施一个纯框架 GEMM 形状大改。** mixed 分流的负结果保留，主负责人推进图内 GEMM 定位合理。
