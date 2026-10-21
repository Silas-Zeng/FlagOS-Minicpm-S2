# Retained prefill：原始调参复核与两个有界候选

2026-10-21，hardware_innovation。仅本地CPU/公开一手资料；未SSH/GPU、未写sweep或改运行代码。结论：**没有证据支持再扩大tile/stage扫描；还剩一个可明确删去重复工作的实现点，以及一个较弱、只值得单点反证的16-warp配置。** C2三维w2信号没有参与推断。

## 最新候选状态（覆盖下文研究时的“未测”）

root后续只授权并执行候选一：121838 full-visible-prefix actual层门exit0，policy87c6/gate d3db/generated a6d身份一致，两case bitwise/KV/RNG/padding和2D selection/3D C2 fallback全过。单P2019、预record Event、32calls一次ABBA，wall中位12.594359734375→12.559617125ms（下降0.275858%），event12.491010189→12.434306145ms（下降0.453959%）。**仅保留小单层信号prototype，不服务集成，不扩大accuracy；不能从98.65%可免mask tile比例推论大E2E收益。** 初次按owner回执保存，后继原件已到盘；本owner已CPU读results/manifest并核15个source SHA全匹配，数值/边界一致，未新增设备门。

候选二w16仍未实现、未测，root明确暂不做；本文保留其研究依据与反证，不追加新方案/扫描。实现、准确source SHA与门说明见 `analysis/2026-10-21-prefill-visible-prefix-implementation.md`。

当前root唯一GPU运行 `official/20261021T122607Z-original-baseline`（runner166637，pristine13eb/source091033）；installed attention已恢复为bab2上游。baseline期间禁止import会触发retained/C3/a0c平台runtime写回54c的任何远端代码；这里只做本地文档更新。

## 已测范围，不能重复

直接逐行读取 `experiments/remote-evidence/a4-triton-attention-tune/` 四CSV：`prefill-chunk2048.csv`、`prefill-chunk2048-refined.csv`、`prefill-full16k.csv`、`prefill-chunk2048-batch8.csv`，合计42行、17个独特 `(BM,T,warp,stage)`。原始上游SHA为bab2c0…，不是候选研究所据54c源码；这些是历史方向证据，**不作当前候选的直接计时基线**。

| BM | 已测 `(T,warp,stage)` |
|---:|---|
| 16 | (32,4,3) |
| 32 | (32,4,1), (64,8,1) |
| 64 | (32,4,1), (64,4,1), (64,8,1), (128,8,1) |
| 128 | (32,4,1), (32,8,1), (64,4,1), **(64,8,1)**, (64,8,2), (64,8,3), (128,8,1) |
| 256 | (32,8,1), (64,8,1), (128,8,1) |

三个精调shape都用后11项；前一个探索CSV额外含BM32/64点。BF16、GQA16Q/2KV/H128、page16。历史精调中位ms：

| 固定BM128/T64 | Q2048/KV16K/batch1 | Q16K/KV16K/batch1 | Q2048/KV16K/batch8 |
|---|---:|---:|---:|
| w4/s1 | 16.70456 | 69.74302 | 129.77150 |
| **w8/s1** | **10.65874** | **44.70315** | **83.37065** |
| w8/s2 | 10.97998 | 45.32349 | 86.52393 |
| w8/s3 | 28.68077 | 120.95296 | 227.99873 |

T128/w8/s1为17.93738/75.73483/141.86635；BM256最优也为13.26891/56.57554/105.74295，均输给保留项。BM128/T32/w8也输，故不重测这些点。历史max_abs_diff不是当前bitwise或整模型accuracy证明。

## 实际挂点与硬件反证

候选研究/变换所据的归档实际源为 `experiments/official/20261021T092944Z-sql-mixed-official/source/installed/vllm/v1/attention/ops/triton_unified_attention.py` SHA **54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f**；同目录helper SHA **59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1**。这不是12:26原始baseline期间的installed状态。

- 54c:869–882设置BM128/BLOCK_Q16/T64/w8/s1；402–562为实际2D内循环，496–527每tile构造causal mask并选择S；helper:396保留在线softmax。
- GQA已将8个Q heads放在同tile，复用一次K/V；不存在简单“再合并8个head便省8倍读取”的机会。
- Q2048单序列时grid129、有效128个qblocks，只有1个早退块；每KV head相同，虚拟CTA数仅0.775%。Q16K为0.0976%。这些还是**CTA数量上限而非时间占比**；不能把裁holes/binary-search包装成大收益。当前C3后缀已排掉自然decode prefix。
- [FlagTree Iluvatar compiler](https://github.com/flagos-ai/FlagTree/blob/main/third_party/iluvatar/backend/compiler.py)明确warp64和capability71→ivcore11。它只佐证线程/布局机制，公开main不等于安装编译器，不能据此移植新pass或套用NVIDIA寄存器容量。

## 候选一：完整可见前缀与原masked尾分开（优先的实现点）

**未测差异**：保持BM128/T64/w8/s1、tile顺序、dot/FP32 accumulator/原`softmax_step`和epilogue；仅对严格普通causal、完整16-query qblock，把 `[0, full_tiles)` 的逐元素causal mask去掉，后续tile继续原mask。`full_tiles=floor((context_len+q_block_local_idx*16+1)/64)`，clamp到原loop范围。这些tile的最大key不大于最小query，原8192个mask元素全部true。不能按GQA展平的BM128当成128个token计算边界。

Q2048/KV16384的128个qblocks合计30784个tile，其中30656个完全可见，**99.584% tile可以省mask生成/score选择**。Q2048首次prefill/context0为1984/2112=93.939%；Q16K/context0为130560/131584=99.222%。这些计数没有乘KV-head数，比例不变。

真实C3代表后缀P2019/KV16K，context14365：127个qblocks，其中末块只有3query，保留整个原循环。其余126个完整qblocks仍可免30177/30590=98.650%的tile mask；未对齐时尾端可能有两个masked tile，不能写死一个。scope不接3D/puredecode、TD、量化、window/chunk、MM-prefix、per-seq causal、alibi、sinks、QQbias、softcap或其他特殊模式；不改KV、metadata、请求顺序/采样/RNG。

[Triton官方FA2教程](https://triton-lang.org/main/getting-started/tutorials/06-fused-attention.html)已经将完整历史区与对角区分开，仅对后者生成causal mask。这里只借鉴分区原理；不路由教程kernel、不搬exp2/新归约、不升级框架。当前warp64大tile的8192元素mask是准确删除对象，但没有实际指令/寄存器资料证明它是CoreX主瓶颈。

**收益上界**：只删除布尔/选择/相关mask活跃值；K/V字节、QK/PV dot及softmax全部不变。99.584%不能解释为99.584%时间收益。设当前E2E中此2D路径占比为f、其可省mask成本占比为m，理想时间下降至多f·m，吞吐倍率至多`1/(1-f*m)`；例如f=30%、m=20%才对应6%时间/6.38%吞吐，这只是条件算术。没有当前无profilerphase占比和编译资源证据，无法给可信实测百分比。

**最短真实层门**：只一个actual backend/helper/54c派生新kernel，P2019/KV16384/page16、16Q/2KV/H128/BF16；真实随机物理页表而非假设连续KV。它同时触发完整前缀、未对齐尾和3-query末块。原KV update后比同配置串行当前2D，输出int16 bits、padding哨兵/整KV/RNG；预热后一次32calls ABBA同时记event与完整wall。bitwise不等先归档数值候选，不能继承103/105；无清楚速度信号立即停止，不扩整套shape。若速度明确才补context0/边界的必要正确性及服务短pair，之后才准确率/官方大测。

## 候选二：仅BM128/T64的w16/s1单点（低优先）

**确实未测**：42行中完全没有16warp；只改w8→w16，BM/T/stage不变。依据是此2D实际同shape w8比w4快约36%，三个历史shape方向一致，不能由C2w2推导。warp64下线程数512→1024，BM128/H128的16384个FP32 accumulator元素在理想均分下32→16个/线程；这只是元素算术，**不是实际寄存器计数或occupancy**。

本地FlagGems5.3.5 `_iluvatar/tune_configs.yaml` 的bmm/mm确有w16，而attention候选只列w4/w8。这说明16warp并非生态中不存在，但既不证明本kernel可编译，也不支持“16越多越快”。更多线程可能降低CTA驻留、增加warp间通信；没有实际n_regs/n_spills/shared/thread-limit记录，不能称它为高置信大收益。BM256失败也说明扩大tile与提高warp数不能混为一项。

**最短验证/上界**：如root愿花一次很短门，沿同一P2019实际层仅试w16，编译/资源拒绝即停，不再衍生w2/w32/T128扫描；记录编译资源与bits/event/wall。无2倍延迟收益依据；严格上界仍是f（只有该2D阶段可能改善），具体上界须资源与新单层结果才能收紧。它不优先于已有growthV2，更不应在没有门的情况下改默认。

上文保留最初研究记录。后继候选一已按root授权独立实现并完成121838单层门；最新状态见顶部。候选二仍未做。没有E2E/accuracy结论，不安排额外测试。
