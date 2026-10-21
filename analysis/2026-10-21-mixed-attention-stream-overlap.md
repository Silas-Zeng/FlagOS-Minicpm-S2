# 一项新框架假设：重叠既有 mixed 两段 Attention

2026-10-21，`/root/hardware_innovation`。本轮只做CPU源码、已归档日志和公开一手资料研究；没有SSH/GPU，没有新增或修改runtime/driver。root当前唯一GPU为110149 fresh16Klong基点，growth在后；本文不改变其队列。新bucket105930的两case Attention/整KV/nextdecode逐位门已由root报告通过，尚非整模型结论。

## 为什么只选择这一项

**现有C3已把mixed Attention拆成独立的decode 3D和prefill 2D，但仍在同一stream顺序执行。** 可以只改变这两段的提交依赖，使同层的decode和prefill在两条stream尝试重叠；两者完成后再执行原整批O projection/MLP。它在42层重复、可作用每个真正split的mixed step，比每步只一次的最终hidden gather有更大作用范围，同时不拆整模型GEMM、不重排请求、不改采样N/RNG或浮点算法。

这仍是**待验证假设**：BI-V150的16SM可能被任一kernel占满；CoreX也可能实际串行不同stream的compute。共享带宽、寄存器资源和额外wait/record开销可能使它变慢。当前没有并发能力或性能证据，不能据“stream不同”声称已重叠。

## actual源码证据与准确挂点

| 实际源 | 身份/位置 | 结论 |
|---|---|---|
| `patches/framework/biv150_mixed_decode.py` | SHA `a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42`，`_wrap_backend.forward`尾部 | `plan.prepare_consumer`后先`original_forward(...plan.decode...)`，再`original_forward(...plan.prefill...)`；两者当前同stream。query/output以自然prefix边界切片，地址不重排。 |
| `experiments/official/20261021T092944Z-sql-mixed-official/source/installed/vllm/v1/attention/backends/triton_attn.py` | SHA `1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605`，forward末段约640–676、separate KV writer | Decoder forward只读已写入的cache，按metadata实际M切Q和out，不再次写KV。两段的输出行区间互不重叠。 |
| 同目录`ops/triton_unified_attention.py` | SHA `54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f`，`use_3d`至launch/reducer | `max_seqlen_q>1`使prefill固定2D，2D的segment指针直接用out占位，代码不触3D scratch；decode3D写segment tensors并运行reducer。 |
| `patches/framework/biv150_decode_launch_runtime.py` | 原C2 SHA `e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f` | 3D launch原w2s1/math/grid/reducer保持；新方案只改变两段所在stream。 |

上述读写隔离成立于当前严格scope：单卡BF16 MiniCPM、natural-prefix plan、无quant/shared-KV/cascade/MM/alibi/sinks等，decode数量不超过原3D阈值，prefill确有max_query>1。scope不扩张到任意索引分组、pure decode或CUDA capture，不同时实现另一份all-singleton gather/scatter。

公开[固定vLLM v0.24 unified Attention](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/ops/triton_unified_attention.py)也区分2D直写与3D scratch/reduce；它提供机制参考，不能替代上表的actual SHA，亦不用于升级分支。

## 最小实现边界（本轮未写代码）

未来应在新隔离source中，显式安装一个约束在当前C3上的forward wrapper，保留原builder与原fallback。当前C3由`functools.wraps`保留`__wrapped__`，可在核对a129模块、wrapper code来源、marker与实际backend函数身份后取得它保存的原backend forward；**不能让新wrapper再递归调用C3 split而重复两段**。不复制统一Attention长参数列表，不替换算子backend，不更改编译tile/warp/stage。

只有通过原C3的scope、plan和输入布局校验时启用；还应排除output与query/KV/scratch共享storage等不在实际正常路径内的alias。QKV本身可为原投影输出的stride view，不能为获得contiguous而复制。两个output切片须按原真实token boundary证明不重叠。

使用一个设备级、长期存活的side stream，避免每层/每步创建stream；不跨GPU，不启动第二服务或benchmark。伪依赖为：

```text
原current: 原QKV/RoPE/独立KV写完成的队列位置 ──┬── prefill 2D ───┐
                                             └── decode 3D + reduce ─┤
原current:                                   wait side ── 原整批O/MLP
```

具体顺序：先在原current执行`plan.prepare_consumer`，side `wait_stream(current)`获取Q、KV和metadata就绪；在side提交原decode forward，在current提交原prefill forward；返回前current `wait_stream(side)`，保证随后整批projection能读全部output。这里的wait仅建立设备依赖，不执行host synchronize。所有原kernel、数学、归约和真实输入输出不变。

必须对side读取的Q/cache/seq_lens/block_table/query_start_loc与写入的prefix output、3D scratch登记`record_stream(side)`，保留必要metadata强引用直到安全使用；不能把record_stream当readiness。side的3D reducer结束也属于join前置条件，否则下一层可能重用同一scratch覆盖未完成的partial sum。主stream的join还要在下一步元数据H2D/CPU staging对应GPU更新之前，避免side读到下一步seq_lens/页表。若这些依赖无法明确建立，直接保留原顺序C3。

runtime不得在某一段已launch之后捕获异常再静默fallback，否则会重复写输出；不支持stream的失败只能在launch前禁用该候选，或者让本实验明确失败并清理。capture和puredecode继续原C3逻辑，FULL_DECODE_ONLY启动参数不动。

[PyTorch2.10 CUDA stream语义](https://docs.pytorch.org/docs/2.10/notes/cuda.html#cuda-streams)要求对非默认stream显式建立依赖和allocator生命周期关系。它并不保证当前CoreX设备能让这两个具体kernel并发；这点必须实测。[Flash-Decoding作者说明](https://pytorch.org/blog/flash-decoding/)解释decode与长query Attention的并行维度和资源需求不同，可用于形成假设，不能把其中NVIDIA硬件倍数移到本BI-V150。

## 收益上界与直接反证

设同层其他工作为G、decode为D、prefill为P。现路径为`G+D+P`；理想重叠至少为`G+max(D,P)+新增依赖开销`，所以最多省`min(D,P)`再扣stream开销。这个上界来自依赖图，**不是性能预测**。42层都会遇到同一提交机制，但不能把旧单层微测乘42当整模型加速，更不能推官方成绩。

现3D decode已有16segments并行，不是低occupancy空壳；prefill也可能同时需要全部16SM/HBM。若真实设备只允许一个kernel占满驻留资源，两个stream只争用队列；即使timeline看似交错，总完成时间也可能无改善。每层多一组wait/record、更多CPU Python提交也会有成本。side stream不额外分配KV、QKV或整批output，仍要记录显存和KV容量，不承诺零内存开销。

天然prefix命中不足也会把总收益压低；本方案不为追求覆盖而重排真实请求。它不减少cold shape数量，所以理论暖态价值不依赖首轮JIT/SQL miss；但是否有暖态收益仍须原官方skip1后三轮核实。

## 最短设备决策

不另做“空kernel并发能力”或失败external-event试验；正常CoreX streams已有正确性门，直接在唯一owner空闲时做**一个真实mixed层的顺序/双stream对照**更便宜。初始只用一档代表满chunk的D29/P2019/长KV16K，保持已审actual Builder/Impl、原KV布局和C2/C3；它是合成代表形状，不是按该数字写入runtime。

1. 先用同一真实输入比较全有效output及padding sentinel bitwise，原KV整tensor不变；连续执行两次不同Q的调用，中间不host同步，并在主stream消费输出，覆盖join与scratch再次复用。异常必须保留原日志，不能只看进程exit0。
2. 编译/初始化放计时前。只比较原顺序C3和新stream顺序，少量AB/BA重复，用整段host monotonic clock+每组末一次device synchronize计完整关键路径，包含所有wait/record开销。不用external timing events、不启profiler、不做多tile穷举；没有明确局部正信号就停止。
3. 若bitwise且warm局部总时长有稳定可辨下降，再在新隔离source做一次同参数16K/1024/32req短服务pair，记录实际split命中/元数据/KV容量/DB与吞吐/TTFT。只有正向筛选才扩官方accuracy/完整复现，不能继承原103/105。

若第一档无收益，记录“两个实际kernel在此设备/shape的重叠不值得stream成本”，不据此泛称所有CoreX stream都不支持并发。本轮产物仅此一个明确方案；未修改runtime/driver，未声称任何新设备结果。

## 后继明确授权：独立single-layer原型已备齐

root随后明确授权CPU-only创建新runtime原型和单层gate；以下覆盖前文研究时点“未写代码”。现有a129/冻结source/任何driver仍未改。

| 产物 | SHA256 |
|---|---|
| `patches/framework/biv150_mixed_attention_overlap.py` | `93c3124ccab9311cb98f319d9f786f7aae571f9c1d976d1a9f1d623adca378db` |
| `scripts/remote/validate_mixed_attention_overlap.py` | `914f7eb3abee25f05af8cb1a7a78eb96ede7b8c88aaf427014e16b3f745ae291` |
| `analysis/source/mixed-attention-overlap/check_source.py` | `35244e5c225f8ece00ceeb75d4dd3083b6fe76ba725630f6eedf949a364e91fb` |

runtime的`MixedAttentionOverlap`**不安装服务patch**，只是显式调用的独立对象。构造时核C3/a129、backend/attention/helper、C2 proxy和C3 wrapper/原forward code binding；保留原serial callback。只有原C3 scope与plan有效、output row布局固定且不和Q/KV/scratch冲突时选中新路径，其余直接serial。实际KV由调用者先在main写入，入口record普通ready event，side等ready、执行原decode+reducer并record done；主流原prefill后wait done，再交还给调用者。未引入external event、全卡sync或数学改动。

所有临时tensor、metadata、plan、ready/done event有pending frame强引用，tensor按storage去重record_side；仅done.query完成后可collect。**此原型没有设计生产服务的全模型retention峰值**：42层host先行可能累计强引用，puredecode整图又不进入此Python wrapper来reap。因此不能直接服务集成；先用单层门证明有值得继续的局部信号，正面再处理完整生命周期/峰值，避免为无收益并发投入buffer池或线程回调。

gate只一档D29/P2019/KV16384，无模型权重或服务；实际Builder/Impl/C2/C3与actual KV writer f182/alias均守卫。先整输出int16-bitview、valid finite、padding sentinel、整KV不变和RNG；连续两个不同Q调用中间没有host sync，主流立即clone消费输出，检验join和scratch再次复用。然后只做serial/overlap/overlap/serial四组、每组4次，regular timing events与完整hostwall同时记录，包含事件分配/提交/collect成本。普通timing event不可用单列能力错误并保留wall；callback或同步失败直接实验失败，不混为计时能力。没有任何GPU结果或预定正收益。

controller复用既有stdlib帮助函数，持同device lock，真实pre/postflight与无进程，独占GPU child/300秒/owned group清理，归档source、环境版本、stdout与GPU样本。两处source hash都明确is_file，避免__pycache__目录基础错误。最小CPU包装检查实际通过，记录`analysis/source/mixed-attention-overlap/cpu-check.log`；它执行真实runtime导入且不载torch/Triton、核pin的SHA/语法和两个实际hash comprehension含cache目录行为，不模拟CUDA。py_compile/help通过，framework_innovation独立终审上述两个最终SHA无single-layer阻断。未扩旧CPU测试。

root在当前GPU队列结束并清理后若决定试验，上传上述新gate/runtime，以及既有C2 runtime、a129 C3与脚本依赖 `validate_hidden_row_gather.py`（65cb…）、`validate_mixed_decode.py`、`bench_attention_dispatch.py`、`validate_block_table_candidate.py`、`monitor_gpu.sh`。示意调用：

```text
VLLM_PLUGINS=fl PYTHONPATH=<原080656 source> python3 validate_mixed_attention_overlap.py \
  --run-dir /workspace/experiments/minicpm-s2/framework/<唯一UTC>-mixed-overlap \
  --runtime-path <原e5f68 C2 runtime> --mixed-path <原a129 C3> \
  --overlap-path <新93c312 runtime>
```

exit0只表示synthetic单层correctness过且采样已落盘；正负局部信号看原timings/summary。不能把exit0、两stream、计时事件或单层正信号当官方成绩/硬件并发证明/可直接默认集成。

## 实际113727结果与当前gate版本（覆盖旧“未上卡”状态）

root已独占完成113727 gate，原914/core93c的单层bitwise、padding、整KV、RNG、no-plan与pending0均通过。wall约+2.50%而event约-0.77%的信号冲突，**没有选为服务优化**。原始证据和CPU独立解释见 `analysis/2026-10-21-overlap-timing-review.md`。

root随后授权仅最小增加计时调用数和排除Python timing Event构造；当前gateSHA **ab1cd95e2f0582e1efa1deb1321887a041a88a068c655627360bb6eee4817eba**，新增`--timing-loops {4,32,64}`（默认4）。方法v2/loops/worker exactcommand均落manifest/results，原kernel/runtime/shape/correctness suite不动。旧914 bytes已另存analysis/source下并核原hash，原run原件保留。下一次仅选择32或64calls一个ABBA以摊销固定host/计时成本；不能把不同方法的新旧百分比当同条件重复。
