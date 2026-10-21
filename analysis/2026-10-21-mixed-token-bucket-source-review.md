# Mixed token M 分桶：实际源码审阅

2026-10-21，供 hardware 的独立 proposal 合并引用。只读本地 actual 源码/已有结果与固定 v0.24 一手源码，无 SSH/GPU、无候选修改、无新增测试框架。现有候选冻结；此文不是新优化的正确性或性能结论。

## 为什么出现 M952 / M259

hardware 对 `083031` 与 `084659` run-control 的 SQLite 前后快照只读比较：分别新增 M952、M259 四种投影的 4 best + 60 benchmark 配置。N/K 对应 QKV、O、gate-up、down。新 index 为 BF16 输入输出，index 长度 raw16/raw29，不符合整数 sampled-token 更新，**更符合**最终 hidden gather；没有生成源码/调用栈的直接映射，仍应标为推断。

实际 runner 镜像 `tmp/remote-source/model_runner.py` SHA256 `446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64`：

| 行 | 证据 |
|---|---|
| 4202–4207 | M 是本次所有请求 scheduled tokens 的总和；真实请求数另有 N。 |
| 3489–3495 | 只有启用 SP 且 TP>1 才做 TP 整除 padding；当前 TP1不改变 M。 |
| 3913–3949 | 非 uniform decode 交 dispatcher；FULL_DECODE_ONLY 下 mixed runtime NONE，descriptor 保留真实 M。 |
| 4248–4251 | 后续模型行数直接取 descriptor.num_tokens；请求数独立取 num_reqs。 |
| 4441、4455 | `hidden_states[logits_indices]` 后才算 LM head；这处 BF16 gather 的输入第一维也随模型 M 改变。 |

因此 partial chunk/mixed 尾步没有自动复用 decode graph 的行数 bucket。**不能仅从数据库倒推出 M952/M259 当步的精确 decode/prefill 组成**；那需要真实 scheduled-token 记录。此处不是“全模型重新 Inductor 编译”的证明，已知后者采用 `(1,2048)` 范围编译。

## 可实现的最小边界

独立候选可只给 **mode NONE、非 uniform decode、M>=256** 的真实文本计算行数做通用 `B=ceil(M/128)*128`；B 不能超过原 `max_num_tokens`，当前为2048。B=M 无操作。128 是有限形状策略，不识别 benchmark、并发数或4K/16K，不查询哪个 DB shape 恰好已暖。首版限定 MiniCPM BF16、TP/PP/DP1、无SP/LoRA/spec/MM/prompt-embeds/ubatch/cascade/跨层共享KV与quant，不碰 pure-decode FULL/capture。

最小挂点是原 `_determine_batch_execution_and_padding` 执行后，仅 `replace(batch_descriptor, num_tokens=B)` 并保持 mode NONE、num_reqs/uniform 及其余返回值；再在原 `_preprocess` 完成后填合法尾 input IDs。它使用已有持久 `input_ids`、positions、slot_mapping 容量，无需另造整模型 staging 或 graph。多卡/DP同步等不满足 scope 时直接原路，不能让只改本地 descriptor 与同步 token count 不一致。

这仍是**待实现/待设备验证**的边界，不是建议直接改一个整数后视为正确。

## 必须保持的语义

1. **请求、调度与 RNG 不动。** `scheduler_output`、query_start_loc、真实 M/N、seq_lens、computed-token 计数及 logits_indices 不变。`:2231` 用真实 query_start_loc 求每个请求末 token；`:2225–2233` 明确 partial-prefill 请求也先采样再 discard。不能删掉这些采样行，更不能把 padding 行送进 LM head/sampler。这样才保持原 N 行与随机数消耗；GEMM 数值改变仍可能改变最终 token。
2. **尾 token ID 必须合法。** 原 `:3612` 只取 `input_ids[:B]`，没有清尾；`:2011–2016` 只更新真实 M 行，不能依赖剩余存储是合法历史 ID。新增尾 `input_ids[M:B]=0` 在原 input-prep 生命周期/当前 stream 中完成，避免 embedding 越界。`:3621–3623` 已将普通 positions[M:B] 清零，不能为此添加全卡同步；mRoPE/XDRoPE 初版排除。
3. **Attention metadata 保持真实 M。** `:4277` 的 pad_attn 仍为 `mode==FULL`，所以 NONE 下 `:4338–4341` 传给 metadata 的 padded参数仍为None；`:2301–2302` 回到 M/N，`:2408` 的 num_actual_tokens 应仍为 M。不能为了模型 B 把 attention metadata 的 actual token 改成 B。
4. **KV 写必须屏蔽尾。** actual Triton backend `tmp/remote-source/triton_attn.py:275` 是 separate KV update；runner `:4325–4333` 因此取长度 B 的 slot_mapping，`:4085–4089` 已把 M:B 填为 -1。backend `:758–766` 将该 mapping 传给 cache writer。[vLLM v0.24 cache kernel:56–60](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/ops/triton_reshape_and_cache_flash.py#L56-L60) 在读 K/V 前对负 slot 返回。实际 installed cache-writer 源尚未在本轮镜像/hash中核实，不能以 tag 源冒充其 exact 身份；设备门需确认真实 KV 哨兵不变。
5. **只有模型中间张量扩大。** backend `:643/646` 只计算 query/output[:M]，`:676` 返回完整 output。M:B attention output 未写，但本模型后续 O/GEMM、逐行 RMSNorm/Silu、QKV/RoPE 不跨 token 行运算；padding NaN 在该限定数学结构下不应传播进真实行。无需在方案阶段强行增加42层zero kernel。若真实输出/alias实现存在跨行依赖则拒绝该路径，不能把“尾不采样”当作任意模型都安全的证明。

当前 natural-prefix mixed candidate 的 `_compatible` 使用 query/key/value/output.shape[0] **>=** actual M，并按metadata的真实 M切片，因此 B>M 不会天然使它fallback；仍需独立验证与新的数值风险，不能继承现候选的 accuracy。

## 量级、内存与数值边界

hardware 发现旧 M259 的四投影 BM 为128/128/256/128，M952均BM256。**若保持原配置**，259→384与952→1024的 M 方向 CTA数不变，支持它可能不是按 B/M 比例增加 dot 工作；但新 M 的 autotuner 可以选择不同配置，不能把这个条件观察说成必然零代价。embedding、norm、activation、RoPE与尾部 KV 检查仍有额外行工作，259→384约多48.3%行，952→1024约多7.6%行，只发生于命中尾步。

`:778–782` 的 input/positions 已有 max-token 容量；`:6382–6394` 的 memory profile 曾跑 max2048，并不自动证明所有新 B 的调优配置/workspace峰值都较小。首设备门至少记录实际 KV容量/峰值，不能隐藏额外内存或通过修改官方 gpu-memory-utilization 抹平。改 M 会改变 vendor MM 选择，数学上真实行独立也**不能承诺 bitwise 或准确率不变**。

## 官方跳过首轮后收益是否还在

官方原脚本 SHA `0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565` 每档4次、取后三次，服务进程并不为每次测量重启。相同 M 已在首轮暖过且后续轨迹相同，首次生成/15配置调优收益会从计分中消失；此时 padding 可能只剩额外工作。**这是否定“发现冷 shape 就必然改善官方分数”的直接反证。**

但 skip1 仅剔除一次 measurement，不保证后续没有新动态 M；请求混合/分配时序、KV驻留和 prefix cache 状态也可能改变尾部 shape。有限 bucket 可降低跨形状首次成本的频率，而非保证完全消除。持久 DB、Triton binary cache、进程内 overload/config cache 是不同层次，不删库、不挑暖 bucket制造对比。应分别记录冷启动与暖后表现，只有官方原4次结果的后三次仍有收益，才将其作为可计分信号。

现阶段不展开实现。先等当前独立 mixed accuracy/真实性能结果；若后续决定验证此新候选，一次最短真实尾步验证实际行输出、KV写屏蔽及同 N采样形状即可进入同参数短对照，不先铺多套 CPU 模型/大测试框架。
