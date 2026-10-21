# 面向大收益的 BI-V150 第二轮机制研究

2026-10-21，Asia/Shanghai。仅阅读本地源码、已有结果和公开一手源码；没有远端操作或 GPU 工作。遵守原服务参数、单设备、MiniCPM5-2B、禁止量化/投机超参数路线、不合并新版框架等约束。

## 后续微测已缩小前两项的收益预期

主负责人后续报告：direct3D 有效输出逐位一致，4K/B64 从 1.6999 降至 1.67835 ms（约1.3%），16K/B30 从3.02027降至3.01511 ms（约0.17%）。原先少1/3早退CTA的算术计数不能预测实际速度。此项只保留为低风险的小候选，未证明整模型收益。

Mixed split 在不含metadata成本的上界微测中：D16/P2032的4K为2.779→2.737 ms、16K为12.590→12.219 ms；D63/P1985的4K约0.5%，D63/P127的4K略慢；D29/P2019的16K约0.7%，只有D29/P127的16K为4.732→4.409 ms（约6.8%）。prefill输出逐位一致，decode出现0.00049–0.00244最大差异。**mixed分流暂缓集成，仅保留长KV短prefill尾部候选。** 不能因128行仅8行有效就宣称有接近16倍局部空间。

下面保留原机制与条件预算作为研究历史；当前主线已转至图内GEMM，见 `analysis/2026-10-21-gemm-launch-research.md`。本段数据来自GPU owner报告，不是本研究智能体测量；原始日志由owner归档。

## 先把收益基数算清楚

主负责人观察的 decode 模型主体 graph 约 150–400 ms/步，而旧 a3 图外 LM-head `linear_kernel` 约 1.093 ms/步。图外 profiler 的算子百分比漏掉了 graph 内绝大多数层，不能据此把 LM-head 或 sampler 尾部列成整模型最大热点。

模型有 42 层，每层 4 个主要投影，共 **168 次 GEMM**；四投影权重总计约 **3.691 GiB BF16**，不包括 embedding/LM-head。gate-up 和 down 分别占其参数量的 53.3% 和 26.7%。因此若图内 GEMM 低效，优先检查 MLP 两投影，比只看图外 LM-head 更可能形成大收益。

按 42 层、2 KV heads、head size 128、BF16，KV 每 token 为 42 KiB。单步完整读取独特 KV 的理论数据量：

| 工作形状 | 42 层独特 K+V 数据量 |
|---|---:|
| B64，L4096 | 10.5 GiB |
| B30，L16384 | 19.6875 GiB |

这只是算法数据量，没有包含事务放大、额外读写或 cache 命中，不能拿它冒充实测 HBM 带宽。已有纯 decode attention 微测约 1.705/3.021 ms/层，乘 42 为 71.6/126.9 ms；这些是确定热点方向的量级估算，不能直接等同真实 graph 中的相位占比。

**已排除一种虚高解释**：当前 [unified attention 源码](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/ops/triton_unified_attention.py) 以 KV head 为 grid 轴，将其 8 个 query heads 放进同一 Q tile 并复用一次 K/V load。源码没有将 2 KV heads 先展开成 16 heads；没有证据支持“消掉 GQA 八倍重复读取就能八倍提速”。需要研究的是实际事务效率、分页寻址、分段执行和无效计算。

## 三个具体机制

以下按当前可落地的研究顺序列出。表中整模型时间下降采用 `f × s`，其中 f 是真实关键路径占比，s 是该部分时间减少比例；数字为**条件预算，不是已测收益**。

| 机制 | 核心改动 | 条件收益预算 | 最短反证 |
|---|---|---|---|
| 1. 纯 decode 3D 直接映射 | IS_3D 的 grid0 改成实际 seq 数；直接定位 query 起点/长度与 seq_len，避免通用查询块上界和搜索；不动算术与归约 | 若 attention 占 50%，局部减少 10%，整步减少 5%；不能把少 1/3 CTA 解释成局部快 1/3 | 大量 CTA 本来很快早退，真实 attention 时间几乎不变，或 real QKV 不是逐位一致 |
| 2. 混合批次在 attention 边界分流 | 同一批 GEMM 不拆；attention 按 decode/prefill 请求分别使用各自合适的 tile/分段 | 若混合 attention 占总体 40%，分流令它减少一半，则整步/总任务时间减少约 20%；需先测混合阶段占比 | 混合迭代很少，或多一次 attention launch/metadata 工作抵消收益 |
| 3. 图内 small-M GEMM 实现与形状策略 | 针对实际 M 的低 warp 数投影实现，模型加载时可做无损权重 packing；在框架图边界保持合适形状 | 若图内 GEMM 占 40%，MLP 路径减少 40%，全图约减少 16%；其正确估值必须按各投影耗时加权 | 图内线性已经接近本设备可达带宽/算力，或当前 graph 已采用良好的专用实现 |

### 1. 直接 decode 映射：当前待评审、待逐位验证

当前 MiniCPM decode 默认 `BLOCK_M=16`、GQA8，故 `BLOCK_Q=2`。包装器使用通用上界 `floor(q_tokens/2)+num_seqs`；每序列只有一个 query 时，只需 B 个有效 query blocks，却发出约 1.5B 个 blocks。再乘 2 KV heads 和 16 segments，B64 约发 3072 个 CTA，只有 2048 个做有效计算；B30 约发 1440 个，只有 960 个有效。

主负责人已将最小方案交独立 reviewer：**仅 IS_3D 分支**将 `seq_idx=program_id(0)`、`q_block_local_idx=0`，加载 `query_start_loc[seq_idx:seq_idx+2]` 与 seq_len；grid0=num_seqs。保留 TILE16、BM16、warp/stages、16 segments、partial buffer 排列以及 `reduce_segments`。2D 的通用 binary search 与 holes 布局原样保留。

这不是对已拒绝 TILE32 decode 候选的复活，目标是保留相同有效算术和浮点归约顺序。必须 gate 到真实单 query decode；零长度 padded row 仍要早退，不能把“纯 decode”错误理解为每行一定有效。

最短实验由 GPU owner 串行执行：先 CPU 映射覆盖 B1/8/30/64、空 padded row，再对两档真实/随机 QKV 验证输出逐位一致，只测基线与该候选两种；随后短 greedy token 一致与一次同形状 graph replay A/B。若不逐位一致，先修映射，不以“BF16误差很小”放行。没有明显局部收益也如实记录，不扩大成 tile 搜索。

后备方向是分段策略。[TritonAttentionMetadataBuilder](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/backends/triton_attn.py) 固定 2D 最小 grid 128、16 个 softmax segments；2 KV heads 得 threshold64，没有按 16 SM 调节。segments4/8 可作为后备，但会改变归约顺序，风险显著高于直接映射。既往 decode tile 改动导致 accuracy83.8%，因此后备应先用真实逐层输出/logits 和短 greedy 找分歧，而非直接跑完整 math500。

### 2. 混合 attention 分流：比单纯裁 graph 更有上限

当前保留优化以批次 `max_seqlen_q>1` 选择 BM128/BLOCK_Q16。只要一个请求正在 prefill，同一次 `unified_attention` 中的 decode 请求也使用这个策略，并因该条件被放到 2D 路径。对 GQA8 的单 token decode，请求实际只有 8 个有效 query-head 行，却进入 128 行 tile；其 dot、softmax 和 PV 模板仍按该 tile 执行，不能把 masked 行当成没有成本。

这是一处**框架批次边界决定算子形状**的问题。候选应当仅在 attention 边界拆请求：prefill 保留已通过准确率的 BM128 路径，decode 先使用原基线 BM16/TILE16/16segments；KV cache 写入、四大投影与整个 batch 的 GEMM 仍只执行一次。避免把整个模型拆成两次 forward，那会重复读取约 3.7 GiB 投影权重，并让 GEMM 数量翻倍。

[runner](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/worker/gpu_model_runner.py) 已有 `reorder_batch_threshold`/`reorder_batch_to_split_decodes_and_prefills` 机制；Triton attention 当前没有声明 decode/prefill 拆分元数据。可用 CPU 已知 query lengths 确定 decode-first 请求和 token 连续区，构建两组 view、重新归零的 cu_query_lens、对应 block-table/seq_lens view。输出写入原 output 的正确切片，保持采样请求顺序。不能每层新增一次 GPU→CPU query_len 读取。

最短实验不是全模型实现：先单层构造 `query_lens=[1]*D+[P]`，测试 `(D,P,L)=(8,2040,4096)` 与 `(24,2024,16384)`，统一调用对分流调用两种配置，各做少量预热/重复。先比 attention 输出，特别核对 decode 真实上下文、causal offset、页表 view/stride 和 Q 起始位置。因为混合路径从 2D 改 3D，输出可能改变；随后用真实层 QKV 或短端到端 greedy 预检数值影响。若单层有足够收益，再统计实际混合迭代比例，估算整任务上限后决定集成。

### 3. 图内 GEMM：让 16 SM 上的小 M 有实际适配

本地 FlagGems v5.3.5 Iluvatar [tune configs](https://github.com/flagos-ai/FlagGems/blob/v5.3.5/src/flag_gems/runtime/backend/_iluvatar/tune_configs.yaml) 的 mm 候选 `BLOCK_M` 从32起、warp数为8/16，即原生 warp64 下512/1024线程。linear 候选也从BM32起；其实现用 M 取模加载 padding 行。这是检查 M1/8/16 以及 M30/64 实际效率的依据，**不证明图内168次GEMM一定都用这份实现**。已有图外 LM-head 是 `linear_kernel`，图内编译后路径须另核对。

第一步只在实际 graph 形状抓两三个 decode iteration 的内部 kernel 时间、四类投影对应 M/K/N、所选 BM/BN/BK、warps/stages 与是否复制/重排权重；如果现有工具不能可靠展开 CoreX graph，使用同权重、同输入、相同 capture 路径的最小 decoder-layer replay。不要根据图外10ms可见kernels的百分比推断图内耗时。

如 MLP 两投影确为热点，可实现 BM16/32、4 warps 的 BF16 decode 投影模板，固定 SPLIT_K=1/FP32 accumulation，加载时无损 packing，并为 prefill 保留高 M 模板。先聚焦 `gate_up(2048→12288)`、`down(6144→2048)` 的实际 M30/32/56/64，最多两个有机制差异的实现，不做所有参数穷举。融合 SiLU 或 residual epilogue 应在 GEMM 本体有效后再做；单纯少几个 launch 不是读取3.7GiB权重的根治手段。

纯替换成现有 vendor GEMM 不满足“切算子必须有实现变更”的赛规；需要提交实际模板、布局或融合实现。不能借此升级 CoreX/FlagTree/框架分支，也不走低精度权重/KV路线。

## 图 padding、HBM 与不展开的方向

graph padding 需计入真实 GEMM 的 M，但当前 bucket 为16后每8一档，B30→32约6.7%，B57→64约12.3%，并非通用数倍浪费。dummy seq_len=0 通常不会读取整段 KV；精确 M 与 padded M 落在同一 GEMM tile 时，少 padding 甚至不减少核心计算。只有实测这些额外行导致 GEMM 配置跨档、attention 路径变化或大量尾阶段时间时才做 graph 策略。不能按官方并发64硬编码裁图。

HBM/PCIe 不混淆：当前16SM/32GiB为一个可见设备，未实测当前 die 的 HBM 上限；不能把整板宣传数字或 pinned H2D 的几十GB/s当成 HBM效率。KV layout 改造只有在同形状 profile显示事务/寻址放大后才做；RoPE+cache-write、LM-head融合、metadata小copy和线程扫描均不排在以上大杠杆之前。

下一步推荐：先完成正在评审的直接映射逐位微验证，同时由 CPU 侧准备混合 attention 的单层对照；若后者证明机制成立，优先实现分流，再决定是否为图内 MLP 投影投入专用实现。所有通过短筛选的候选最终仍需交叉评审、精确准确率门槛与同参数官方复现。
