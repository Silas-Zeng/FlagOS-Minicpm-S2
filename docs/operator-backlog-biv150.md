# 算子优化候选清单（BI-V150 / MiniCPM5-2B，2026-10-23）

每条都标：状态、依据、预期收益（标注是实测还是推断）、成本、验证方法、合规风险。状态含义：**已合并**（在 main 且默认开启）、**已测负**（有原件，不再试）、**待测**、**设计已备**（代码/方案已写好，等机器）、**多天**。

## A. decode attention（当前 512/510 GB/s，锚点 553）

- **A1 页选择稀疏（Quest 式，上一步页分数复用）** — 设计已备。依据：Quest 2406.10774 自述 1.74×；LServe 2502.14866 自述 decode 1.3–2.1×、页表可跨步复用。预期：f=0.5 → TPOT 60.35→46.6（+29%，推断）。成本 2 h + 精度门。验证：闸门 A（见 A2）→ kernel A/B → 两轮探针 → Level-3。
- **A2 缺页敏感度探针（随机丢一半页 + 首末页保留）** — 设计已备。唯一能先回答"这个基准能不能承受少读页"的实验，25 分钟一次 Level-3。判定 ≥0.965 继续，<0.95 全放弃。
- **A3 每 16 步全量刷新** — 设计已备，配合 A1 防"冷页永不复活"。成本 +6% attention。
- **A4 Quest 原始 min/max 上界（不做时间复用）** — 待测/成本高：需 512 B/页/头 ≈ 1.3 GB 旁路缓冲与一次性扫描（14 ms/序列，摊销后可忽略）。精度比 A1 稳，内存代价大。
- **A5 页内 token 级 eviction（SnapKV/H2O）** — 已判不可行：与分页共享块冲突，要物理搬移 KV。
- **A6 每头流式化（DuoAttention/Razor）** — 待测但风险高：GQA 组内 8 个头若分类不同，ROWS=8 的共享页表要拆成双路径。
- **A7 宽 tile（BLOCK_N=64/128，跨 4/8 页）** — 已测负：pages_per_step=2 即更差（0.9672 vs 0.6471），跨页 mask 与标量页表开销吃掉收益。
- **A8 每 (序列,头) 一 program（SGLang/MetaX 形态）** — 结构性不可移植：GQA 下每头各读一遍 KV，流量 ×8。
- **A9 循环软件流水（tl.range num_stages）** — 已测负：慢 21–35%。
- **A10 evict_first / cache hint** — 已测负：415.2 vs 414.9 GB/s。
- **A11 warps/ROWS 组合** — 已测负：warps=2、ROWS=16 都更差；w1、ROWS=8 最优。
- **A12 split-K 段数自适应** — 已合并。实测最优：b64/4K seg2=0.5242 ms（512 GB/s）、b16/16K seg8=0.5264 ms（510 GB/s）；TARGET_PROGRAMS=256 已经落在最优点。
- **A13 128-bit 向量化加载提示**（`tl.max_contiguous`/`multiple_of`）— 待测，成本 20 分钟，预期 ≤3%。
- **A14 把 reduce_segments 融进最后一次段内累加** — 待测：段数 ≤2 时节省一次 pass（约 0.3 ms/step，约 0.6%）。
- **A15 段内两页一组但共用一次页表向量化加载** — 待测，预期低（A7 的近亲）。
- **A16 用 uint16 索引/更紧凑的地址算术** — 待测，预期 <1%。

## B. prefill attention / 2D 路径（本机占比约 1%）

- **B1 BM128/TILE64/8w/1s** — 已合并（团队 #6，7.1×）。网格已扫尽。
- **B2 TILE128/BM256** — 已测负：b2_q4096 比团队配置慢 21.6%。
- **B3 stages=2/3** — 已测负（团队与另一队都测过，只 +0.04~0.11%）。
- **B4 GQA head packing 更大（BLOCK_Q=32）** — 待测，成本 30 分钟，预期 <2%。
- **B5 prefill 的 split-KV（长序列并行）** — 已判低价值：16K prefill 并行度已足够。

## C. GEMM / 线性层（prefill 91–100% 峰值；decode 267–553 GB/s）

- **C1 int8 权重（W8A8 三 kernel 链）** — 已测负于服务：七种集成形态全失败；孤立 1.18–1.61× 无法落地。
- **C2 W8A16（int8 权重 + bf16 数学）** — 已测负：逐元素加宽，0.20–0.61×。
- **C3 FlagGems scaled_mm（Triton int8 GEMM）** — 已测负：0.52–0.70×（46–64 TOP/s）。
- **C4 原生 int8 GEMM（C++/vendor 无 Python 分发）** — 多天。唯一可能让 prefill GEMM 提升 >20% 的路线（`_int_mm` 已 223 TOP/s）。
- **C5 decode 小 M GEMM 的 split-K**（qkv 267 GB/s、o 276 GB/s）— 待测，但改动在图内 → 撞 fullgraph 墙；除非用 attention 那样的"算子外层"接法（GEMM 没有这层）。预期上限 +2%。
- **C6 lm_head 融合 argmax/sampler** — 待测，上限 2%（0.97 ms + 0.4 ms）。
- **C7 gate_up 合并 GEMM 的 tile 调优** — 已测（small-M 扫描）无收益。
- **C8 权重预转置/布局（NT vs KN）** — 已测（三种 layout bit-exact，差异 <1 ms/step）。

## D. KV / 内存 / 容量

- **D1 int8/fp8 KV** — 已判不可行（dtype 属 serve 超参；shadow 21+10.5 GB > 32 GiB；int8 gather 吞吐仅 1/3）。
- **D2 HND 布局（每 head-page 连续 4 KB）** — 待测/成本中：需同步改 `reshape_and_cache`（FlagGems 硬编码 NHD），且写入在图内。预期 ≤7%（attention 已 92–93% 锚点）。
- **D3 block_size 16→32** — 合规灰色（改基线默认值），且容量粒度变粗；暂不做。
- **D4 提高 KV 容量以提升 16K 并发** — 只能靠减权重（量化，已堵）或减 KV dtype（禁）。
- **D5 释放 tie 无关的 embedding/lm_head** — 不可行（模型需要）。
- **D6 分配器碎片治理（加载期 fp32 临时量）** — 待测：`empty_cache` 影响 <0.1 GiB（已由 agent 核实）。
- **D7 前缀缓存跨轮复用** — 已发生（官方 4 轮/2 轮的第 2 轮起受益），无需改代码。
- **D8 KV 页表紧凑化（int32→int16 页号）** — 待测，收益极小（页表读 320 个标量/步）。

## E. 调度 / 执行

- **E1 CUDA graph 覆盖（FULL_AND_PIECEWISE）** — 需改 serve 参数 → 禁止。
- **E2 图内 kernel 改动必须清编译缓存** — 已确认（陷阱，不是优化）。
- **E3 torch.compile 模式/后端调优** — 待测/合规灰色（`compilation-config` 属 serve 参数，不能改）。若插件内部设置需谨慎。
- **E4 多流重叠 attention 与 GEMM** — 待测/成本高：需要插件改调度，且 decode 是单流图内。
- **E5 每步 CPU 侧开销（metadata/采样）** — 已合并 #1/#2；剩余 <2%。
- **E6 prefill 与 decode 的交错策略** — 属框架侧；改变 per-token 延迟而非总吞吐。
- **E7 准入/水位策略（先进 prefill 再 decode）** — 待测/框架侧，理论上总工作量不变，收益来自 GEMM 效率，风险是 TTFT。
- **E8 max_num_seqs / max_num_batched_tokens 的代码侧默认** — 合规灰色，不做。
- **E9 请求级 batching（客户端）** — 违反 benchmark 协议，禁止。
- **E10 图捕获尺寸集合与 batch 命中率** — 已由 vLLM 固定捕获 35 档；待确认官方 batch 是否总命中（4K 64、16K 30~64）。

## F. 采样 / 输出 / 杂项

- **F1 histogram top-p** — 已合并（13.9×）。
- **F2 采样链融合（softmax+top-p+multinomial 单 kernel）** — 待测，上限 0.4 ms/step（0.8%）。
- **F3 detokenize/输出带宽** — 已测非瓶颈。
- **F4 RoPE 与 KV 写入融合** — vLLM 0.24 在非 ROCm 上强制关闭；profile 显示 0.07%，不做。
- **F5 RMSNorm+residual 融合** — Inductor 已融合，剩余 <1%。
- **F6 词表裁剪/lm_head 稀疏** — 改变输出分布，精度风险高，不做。

## G. 测量 / 流程（避免再走弯路）

- **G1 两轮协议（第 1 轮冷、第 2 轮稳态）** — 已定，官方四轮只在最终交付时跑。
- **G2 预热丢弃首轮 + 记录 install marker** — 已定。
- **G3 精度闸门顺序：先粗筛（贪心指纹，已降级为崩坏检测）→ 官方 Level-3** — 已定。
- **G4 图内改动前清 `torch_compile_cache`** — 强制步骤。
- **G5 停服务按进程组、启动前查显存与端口** — 强制步骤（已有孤儿进程事故）。
- **G6 每次登记都写入 registry + 原件目录，负结果保留** — 已定。

## H. 多天项目（需拍板）

- **H1 原生 int8 GEMM 算子**（C4）：让 `_int_mm` + 融合反量化成为编译器可捕获的单一算子；目标是 prefill GEMM 1.3–1.5×（16K 端到端 +15~20%）。
- **H2 int8 KV + 改写 cache 分配/写路径/两个 attention kernel**：容量翻倍（16K 并发 +100%）+ attention 字节减半，理论 +30~50%，精度风险与工程量都最大。
- **H3 页选择完整版（A1+A4）**：若 A2 探针通过，这是性价比最高的规模化路线。
- **H4 每头自适应预算（Ada-KV/Razor 类）**：需要先做头分类实验（成本 1 天）。

## 结论排序（当前）

1. A2 探针（25 分钟）——决定 A1/H3 是否成立，**必须先做**。
2. A1+A3（2 小时）——若探针通过，预期 +25~39%。
3. C6+F2+A13+A14（各 20–40 分钟，合计 +3~5%）——小而稳。
4. H1/H2——多天，需拍板。
