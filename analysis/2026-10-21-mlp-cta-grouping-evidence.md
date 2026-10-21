# MLP CTA grouping：冻结前已完成证据与未实施门草案

2026-10-21，hardware_innovation。本轮只做本地stdlib源码、真实trace、immutable SQLite阅读与一手资料。**用户随后要求停止探索，并只完成已经开始的工作。中断前未写候选runtime、source transformer或可执行GPU门，因此不再扩大实现；现保留证据和设计交接，未服务集成、未上卡。** 不新增tile/warp/stage变体或后续方向。

## 实际留下的产物

- `analysis/source/mlp-cta-grouping/iluvatar_mm_original.py`：actual installed源码的持久只读副本，SHA **4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090**，原来自 `tmp/remote-source/iluvatar_mm.py`。没有改动它或冻结候选。
- `analysis/source/mlp-cta-grouping/evidence.json`：原trace、来源SHA、按真实shape聚合的kernel/grid/block/register/shared字段、6个既有DB best rows，以及121838原件身份核对。SHA **875f2662e1fc9045ce9d4116ab9deea41a7ad758a8fbe5af58c9fc8fd256e320**。
- 本说明及 `docs/agent-work/hardware_innovation.md`。不存在已完成的grouping runtime/kernel、CPU bijection测试脚本或GPU gate；不能把下面设计描述成实现/验证完成。

## 为什么没有继续追小launch/metadata/GQA重复

实际缓存图 `tmp/remote-source/computation_graph.py` SHA **ab75722cd9edd5cbd33a2bb72d3f17f090eb2796ec86386d777a852f8e9cd69c** 已有42个KV/Attention opaque段和43个编译段；RMSNorm/SiLU/RoPE周围的逐元素式子经过Inductor融合。不能把图上每个mul/cat/index_select当成独立GPU launch。

旧真实prefill trace `experiments/profiles/b0-triton-16k-prefill/prefill/trace/rank0.1792528309825622459.pt.trace.json.gz`，原gzip SHA **1a7f511d2a0d30f6aa36e1f590cc11babaf788ae148fe83c42870f77943aa310**，948个kernel。按原ts/dur合并，kernel区间并集3720.346239ms、首末span3757.450509ms，内部空隙37.104270ms，约0.99%；这只是**旧profile窗口**，不能等同修复SQL后的服务占比或当前host空洞。

同trace中，RoPE相关 `triton_poi_fused_3` 为82次/6.716336ms，KVwriter84次/2.542130ms；两者合9.258466ms。真实图/trace并不支持再将这些路径假设成几十个未融合launch。原runner `_build_attention_metadata:2445–2517` 按group build并将同一个metadata对象分配给各layer；没有42次独立builder/H2D的源码依据。actual unified attention已在一个KV head tile中复用8个Q heads，不存在未消掉的8倍GQA展开。

121838 full-visible-prefix原件已到本地；本owner已读results/manifest并实际核15个source SHA全匹配。输出/KV/RNG/selection checks全true，32calls ABBA仅wall下降0.275858%、event下降0.453959%，仍只保存prototype。它反对把“98.65% tile的mask恒true”外推为大收益，但不证明所有算子数据复用机会都没有价值。

## 唯一保留的机制证据：固定tile，改变GEMM CTA枚举

这不是新发明：旧 `analysis/2026-10-21-gemm-launch-research.md` 已把grouping列作小M后备，尚未实施。本轮新增的是**真实M2048 prefill trace与当前best config对上**，不是重做旧tile sweep或裸 `F.linear` 微测。

actual mm源码 `:113–122` 把grouped PID代码注释，实际为 `pid_m=pid//grid_n, pid_n=pid%grid_n`，N索引变化最快；`:206–237` 的 `_launch_mm` 却固定传 `GROUP_M=8`。因此这个参数目前不影响CTA映射。

旧trace按CPU `External id` 映射真实矩阵shape，不根据kernel名字猜投影：

| BF16实际投影，M2048 | 次数/合计ms | grid/block | regs/thread/shared |
|---|---:|---|---|
| gate-up K2048→N12288 | 84 / 117.804835 | 384 / 1024线程 | 97 / 65536B |
| down K6144→N2048 | 84 / 60.900605 | 128 / 512线程 | 97 / 49152B |

两MLP合178.705440ms，是上面RoPE+KVwriter基数的约19.3倍，但**不是当前E2E份额**。旧attention配置/上下文与retained/C3不同，不能把其6.04% GEMM百分比或任何除法外推到当前服务。

独立以SQLite `mode=ro&immutable=1` 读取 `experiments/framework/20261021T115950Z-growth-v2-warm-repeat-context16k-long-control/db-after/snapshot.sqlite`，文件SHA **29fb47cbfdaa445875e8962dc1bc3f6eb36bffaee7006c2472d59947c5179074**。best表为 `mm_kernel_7ea0a6df3012d3bc5475d21d5eb156a7-45eed7266d4cc0f7be44aaaa091bc3b1`：

| M/N/K | BM/BN/BK | SPLIT_K | warps/stages/ctas |
|---|---|---:|---|
| 2048/12288/2048 | 256/256/32 | 1 | 16/2/1 |
| 2048/2048/6144 | 256/128/32 | 1 | 8/2/1 |

由DB得到的grid8×48=384、8×16=128及warp64线程数与旧trace匹配；没有从grid唯一反推BM/BN。evidence.json也保留既有M259/952 rows供防重，不是新变体建议。**旧trace没有把当时源码4c2e/DB整份hash绑定在同一manifest；当前配置一致性是交叉佐证，不能伪称旧trace已证明当前compiled实例身份。**

一个Mtile扫描完整N后才到下个Mtile；gate-up/down独特权重48/24MiB均大于实际BI-V150的16MiB L2。M2048/BM256有8个Mtiles，若相同Ntile的8个Mtiles相邻，存在更短的B tile复用距离。忽略cache，原CTA对权重的请求量分别为8×48/24MiB；这些是请求量而非HBM实测流量，更不代表8倍提速。gate-up输入8MiB、down输入24MiB也会竞争L2，尤其down可能因A复用变差而输。

[Triton官方matmul教程](https://triton-lang.org/main/getting-started/tutorials/03-matrix-multiplication.html)明确用program重排改善L2复用；这里只借鉴映射机制，不引用其A100收益预测BI-V150。[FlagGems v5.3.5一手源码](https://github.com/flagos-ai/FlagGems/blob/v5.3.5/src/flag_gems/runtime/backend/_iluvatar/ops/mm.py)可对照该路径，本地actual hash才是候选实现的固定输入，不升级框架或路由到现成其它后端。

## 冻结时的候选/门设计，均未实施

只比较原枚举和group8，固定上表全部BM/BN/BK、warps/stages、SPLIT_K1、`fp8_fast_accum=True`、FP32 accumulator、BF16输入输出、原K循环、input precision、%M/%N加载、输出mask与stride。不动decode，不新增packing/fusion/其它group值，不改任何模型或服务参数。

拟用独立源提取actual4c2e的同一个JIT体，baseline保原枚举，candidate只改PID整数映射；现有调优器/DB保持只读，不能让新kernel重新autotune后把配置差当grouping收益。严格同设备BF16、M>=256、仅MiniCPM这两MLP投影、SPLIT_K1，unsupported走原mm_out；第一门只准备上表M2048两点，未承诺服务中所有任意M皆已验证。

映射草案：令R=ceil(M/BM)、C=ceil(N/BN)、W=8C；第g组从r0=8g开始，实际组高h=min(8,R-r0)。程序pid的组内序号u=pid-gW，对应 `(row,col)=(r0+u mod h, floor(u/h))`。h不是固定8，末组仍正确；每组u覆盖0..hC-1，除法/余数给出行列笛卡尔积的一一映射，组之间行区间不相交。必须使用组内u，不直接套旧注释的全局pid取模。原每输出tile的K顺序保持，SPLIT_K1无跨CTA浮点归约；仍不许省略GPU bitwise门。

最短门草案仅有：一次含非8倍末组及partial M行的CPU bijection检查；root设备空闲后，同上表两投影真实stride/固定C0参数，baseline/candidate int16逐位、输入和RNG不变，再各一次32calls预record Event ABBA。没有裸F.linear、tile扫描、精度大测或服务集成。若编译/bitwise失败或两计时方向不一致、收益不清楚，停止；若grouping不改真实cache命中/矩阵已compute-bound也停止。**这些检查当前全部未执行，GPU gate脚本也不存在。**

## 当前交接与恢复边界

用户冻结优先。所有已有prototype（包括小mask信号）保存但不默认启用；本grouping只有证据和设计，没有runtime需要回滚。原official122607仍由root独占，installed bab2，绝对不import任何可能写回54c的retained/C3远端平台代码。

只在用户以后明确恢复此方向时，先读本文件/evidence.json、确认live源码4c2e与当时best config是否仍同，再决定是否完成独立实现和上述一次必要门；不能直接把旧DB当当前配置。当前收尾交framework作只读证据/映射审阅，收到回执落handoff即结束本线，不因公开教程或逻辑读量继续开新探索。
