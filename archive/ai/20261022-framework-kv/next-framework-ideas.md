# 下一项框架候选：2026-10-23 只读筛选

基于当前 422/423 来源、BI-V150（16 SM、warp64、L2 16 MiB、共享内存128 KiB）与既有原件。只读 CPU/社区分析，未实现、SSH、GPU测试或上传；不改 CURRENT、registry。结论：两项机制可解释，但现有预算均不支持现在单独上卡；计算顺序自然命中验证仍是主线。

**1. 页表有效列 H2D：保留低优先级，不新造桥。**

2026-10-23 用户问是否改参数：按当日保存的官网4.1规则，保留8192列容量/行跨度、KV block大小及原SERVER，仅按实际seq及所有消费者读表上界动态缩小搬运范围，属于KV/显存管理实现优化；不能硬编码16K/1024列、减少上下文支持或改benchmark。最终仍需准确率与复现。当前尚未实施。

[上游 MRV2 #25266](https://github.com/vllm-project/vllm/pull/25266) 已用 GPU 持久页表及增量传输避免全表上传；本地可考虑保留原 GPU 行跨度、仅二维搬有效前缀，不引入其 Triton 更新算子或升级框架。这不同于 KV 内容 restore-pitch：现有 SDK 桥 `q-gqa-kv-restore-pitch/biv150_kv_pitched_restore_bridge.cpp`（48295ffd）已使用 `cudaMemcpy2DAsync(..., cudaMemcpyHostToDevice, current_stream)`，只能证明已有接口能力，不能证明窄页表快。

原件 `experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic/native-trace.json` 实为 SQLite。复用 `analysis/q-gqa-puredecode-native.json` 的内部 step 2→3 至 6→7 映射，排除前两步边界 sync 扰动；`ts/dur` 单位 ns，`bytes` 单位 B。定位查询：

```sql
SELECT id, correlationId, ts, dur, bytes, streamId
FROM cuda_memcpy
WHERE processId=390300 AND correlationId IN
 (2687571,2688022,2688473,2688924,2689375)
ORDER BY ts;
```

五笔均为 pinned HtoD、stream1、1,015,808 B，等于31×8192×4，结合原 `commit_block_table()` 全行上传路径可归为页表大小匹配的复制；没有指针/调用栈级归因。GPU耗时依次40.115、39.726、39.923、39.946、39.773 µs。对应相邻 `cuda_graph` 起点差54.480117、54.478300、54.438639、54.492507、54.452983 ms，平均39.8966 µs / 54.4685092 ms = **0.073247%**：这是完全免除此笔 DMA 的当前窗口预算上界，不是可实现收益。各 gap 为2.062–2.118 ms，复制确实在两 graph 之间；下一 graph API已提前约50.8–51.2 ms提交，不能再把省CPU算成减少wall。

423 `copy_block_table()` 的 `np.take` 对 N17全宽重排：557,056 B有效搬出、最低CPU读写1,114,112 B。002156不是423，未记录该段独立CPU耗时。仅替换H2D并不减少全宽take；对非连续 `src[:, :W]` 直接take可能新增连续化临时副本。W=1032时70,176 B、少87.4%仅是16K+128的几何例，不能代替本次真实块数。统一Attention有未加mask的页表 `tl.load`，宽度须覆盖各消费者tile读表上界，GPU整stride、pinned寿命、原stream/event及尾部有效性都须保持。

仅当后续现成mixed轨迹显示该复制/重排真正曝光且预算明显增长时再开最短门：CPU确认全部读表宽度，再由owner做一次有效列/尾毒化与原路径逐位比较，最后关闭诊断做可比短pair；2D提交/行片段成本吃掉DMA节省即停止。本轮不做这些测试。

**2. 全部中间 chunked-prefill 免 LM head：本轮停止。**

当前 runner `4471–4472` 已先 `hidden_states[logits_indices]` 再计算 N行 logits；`_is_all_reqs_chunked_prefill()`（4140）只检查本次discard mask全真，现用于PP广播优化。故 [vllm-metal RFC #525](https://github.com/vllm-project/vllm-metal/issues/525) 的全M行投影→选N行大收益在本地已经不存在，不能借其数字。这里理论上只省最终全discard的N行LM head，仍需等shape/dtype的有效dummy logits、原N行sampler与原RNG调用。

源码 `_bookkeeping_sync()` 对discarded的seeded generator仍做offset−4；async的 `prev_req_id_to_index` 排除这些行，且不追加其输出token。任何后续实现都须保留这些推进/回退、原采样行数、请求映射；logprobs、prompt logprobs、自定义处理器、spec、PP、dummy/capture等消费者未逐项闭合，不能仅凭discard就删全部后处理。

现成 `analysis/q-gqa-mixed-coverage-only-short.json` 与 `q-gqa-puredecode-mixed-coverage.json` 均有 metadata_steps−mixed_steps=9。观察器在max_query_len=1时先跳过，因此这是所记录范围内全部q>1的9步；未记录discard mask、未保证负载全程覆盖，既不证明9次可省，也不是完整官方轮次上界。002156 N31投影匹配的 `linear_kernel` 为0.929–0.942 ms，仅作量级参考，不能当N1纯prefill实测；即按9×0.94 ms也仅约8.5 ms，还未扣dummy logits及门判断成本。当前不足以支持新增实现/独立GPU诊断。只有未来既有轨迹显示大量全discard步骤及可观LM head占比时，才考虑一次原RNG状态/后续生成token对齐门。

**社区大机制过滤。** [2026-09 AgentX packed KV](https://vllm-project.github.io/2026/09/08/vllm-agentx.html) 与 [2026-01 KV offloading](https://vllm.ai/blog/2026-01-08-kv-offloading-connector) 将跨层/多组KV放进连续块，省描述符与传输碎片；当前单组Full Attention已做真实42层restore-pitch，尚无新的曝光传输预算，不能把DeepSeek92张量或高prefix复用收益移植成MiniCPM结论。[#39936](https://github.com/vllm-project/vllm/pull/39936) 专攻多组metadata CPU launch，作者亦说明1–2组收益小，不重开CPU starvation。[#51482](https://github.com/vllm-project/vllm/pull/51482) 是恢复关闭prefix caching时LIFO语义的回归修复，证据是TPU故障消失，不是BI-V150吞吐证据。此次未找到足以替代当前计算顺序主线的新大收益框架候选，不以盲组合凑下一轮。
