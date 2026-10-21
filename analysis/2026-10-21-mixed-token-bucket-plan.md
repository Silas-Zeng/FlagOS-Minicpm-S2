# Mixed 尾块 token 分桶：实际调优证据与最小方案

2026-10-21，仅 CPU/source、只读本地 SQLite 副本与公开一手资料。没有 SSH、GPU、运行源码/driver修改或新测试框架。当前 `090505` SQL+C3 accuracy 由唯一device owner执行，本文不提前给它通过结论。

## 本轮结论

下一项最值得短测的框架假设是：**将非uniform、NONE模式的partial-prefill/mixed尾块，按通用有限token bucket执行backbone，同时保持Attention、KV与采样的真实长度。** 目的在于减少任意M带来的新GEMM调优/编译和hidden-state gather代码生成，并尝试使常用tile更规整。它不启用新图、不改官方batch参数、不重写GEMM、不根据4K/16K或并发64识别评测。

已经证明“新shape产生了调优记录”，尚未证明它是SQL后最大耗时，也未证明暖稳态会受益。官方四轮丢首轮，可能排除大部分冷收益；因此必须单独看暖路径，不能把一次冷启动暂停外推成官方大收益。

## 已确认的DB差分

读取 [083031 control](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083031Z-sql-decode-context16k-control/db-after/manifest.json>)、[084659 control](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T084659Z-sql-decode-context16k-long-control/db-after/manifest.json>) 的before/after `snapshot.sqlite`，使用SQLite URI `mode=ro`及`PRAGMA query_only=ON`。这些文件被.gitignore隐藏于普通`rg --files`结果，实体确实存在，不能由默认文件搜索误判未下载。

| 基点run | 表 / 行变化 | 新增主体MM数据 |
|---|---|---|
| 083031，16K/128、32req | 479/17982 →481/18052 | **M=952**，四个(N,K)各15条benchmark和1条best config |
| 084659，16K/1024、32req | 481/18052 →483/18119 | **M=259**，同四个(N,K)各15条benchmark和1条best config |

四个(N,K)准确为 **(2560,2048)、(2048,2048)、(12288,2048)、(2048,6144)**，分别与模型QKV/O/gate-up/down主体投影相符；dtype全部BF16。其benchmark table是 `mm_kernel_36ce59dd..._benchmark_v2-45d27be3...`，best table是 `mm_kernel_7ea0a6df...-45eed726...`。这是 **4种配置供42层168次投影复用**，不是168次独立调优。

actual [Iluvatar mm.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/remote-source/iluvatar_mm.py:51>) SHA256 `4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090`，明确以M/N/K为调优key，候选剪枝`top_k=15`、warmup5/rep10，与新增行吻合。M为runtime参数；不能因此声称每个M必然重新编译所有二进制，当前只证明新的调优/配置记录，编译耗时仍未知。

索引差分也很具体：

- 083031新config表 `_index_linearized_jit_function_21535ae1...-9924b48...`：key16、BF16 input/int32 index/BF16 output，1行；对应新benchmark表 `d8cbd53b..._benchmark_v2-be4075...`，2行。另一个既有int32/int64/int32 index表增加2条benchmark和1条规范key960的config。
- 084659新benchmark表 `199da4c4..._benchmark_v2-be4075...`：raw key29、BF16/int32/BF16、2条；新config表 `279e11bc...-9924b48...`：规范key32、同dtype、1条。actual [index.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/remote-source/decode-gap/index.py:619>) 的source key含完整input shape，调优key另用align32，二者不是同一缓存层。

这些BF16索引更像`hidden_states[logits_indices]`：它的input从[M,2048]改变，indices为int32、输出真实请求行。**这是结合源码的推断，未用生成模块source/hash精确映射。** 它们不是已准备的async-token融合所替代的int32→int32采样ID gather。该融合不能消除四种MM新key，也不能消除这里的BF16索引新表，因此不再把它当这批长尾的主要解法。

084659后，MM best表有很多非规则M，但**320/384/512/960/1024均没有这四种投影的配置，2048已有**。不能因为2048暖就将所有尾块塞到2048，也不能声称128分桶候选目前已暖。分桶规则必须来自通用tile/开销折中，自己的首轮bucket调优须如实记录。

## 对现有16K结果的正确解释

32req、16K/128：SQL+C2 131.739373s，SQL+C3 120.670244s。其10秒服务日志仅达到约17 running、53% KV，反对将它当满容量常驻负载。16K/1024基点084659为236.025033s，随后warm C2为231.3221s、mixed为220.3681s；后两者由root确认KV均521840、DB三项hash相同，约4.97%吞吐增量是当前可比的单次信号。没有用它给bucket候选预估百分比。

084659日志从31 running/1 waiting、99.8% KV，到30/2、97.3%；这支持容量压力下出现重新排队的可能性。没有逐请求scheduler事件，不能仅由该日志给出精确preemption次数或重计算成本。`active backend ... event timing` warning及GPU0%采样与新调优存在，尚无精准时间归因。

## 为什么已有padding未覆盖

实际归档 [runner](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/source/model_runner.py:3891>) 与framework owner的[独立source审查](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-mixed-token-bucket-source-review.md>)相符：

1. `_determine_batch_execution_and_padding`先`_pad_for_sequence_parallelism`，再交cudagraph dispatcher。当前TP=1且SP关闭，前者不改M；FULL_DECODE_ONLY的mixed请求进入NONE，descriptor保留真实M。编译范围(1,2048)只使动态图可复用，**不等于GEMM的M被规整**。
2. execute只在mode FULL时设置`pad_attn=True`。NONE时`_build_attention_metadata`继续接真实M，`num_actual_tokens`、cu-query、seq_lens和请求数不padding。
3. actual Triton backend分离KV update；runner `_get_slot_mappings`仍按backbone B建立slot-map视图，并已有`slot_mapping[M:B].fill_(-1)`。上游 [v0.24 KV writer](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/ops/triton_reshape_and_cache_flash.py)先查负slot再load K/V，符合padding哨兵机制；实施前须核对实际installed writer，公开同版不能代替其hash。
4. [preprocess](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/source/model_runner.py:3508>)已有`positions[M:B].zero_()`，但text input_ids仅返回`[:B]`，**没有清尾token IDs**。新策略必须同流把input_ids[M:B]填合法ID0，不能靠旧buffer碰巧有效。
5. attention只读query[:M]、写output[:M]；保留C3也接受Q/K/V/output.shape0>=M，所以增加backbone B不天然关闭C3。postprocess仍用原`logits_indices`取N个真实采样行。

公开 [v0.24 attention builder](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/backend.py) 及实际downloaded backend佐证真实长度与图buffer边界的区分。无需改FULL_DECODE_ONLY配置或启用piecewise图。

## 最小可行补丁设计（尚未实现）

首候选只用一个规则：**mixed/nonuniform、max_query_len>1、M>=256，B=ceil(M/128)*128，且B<=原max_num_tokens；B=M则原路。** 当前上限2048，但实现从实际config/buffer取上限，不识别输入长度、请求总数或benchmark。仅真实execute路径；profile/dummy/capture的强制调用保留原路。小M、puredecode、FULL、spec/LoRA/DP/TP/PP/DCP/ubatching、非MiniCPM BF16、MM/prompt embeddings/aux等非审计路径全回原行为。

仅需三个小接点，不写新kernel、不改调度：

- 对已审计runner方法做原source hash guard；原`_determine...`返回NONE且nonuniform后，用`dataclasses.replace(batch_desc,num_tokens=B)`，保留mode、num_reqs、uniform和其余tuple。不能通过假装uniform/FULL来蹭decode graph；观测stats如启用，需如实更新padding数。
- 在preprocess同一current stream，仅额外清input_ids[M:B]=0；positions沿原清零逻辑。H2D/pinned buffer等待和所有真实[M]输入保持原序；不新增CPU/GPU同步。
- 继续使用原slot-map尾-1与真实attn metadata；postprocess、LM-head、sampling metadata、N与logits_indices不动。统计只用CPU descriptor，禁止`.item()`读GPU。

### 硬件上为什么128值得先试

本实例是32GiB/16SM/native warp64，不能套全板64GiB。当前DB的M259选中BM为128/128/256/128，M952四种BM均256。**保持这些配置时**，259→384的M向CTA数仍3/3/2/3，952→1024仍各4；原GEMM本来就计算整个尾tile。因此数值上的额外行比例（259加48.3%、952加7.6%）不等于主dot FLOPs同比增长。rowwise norm/activation/embedding仍有额外开销，其他shape/新选中配置可能增加CTA，不能先承诺暖速度。

128对齐把256..2048范围收敛到有限15个bucket，并把hidden gather input shape的任意M收敛；它没有降低真实Attention计算或改变KV长度。首候选不扫描多组粒度，不因当前DB缺哪些key临时换策略。

## 必须明确的正确性与成本边界

- **不能先称bitwise。** 有效行逐row数学没有改变，但M改变会让autotuner选不同BM/BN/warps/BK/SPLIT_K。当前三种M的best均BK32/SPLIT_K1，也不足以保证将来bucket配置和编译归约顺序一致。短门先比真实有效hidden/logits/KV逐位；失败记录差异并停止扩大，不靠容差冒充accuracy。
- **RNG行数不变是设计约束，不是已验证结果。** 不给padding追加request/采样行，不重排真实行，不跳过partial-prefill被discard的采样；这样采样调用数、shape与噪声消耗应保持。若logits有差异，输出仍可能变化，最终仍需独立accuracy。
- **pad activation尾不是新请求。** Attention只写有效[M]，其余output尾可能含旧值/NaN；标准linear/RMSNorm/SILU逐row，不应回流真实行，KV writer也应先跳负slot。首门要用污染尾验证这条隔离，而不能只比全零尾。若不能证明installed编译路径隔离，可保守在attention输出后清[M:B]，但那会每层新增工作，应单独记成本，不默默忽略或默认制造42个额外launch。
- **峰值不能由B<=2048自动证明。** 原profile最大2048已覆盖大shape，但bucket可能选另一workspace/config；候选要记录实际KV capacity与显存峰值。不得手调0.85或KV bytes来掩盖新峰值。
- **没有新的全局调优cache。** SQL按表反射、DB keys/config rows、autotuning策略都保持。不能直接改MM key把M259伪装成384而实际tensor仍259，这会改变调优契约且不能解决input shape source生成。

## 官方丢首轮后的反证与最短设备决策

actual [官方脚本](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/remote-source/benchmark_throughput_serve.py:379>) SHA256 `0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565`：同服务每档4次，统计第2–4次，不清进程/DB。若第一轮恰好见过全部后续M，避免调优的收益可能全部被丢掉；若后续完成/重新准入时产生新M，才仍有冷shape暴露。当前before/after只能证明两次各出现新M，不能证明官方保留三轮持续如此。

后续设备仍唯一owner、accuracy结束后串行，最小顺序：

1. 两个已有实形状M259/952的真实backbone短门，仅比原与bucket有效hidden/logits、KV及RNG状态；含一轮pad尾污染与接下一真实step，不另建大测试框架。新bucket config/source/异常全部留档。若不bitwise，先停止，将风险交给owner决定而非自动跑大accuracy。
2. 若门通过，同一32req、16K/1024、官方SERVER做一次原SQL+C3与加bucket短pair，**分别报告各自首见与暖复用**。用DB前后指纹确认4best/60benchmark是否被收敛，原始logs看0%空洞是否消失。不能偷偷提前用baseline调优结果只暖候选，也不删库强制冷测。
3. 若暖结果没有信号或更慢，即使首见变快也降级；不继续扩大粒度扫描。若暖路径稳定改善，再进入后续官方四轮与accuracy程序。本文没有申请或启动这轮设备。

## 三项联合交付delta独立封装审查

[联合delta](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode.patch>) SHA256 `4b3e2e52b01d04a0f0477ae4e9b8dc3fed3c1f721360af3bbe6b01014572bbba`，直接接retained，不先叠两个旧delta。

独立从diff的new-file内容逐字重建，三个模块分别精确匹配owner文件：SQL `ad84c9af...`、decode launch `e5f68a30...`、mixed `a129361f...`。对原审计runner `446f12c0...`在内存中应用唯一append hunk，得到 **`e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1`**，精确对应080656服务版本。footer顺序SQL→C2→mixed正确；mixed要求已安装原e5代理，均早于图捕获。没有额外候选、参数改动或封装阻断项；没有重做已通过的代码测试。bucket方案未放入该delta，当前accuracy测的仍是原版本。
