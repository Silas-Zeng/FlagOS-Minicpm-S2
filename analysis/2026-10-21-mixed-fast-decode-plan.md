# Mixed Attention 与 fast decode 的最小集成计划

日期：2026-10-21。状态：已有本地 CPU 候选与小测试，尚未集成 mixed 服务补丁。本 agent 没有安装候选、启动 GPU/远端任务或改变官方参数。设备仍由主负责人持同一 `framework-device.lock` 串行使用。

## 判断与证据边界

值得准备一个只覆盖自然单 token 前缀的小范围首版，先等待当前 C2/B0 pure-decode matched 服务与随后四形状 mixed 微测。旧 mixed split 在满 chunk 上的收益不足 1%，但其中 decode 仍使用旧 3D 配置；新的 w2s1 可能改变净收益，不能直接沿用旧否定结论，也不能先承诺 10–20% 服务收益。

已保留证据 `experiments/framework/20261021T044807Z-decode-launch/manifest.json`、`results.json` 和 `source/` 显示：w2s1 在单层 pure 3D graph replay 上，相对 C0 的中位数从 1.695558 ms 降到 0.997373 ms（64 请求、KV 4096，41.18%），从 3.024362 ms 降到 1.803277 ms（30 请求、KV 16384，40.37%）。五项 case gate 与计时后的有效 token 输出检查均通过 finite、bitwise equal；该结论只覆盖所测单层输入，不是官方分数或整模型精度结论。

**pure 3D bitwise equal 不等于 mixed 2D bitwise equal。** w2s1 改变 3D launch 参数，而原 mixed 批因为 `max_query_len>1` 使用 2D prefill 形状。split 令单 token 前缀从 mixed 2D 转到 segmented 3D，softmax 分段和归约顺序改变。旧 `20261021T035611Z-mixed-dispatch` 的四形状中，prefill 输出 bitwise equal，但 decode 输出虽 finite，仍出现最大绝对差 0.00048828125–0.00244140625；未因此通过官方 accuracy。新 fast-decode 不能消除这条已有数值风险。

完整旧反证及调用链见 `analysis/2026-10-21-large-gain-framework.md`；新的 launch 结果见 `analysis/2026-10-21-framework-experiments.md`。

## 源码身份与复现缺口

本次实际后端只读镜像为 `tmp/remote-source/triton_attn.py`。镜像来自设备安装源码，当前本地完整字节 SHA256 为 `1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605`。相应安装模块路径为 `/usr/local/lib/python3.12/site-packages/vllm/v1/attention/backends/triton_attn.py`。最初核对的 `044807` 实验 manifest 没有记录该 backend 文件及其 hash。主负责人随后在 `20261021T051639Z` 开始的新 B0 run 只读核对安装文件，确认与镜像相同，并保存 `backend-source.sha256`；此事实来自设备负责人，本 agent 没有进行远端操作。候选把该 hash 设为安装硬门；新 mixed run 仍须携带完整原始源码及 manifest，不能用本地 ignored 镜像代替归档。

已在 `20261021T044807Z-decode-launch/manifest.json` 中保存的另外两份实际安装源为：

| 文件/安装路径 | SHA256 | 可提交/保留的复现来源 |
|---|---|---|
| `/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py` | `54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f` | 该 run 的 `source/retained_original.py` |
| `/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_attention_helpers.py` | `59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1` | 该 run 的 `source/helpers.py` |
| 微测 w2s1 变体 | `7dd7353f2a828981c30393803a619bd2a93542766e2cfa1cf8c9e3c558023de2` | 该 run 的 `source/w2s1.py`；它不自动证明服务 runtime 的接入 |

实际 runner 镜像 `tmp/remote-source/model_runner.py` 的 SHA256 为 `446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64`，对应保留 B0 runner；固定插件参考为 `tmp/src/vllm-plugin-FL`，base `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`。`tmp/` 是辅助审计镜像，不能作为唯一复现依赖；新实验必须自带所使用源码快照、版本和精确命令，不依赖这些 ignored 文件长期存在。

## 当前排序约定：不能假定已有 decode prefix

实际 `TritonAttentionMetadataBuilder` 没有声明 `reorder_batch_threshold`；此前对 v0.24 基类的审计记录其默认继承值为 `None`。runner 的 `_may_reorder_batch`（实际镜像 1125 行起）仅在计算出的 threshold 非 None 时重排，`calculate_reorder_batch_threshold`（7025 行起）取各 attention builder 的最小请求阈值。首版不改这个值，不启动全局 reorder。

旧请求通常可能在新 prefill 前面，但这不是必须满足的不变量。请求移除、`InputBatch.condense()`、行移动/交换、重新准入都可能让某个多 token prefill 落在前面，使自然单 token 前缀缩短甚至 `D=0`。不能以请求年龄、decode 请求总数、scheduler 字典迭代顺序或上一 step 的 D 代替当前物理行顺序。

应在每批 metadata build 使用当前 `CommonAttentionMetadata.query_start_loc_cpu`，只读取 CPU 张量并求差分。设实际请求数 R、有效 token 数 N、query offsets 为 cu：

- 要求 `cu[0]=0`、`cu[R]=N`、所有实际请求 query 长度正数；首版遇到零 query/padding 不分流。
- D 是从第 0 行开始连续满足 `cu[i+1]-cu[i]==1` 的最大前缀长度；必须 `0<D<R`，因此 `T=cu[D]=D`。
- 后缀至少存在一个 query 长度大于 1；后缀可以仍含单 token 请求，不必再分区。`max_query_len>1` 保证后缀继续走原 2D prefill 路径。
- 首版要求 `D<=seq_threshold_3D`，沿用原 segmented scratch 容量，不强制扩大 buffer 或改变阈值。超过阈值直接走原整批路径。

`seq_lens_cpu_upper_bound` 或 runner 的 `optimistic_seq_lens_cpu` 可给 KV 长度安全上界；识别 D 不需要读取 GPU `seq_lens`、`is_prefilling` 或计算已完成 token。query 长度为 1 的 prompt 尾块也能在该形状路径正确处理，不必把它误称为语义上的已生成 decode。

## 最小实现边界：builder 一次准备，forward 两次读 cache

只在通过精确源码 hash 核对的 `TritonAttentionMetadataBuilder.build` 与 `TritonAttentionImpl.forward` 两处实现。不改 runner 的 token 排列或 scheduler，不把整个模型/Attention layer 执行两次。

runner `_build_attention_metadata` 将 CPU query offsets 放入 `CommonAttentionMetadata`（2402 行）；对同一 attention group 的各层赋同一 `attn_metadata_i`（2516–2517 行）。因此 builder 可在单次 build 中用 `dataclasses.replace` 构造两个子 metadata，再让父 metadata 持有 split plan；MiniCPM 同组 42 层复用它，不做每层规范化。

| 子 metadata 字段/输入 | 单 token 前缀 | 其余后缀 |
|---|---|---|
| `num_actual_tokens` | D | N−D |
| `query_start_loc` | `cu_gpu[:D+1]` | `cu_gpu[D:R+1] - D`，只在 build 执行一次 |
| `seq_lens` | 原 tensor `[:D]` | 原 tensor `[D:R]` |
| `block_table` | 原 tensor `[:D]` | 原 tensor `[D:R]` |
| `slot_mapping` | 对应 token 前缀视图 | 对应 token 后缀视图；保持子 metadata 一致性，不重做 KV 写 |
| `max_query_len` | 1 | CPU 后缀 query 长度的最大值 |
| `max_seq_len` | 首版保留整批安全上界 | 同左，不低估，不为此增加 D2H |
| segmented scratch | 复用 builder 现有 tensor | 2D 不使用它；不新增每层 scratch |
| query/output | 原 `[:D]` 视图 | 原 `[D:N]` 视图 |
| K/V cache | 共用原 cache、原页号 | 共用原 cache、原页号 |

后缀 GPU subtraction 的结果附着到这批 metadata，保持对象活到使用结束；在相同当前 stream 上先准备再执行模型。初版用每批新 device tensor 避免跨 step 复用和捕获地址问题，不新增 pinned CPU 临时源、事件或跨流复用。不能在 42 层各做 `.sub()`，也不能为了边界判定执行 `.cpu()`/`.item()` 读取设备数据。

forward 无 split plan 时直接调用保存的原函数。有 plan 时，以保存的原 `TritonAttentionImpl.forward` 执行两个子批，分别写入原 output 的不重叠切片，最终返回整个原 output。传入子批 key/value 视图以保持接口一致；当前 decoder forward 实际读取 K/V cache，不在这里再写 cache。调用保存的原函数可避免递归进入 wrapper，并保留参数转发，不复制另一份逐渐漂移的 unified_attention 参数列表。

实际 backend 的 `forward_includes_kv_cache_update=False`（275 行），`do_kv_cache_update` 是独立方法（724 行起）。该方案不重做 KV update、RoPE、QKV projection、output projection 或 MLP；两段 Attention 同流执行。query/output 与页表只创建视图，保留 stride；无需 contiguous/concat，不重新编号缓存页。不移动请求，也不改变最终采样 row、logits indices、每请求 generator 或 RNG 调用次数。

## 首版特性与 graph 保护

只在已验证的 MiniCPM5-2B、BI-V150、单卡 dense BF16 decoder 情况启用：标量 `causal=True`、无 KV/query/output 量化、cascade、MM-prefix、alibi、sinks、sliding window、softcap、chunk lookback 或 tensor descriptor；禁用 batch-invariant、ubatch 和 speculation 的分流。相关模型/impl/metadata 条件不满足，保留原函数路径，不猜测特殊参数切片规则。

固定官方模式为 `FULL_DECODE_ONLY`。只给 `max_query_len>1` 且满足保护条件的 mixed 批次附加 split plan；当前 full graph 的 metadata 为 `max_query_len=1`，天然无 plan。builder 与 forward 均排除实际 CUDA capture；pure decode 和 pure prefill 保持原路。仅包装这两个方法不能可靠区分所有普通 dummy mixed 调用，因此主负责人明确接受其满足相同条件时也可分流，不增加 runner scope、长度启发式、设备回读或全局状态。不得为了让候选触发修改 graph sizes、模型参数、官方 serve/benchmark 参数或 padding 规则。

pure decode 仍调用已独立评审/验证的 3D fast launch；本计划不再改其 grid、tile、scratch 或 graph 捕获策略。新增 mixed plan 不能改变图捕获对象的字段和存储地址。若安装时替换了模块/函数，必须确认实际 backend 中已经绑定的 `unified_attention` 引用也指向预期实现，不能仅凭 import 成功推定生效。

## 收益与最短后续验证

当前主线先完成主负责人串行 C2/B0 matched pure-decode 服务，再由同一负责人执行硬件 agent 准备的四形状 mixed fast-decode 微测。此文档不授权另起并发服务、benchmark 或 GPU microbenchmark。

四形状微测应区分 whole mixed 2D、旧 split、fast-decode split，并分别保存 decode/prefill 输出差异；prefill 后缀地址与 offsets 改变后，bitwise 也应实测。输入和 output sentinel/alias gate 应先通过，且时序包含真实 split 调用，不能把预建 metadata 的机会筛选误写成完整服务收益。

若微测有足够稳定的正信号，首版服务集成同时记录自然前缀 D 的批次命中/覆盖，不每步写日志，不为此额外占用设备。只有实际命中频率与节省都成立，才有端到端价值。粗略新增节省是旧独立 decode 耗时下降部分，剩余 prefill 仍可能支配整层；不能把 40% 延迟下降乘 42 后作为模型总收益。

最小 correctness 边界包括 D=0、全单 token、`[1,1,7,9]` 多后缀请求、`[7,1,9]` 不命中、含零长度直接 fallback、以及行 move/swap 后重新 build。mixed 2D→3D 的归约次序差异必须接受单层误差审查和服务精度门；原 baseline 自身 greedy 不稳定的证据也不构成候选正确性的证明。最终仍须准确率和可复现性门，不因“框架切片”豁免。

## 仅作后备：Attention 内 gather/scatter

若自然前缀覆盖不足，可再考虑 Attention 内部 gather 单 token/多 token Q、scatter 输出回原 packed token 位置；CPU token index 与 GPU seq/block-table 重排可按 batch 一次准备。整批投影、全局 packed token 顺序、最终 sampler row 和 RNG 保持不动。

这会增加每层 Q/output 拷贝、额外 launch、临时 buffer 和索引一致性负担；实际字节数应由 dtype/shape 精确计算，不能固定宣称为 8 MB。收益可能覆盖成本，但尚无这条实现的证据。当前不实施该复杂后备，不启用全局 reorder，也不修改采样/RNG 语义来提高命中率。

## CPU 候选实现记录

在设备负责人完成新的四形状 fast-mixed 单层筛选后，本 agent 按授权新增 `patches/framework/biv150_mixed_decode.py` 与 `tests/test_biv150_mixed_decode.py`，尚未在服务中安装或运行 GPU。安装需先有已审计 w2s1 `DecodeLaunch`，同时核对 backend、attention、helpers 和 runtime 源码；失败直接抛错，不静默保留半安装状态。

新 suffix GPU tensor 由共享 plan 的子 metadata 强引用。跨流首次消费在消费 stream 做 `wait_stream(producer)` 建立就绪依赖，并对 suffix tensor 做 `record_stream(consumer)` 防止 metadata 释放后 allocator 提前复用；同一消费 stream 仅登记一次，同创建流无需额外依赖。没有新增全卡同步或 CPU 等待 CUDA event。该协议的 CPU 测试只验证调用和引用关系，不能证明真实 CUDA 排序。

10 项 CPU 测试通过（0.131 s），覆盖 offsets、padding/零长度/自然前缀边界、严格保护条件、原参数对象身份、两段 output alias、42 层共享 plan、跨流依赖只登记一次和安装拒绝源码漂移。首个本机 Anaconda 测试进程因重复 `libiomp5md.dll` 初始化退出；重跑仅在测试子进程设置 `KMP_DUPLICATE_LIB_OK=TRUE`、`OMP_NUM_THREADS=1`、`MKL_NUM_THREADS=1`。这些是包装器的小型 CPU 接口测试，不作为 GPU 精度、生命周期或性能证据。
