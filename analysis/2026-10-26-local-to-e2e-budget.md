# N-only局部收益与整模：先恢复可比性，再解释预算

**最新结论：局部不是完全没传到整体。** 精确身份修复后，4K暖均观察+1.1145%，与下述约1%的条件预算接近；16K首暖−2.7652%，同时存在额外权重容量成本与形状覆盖缺口。此前把部分手工MM微测当生产F.linear、漏核新runner与旧优化栈的集成身份，确实降低了选题判断的可靠性；这些是应改进的实验设计，不用“整体复杂”概括过去。

后续候选先按三项筛选：真实生产调用省多少、实际负载能覆盖多少、新增内存/搬运/同步花多少。局部Graph必须包含完整producer与reducer，形状命中不能用首次selected代替频率，指令/寄存器变化不能替代净计时。当前GQA stages2就是反例：实际async-copy生成且数值通过，但搬运没有排进主要矩阵计算窗口，并增加双缓冲和hot-loop Q读，完整组件反而慢27.6324%。该结论来自已有原件，不为解释重跑模型。

用户最新建议decode小M：优先准备原权重M64 down窄N双波的单一新差分，不保留第二份权重。单份packed＋每次恢复原W虽可省容量，但恢复42层的乐观流量预算约3.18ms，远大于M64单步0.381ms的局部节省；高频fallback尚未封闭，不进入官方。既有M1–8 SplitK、宽tile与旧packed负结果不重复执行。

2026-10-26，仅CPU读取既有原件，无新测试。**当前最明确的问题是新runner没有同步compute-order精确身份，实际日志出现 `BIV150_COMPUTE_ORDER_SCOPE_REJECTED`，所以本轮不是“原完整优化栈＋N-only”严格对照。** [本轮posthoc](../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/posthoc-after-stop.json) 的 `prefill_valid=false`，同时42个N-only FX及新核selected存在；原normalization和Q-hoist仍有局部selected，不能说所有旧优化都关闭。[首暖筛选](../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/performance-stop-decision.json) 5440.33对5533.03 tok/s（−1.6754%）是实际组合结果，但不能全归因N-only，更不否定其组件正确性。42权重helper门没有经过完整compute-order调用链，这正是其明确未覆盖的集成边界；应先修精确身份，不再为这次失配拟合缓存慢因。

**收益账只有条件预算。** [M64原组件](../experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/result.json) A/B为0.085926324129/0.076858177781ms，单层省0.009068146348ms；若每步42层都M64、每层保留同样差额且无其它成本，约省 **0.380862147ms/步**。[当前main6971的4K诊断](main6971-084521-nodes/summary.md) 只有一个M64 Graph的4个插桩样本：每样本GQA区间和中位23.970038ms、全部linear7.960562ms，其中[down42节点](main6971-084521-nodes/linear-breakdown.json)3.645377ms；boundary/full也分别为带计时的34.603107/37.140869ms。0.380862约为该boundary的1.1007%（条件吞吐约+1.1129%），不是10.5534%整模收益。该数字仍不是无插桩E2E预测：没有本轮所有实际M、命中频率或未插桩整图分母，不能将该窗口外推整轮或将GQA/linear中位数相加作官方总时。旧16K的M32/M40分布不是本轮4K频率；首次M64 selected也不是逐请求覆盖率。

**容量下降已发生，但本次4K没有抢占证据。** [本轮server.log](../experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/server.log) 中KV为516320，对基线548336少32016 tokens（按43008B/token折1313.156MiB）。已知packed副本1008MiB只等价24576 tokens；剩余7440 tokens/305.156MiB没有分项证明，不能全部归因pack、Graph池或某个workspace。本地完整server.log检索 `preempt`/`recompute` 均0，52条KV使用率采样最高61.9%；没有另存的累积preemption计数，准确说法是“未发现实际抢占/重算记录”，不是凭空补0次硬计数。4K并发64的请求token账64×(4096+1024)=327680，仅为516320的63.46%（不含内部额外预算），也不支持以容量损失解释这次退化。16K未跑，不能借此排除未来16K容量问题。

**单层Graph与模型交织的差异仍须诚实保留。** 组件是同一layer0权重/合成X、固定Graph在ABBA各臂重复16次；模型42套down权重流经其它投影、native与GQA/KV后再到下一层。单份down权重24MiB已大于L2 16MiB，不能把组件描述为“整权重热驻L2”；42层单格式合1008MiB，重用距离和竞争确实不同，但未测counter，不能断言缓存就是慢因。M64-only的新opaque在非M64回原stable，那里没有GEMM节省；Graph replay不重执行这些Python检查，不能把额外Python调用算成每个图内token成本，图外路径额外dispatch仍是未量化成本。组件省量、模型额外常驻内存及旧栈身份回退必须分开。修复身份后若完整调用仍不正，就保留负结果，不用局部速度为整模结果辩护。

可说：组件正信号真实、M64-only实际启用、旧栈身份失配真实、KV下降真实、4K日志未见抢占。不可说：组件10.55%=整模10.55%、所有M都命中新核、全部退化由容量或缓存造成、旧16K形状代表本次4K、失配组合已否决正确接线版本或取得完整官方/105资格。

## 12:46身份修复v2官方收尾：4K正、16K负，未形成新基线

新run `20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds`修复了旧runner身份遗漏，实际compute-order/normalization/Q-hoist与42pack/FX42均闭合，posthoc `valid=true/prefill_valid=true`。4K四轮4899.30/5700.44/5672.77/5786.23，弃冷暖均5719.813333对5656.77观察 **+1.114476%**；16K冷/首暖3642.71/4005.55，对应首暖4119.46观察 **−2.765168%**后停。六轮1280 SUCCESS；原SIGTERM/exit1是主动早停，清理/DB/source/native恢复通过。无105、合并或新基线，保留混合结果而不称整体收益。

原日志按benchmark首个client时间划分负载窗（本地UTC+8，含setup/初始单请求，非精确GPU活跃窗）：候选4K采样UTC12:08–12:25共100条，KV最高62.6%、Running最高/中位64/64；16K前两轮UTC12:25–12:45共121条，KV最高100%、Running最高/中位31/29。基线相同口径4K103条、最高59.1%/Running64；16K只取前两轮115条、最高100%、Running最高/中位33/31。双方完整server.log未发现preempt/recompute记录，但没有独立累积counter，不写“抢占零次”。[分窗、行号口径和数值](main6971-084521-nodes/nonly-identity-120453-windowstats.json)可复核。

KV仍516320对548336，额外packed1008MiB始终常驻；总容量差1313.156MiB中其余305.156MiB无分项证明。4K未逼满、可出现预期约1%局部预算量级的正观察；16K达到容量上沿且同时Running较少，**支持容量/调度成本可能抵消M64局部收益，但未隔离因果**。Running是请求采样而不是Graph M，本轮没有M调用分布；旧16K M32/M40窗口只能作为适用性先验，不能冒称本轮M64零命中。首次M64选中和FX42也不等于每个16K步都受益；不据此猜cache命中、重算次数或稳定收益。
