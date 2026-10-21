# 图内 GEMM 的最小 launch 与数据移动研究

2026-10-21，Asia/Shanghai。第三轮 CPU/源码研究，没有启动 GPU、连接远端或写新大 kernel。attention 的直接映射和 mixed split 微测反证已补入 `2026-10-21-large-gain-hardware.md`；不再按空 CTA/masked 行比例估计整模型大收益。

## 当前证据边界

已读 `scripts/remote/bench_decode_gemm.py`。它只调用 `F.linear`，没有显式安装插件/FlagGems上下文，没有记录实际 kernel/config，不包含图回放和候选输出比较。独立运行它，不能默认测到当前模型 graph 内的 `mm_kernel`。

本地核对的源码是 FlagGems v5.3.5 解包目录 `tmp/src/FlagGems-clean/FlagGems-5.3.5/`；其 Iluvatar mm.py SHA256 为 `4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090`，与 snapshot 副本相同；tune_configs.yaml SHA256为 `dd1c7432a84b72dde9fe7d48527f4b1744383fa188a6feb69adb1d8fe5748bc0`。**仍需GPU owner核对实际import源/哈希以及图内配置**，不能将本地解包源码无条件等同正在执行的代码。

可公开核对的相同结构见 [FlagGems Iluvatar mm 源码](https://github.com/flagos-ai/FlagGems/blob/master/src/flag_gems/runtime/backend/_iluvatar/ops/mm.py)；参考版本不用于升级。该实现是每个输出tile沿K顺序循环、SPLIT_K=1时直接写回，运行候选由M/N/K调优选择。[FlagTree Iluvatar 编译器](https://github.com/flagos-ai/FlagTree/blob/main/third_party/iluvatar/backend/compiler.py) 定义warp64，因此warp4/8/16对应256/512/1024线程。允许配置power-of-two并不自动保证某个GEMM shape编译成功或运行更快。

## 先确认实际图内热点

先做最短观察：两个真实decode迭代，记录四投影的实际 M/K/N、对应kernel、best config（BM/BN/BK/warps/stages）、权重stride、是否存在额外contiguous/transpose/copy。若CoreX profiler无法展开graph，用相同算子路径的最小decoder-layer capture/replay，不能用图外LM-head代替。

模型42层、四投影共168次GEMM；gate-up与down占投影权重80%，但**权重份额不等于时间份额**。四类shape为：

| 投影 | K→N | 每层BF16权重 | 图内值得先测的M |
|---|---:|---:|---|
| qkv | 2048→2560 | 10 MiB | 真实capture桶 |
| o | 2048→2048 | 8 MiB | 真实capture桶 |
| gate-up | 2048→12288 | 48 MiB | 32、64；对应实际30/56等padding |
| down | 6144→2048 | 24 MiB | 同上 |

如果实际热点确是这份 mm，先聚焦两个MLP shape和M32/64；不一次跑原脚本7档M×4层的全表。只有结果证明有价值再覆盖其余真实shape。

## 第一轮只改 BM/BN/num_warps

对每个shape先保存实际选中的baseline配置C0，随后复用**同一个JIT算术体**：

| 候选 | 相对C0的唯一变化 | 机制与反证 |
|---|---|---|
| Cw | num_warps由8降4（若baseline16，则先8） | 少线程/warp间协作可能改善16SM资源利用；但每线程accumulator增多可能抵消甚至spilling，不能预期线性加速 |
| Cm | M>32且baseline BM32时改BM64，其他不动 | 减少M方向独立tiles，可能减少weight重复读取；若已BM64或M≤32，则没有这项traffic收益，不重复测等价候选 |
| Cmw | 只有Cw/Cm至少一项显示收益、另一项无明显退化时才组合 | 可能减少weight读同时保持合适并发；BM翻倍且warp减半会提高每线程寄存器压力，应检查编译寄存器/溢出信息 |
| Cn（后备） | 固定BM/warp，将BN64→128，或实际基线相邻合理值 | 减少N方向CTA与A重读，改变访存向量/计算粒度；不减少每个Mtile需要的独特weight总量，且可能使总CTA太少 |

全部固定：BK、stages、SPLIT_K=1、FP32 accumulator、输入/输出BF16、input_precision、`fp8_fast_accum`、tl.dot的acc形式、循环方向、stride和写回cast。这里 `fp8_fast_accum` 是该通用实现控制 `tl.dot(a,b,acc)` 与单独加法分支的参数名，**BF16输入也需保持原值**；不能以“本项目没FP8”为理由随意改它。

不要第一轮加SPLIT_K或改BK。它们会直接改变K分组与归约路线。先不prepack、不融合epilogue、不切到现成vendor实现、不动框架版本。

**K循环源码不变仍不是bitwise保证**：BM/BN/warp改变可能让编译器选择不同MMA布局和指令分解。每个候选必须对相同输入和相同baseline输出做逐位检查；随机BF16需加入足够K累积、抵消值与实际层输入。若不逐位同，先记录为数值变更候选，不能宣称“保留归约顺序”或直接集成。

## BM64 能省什么，不能省什么

忽略L2命中时，M方向tile对weight读量的放大近似 `ceil(M/BM)`。M64/BM32为2，改BM64为1；M56同理。M30/32时BM32与BM64都为1，不存在weight读量减半。

本实例L2记录为16MiB。gate-up的48MiB与down的24MiB均大于L2；当前N-major CTA次序下，第二个Mtile隔完整个N扫描才再次访问同一weight。BM64有机会消除这部分重复；若MLP实际全部选BM32，那么42层两投影的CTA请求weight量上界可由约5.906GiB降至2.953GiB。**这不是HBM实测流量，更不是整模型快一倍**：L2已经可能吸收部分重复，BM64也增加寄存器和每CTA计算。

BN128在down的N2048时仅16个CTA（BM覆盖M的情况），恰好一CTA/SM；BN256只8个CTA，会低于16SM。qkv的BN128有20CTA，gate-up有96CTA。首轮不使用统一BN256策略；宁可先保持实际baseline BN，再决定局部改变。

## 第二步数据移动后备：恢复相邻 M 的 weight tile 复用

本地 mm.py 传入 `GROUP_M=8`，但grouped PID映射被注释，实际 `pid_m=pid//grid_n`、`pid_n=pid%grid_n`。M64/BM32时，所有N列的第一个Mtile完成后才处理第二个Mtile；对48/24MiB矩阵会使weight重用距离超过16MiB L2。

可作为launch候选之后的独立最小实现：恢复原grouped PID映射，使同一个Ntile的两个相邻Mtile先后/邻近调度。保持BM/BN/BK/warps/stages及全部算术不变，既不改accumulator尺寸，也不改任一输出元素的K遍历。这比引入split-K/packing更容易追求逐位同，但仍须验证编译结果、边界与输出。

M≤32且BM32时只有一个Mtile，这个方案不会增加weight复用，应跳过。M>BM时才比较，重点M64两类MLP。最短测试是C0与grouped两种，确认调度为一一覆盖输出tile、无重复/遗漏，再同输入bitwise与小次序交换计时。若L2/带宽没有改善或耗时无信号，停止，不继续扩大为persistent大kernel。

## 计时和整模型取舍

计时必须包含相同算子真实路径与capture环境，编译/调优/初始化放在计时前，所有候选复用同一权重与输入。仅做少量预热、交替次序的配对重复；record warm-cache条件，因为gate-up48MiB、down24MiB均大于16MiB L2，而小投影可能驻留。

输出不仅写FLOP/s/`weight_bytes/time`，还需实际config、bitwise状态、graph replay时间与加权预测：`ΔT_graph≈42×Σ投影(t_baseline−t_candidate)`。`weight_bytes/time`只按独特weight算，是有效速率，不是显存实际流量。最终以相同服务参数的整模型短A/B判断，不靠局部百分比挑选。

本轮不设“必须出现大收益”的结论。若profile表明GEMM占比低、候选非逐位同或实际收益不稳定，就记录反证，继续定位真实graph主体，而不放大微测结果。
