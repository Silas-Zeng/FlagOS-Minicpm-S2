# 近期论文与作者代码：框架候选筛选（截至2026-10-22）

范围为天数BI-V150/16SM/32GiB/6CPU、MiniCPM5-2B、原服务与benchmark参数。此文是CPU/web-only研究，不加载模型、连接SSH、改运行候选或启动设备。只使用arXiv全文/作者主页/作者代码；检索摘要中的倍率不当本站收益。下文“推论/候选”均是本项目分析，并非论文已在本站验证。

当前root继续独立42层SAVE正确性门；本文不重做短R、WAITING观察、已测C2D微门、全future reserve、terminal-drain或progress-victim失配pair。实际输入长度/抢占/source归档沿现有证据，不能为迁就论文改变输出长度、混入别的模型/量化/推测解码或合并新框架分支。

## 五项一手资料与可迁移边界

### 1. P-PAS：低成本代码切口最具体，但原2048端点已限制其可迁移收益

[P-PAS v2](https://arxiv.org/html/2608.15171v2)，初稿2026-08-15、修订2026-10-09；公开[作者代码与原始结果](https://github.com/TimoSaemann/ppas-vllm)。论文按prefill与decode并存状态动态选预算，小模型主实验覆盖0.5B/3B、RTX5090 32GB，并提供A100/H100结果；评价重点是请求延迟。主3B策略在16384和2048之间切换，表1 makespan相对静态2048改善1.0%，相对16384反慢3.9%；不能用平均延迟改善代表比赛总耗时。[论文第3/5节](https://arxiv.org/html/2608.15171v2#S3)

代码确已公开，但不能整patch照搬：[0.22.1 patch](https://raw.githubusercontent.com/TimoSaemann/ppas-vllm/main/scheduler/ppas_vllm_0.22.1.patch)实际加aggregate-prefill约束，且enabled分支跳过原max-model-len截断；[0.27.1 patch](https://raw.githubusercontent.com/TimoSaemann/ppas-vllm/main/scheduler/ppas_vllm_0.27.1.patch)改为global预算并支持另一pressure信号。两个版本并非逐字相同机制，本站df780不是其中任一基点。这里只读，不安装/merge。源码链接为本次检索时main，未将其当冻结可执行资产。

**本站推论：**现有2048总预算已等于主实验高压小端点；移植其2048 prefill cap几乎是no-op。只有“在原2048上限内，混合高压时再临时缩小”的新子策略值得一次最短反证；这是新推论，不能沿用论文的16384→2048收益。16SM上更小chunk也可能增加forward/权重提交、延长最后请求准入，故没有大收益证据。

**最短测试：**如root选择该方向，先一个实际schedule CPU合同核原maxlen/FCFS/async/预算上界不变、两状态命中，再一个原参数context-screen候选与必要基线；不做预算扫描/纯观察长门，记录实际cap命中、总步与preempt。耗时无改善即保负结果，不追求论文的平均延迟指标。

### 2. eLLM：潜在容量收益最大，但不是当前可小补丁落地的现成实现

[eLLM v2](https://arxiv.org/html/2506.15155v2)，初稿2025-06-18、修订2026-05-06，正文标明DAC2026及[正式DOI](https://doi.org/10.1145/3770743.3804144)。它把activation与KV纳入共享物理内存管理，通过虚拟Tensor和GPU VMM保持虚拟地址、按阶段借还内存，并可CPU卸载。实现基于vLLM0.5.5，涉及PyTorch allocator与C++层；论文/landing页本次未给出可确认的对应作者仓库，不把同名CPU框架当它的代码。[原文第2/3节](https://arxiv.org/html/2506.15155v2#S2)

**本站推论：**比再省几十次copy更有潜力的是回收“真实不活跃”的activation物理页给KV，跨过容量断点；不改精度/请求/服务args在原则上可行。但现在42层KV是固定连续storage，kernel以单base寻址；只有Memcpy2D可用不代表Corex VMM/地址重映射可用。禁止把torch cached free、profile peak或未知non-Torch内存直接认作安全可借页，更不能删peak记账骗增KV池。

现有215849实际观察的`peak_activation_memory=656424960B`只给profile标量，不证明decode时全部可借。即便全额借到，该数也不足以覆盖32条从16384增长到17408所需的完整额外驻留缺口；是否足以越过第一次释放点仍需真实生命周期证明。不得据此宣称避免抢占或保全部32条。

**最短测试：**先核当前Corex与allocator确切能力/原Tensor引用，若稳定地址和原总显存预算内不能借还就停；不先跑GPU性能。只有可审生命周期方案成立，才一个很小的分配/映射/保值/归还门。当前不批准换allocator、合并0.5.5或另写大VMM系统，列长期大潜力/高阻断项。

### 3. Service-Induced Congestion：两天前更新的同长输入反证，不能把持续系统定理硬套32请求

[最新v3](https://arxiv.org/html/2606.15555v3)，初稿2026-06-14、v3修订2026-10-20，版本日期由[arXiv记录](https://arxiv.org/abs/2606.15555)确认。论文研究服务过程中KV增长导致的同步/eviction循环，讨论按迭代限速准入和请求类别混合；含模型、Vidur与实际GPU实验，不能把Vidur结果当真实设备。论文没有给出本次能确认的v3专属代码仓库；作者主页的[WAIT相关代码](https://github.com/Luoxiaogan/vidur_or)与[模拟器](https://github.com/Luoxiaogan/vllm_simulation)属于相关工作，不冒称v3完整工件。

**本站推论：**实际同长prompt/合法输出预算使同步增长值得警惕，但本站32条有限请求、常见单次preempt，与饱和持续到达/反复级联不是同一制度。准入“每步最多1个”在16K输入/2048 token budget下很可能已由原chunk路径自然满足。改输出长度以制造互质、混入别的请求或按benchmark序号分组均不合法。再做全future reserve会重复115950负例，先不排新限流门。

**最短反证：**从已有原件核多次eviction级联是否实际存在；不存在即不启动这套稳定性策略。真正新证据应是持续重复浪费而非一个counter或瞬时fit，本轮没有增加观察器/运行。

### 4. LMCache：精确KV传输和分层流水可借鉴，本站多数“大倍率”前提不成立

[LMCache v2](https://arxiv.org/html/2510.09665v2)，初稿2025-10-08、修订2025-12-05；[作者开源库](https://github.com/LMCache/LMCache)。其机制包括批量页移动、chunk化存储、分层计算-I/O流水、少复制和连接器生命周期。页scatter先pack再DMA属于该实现的一部分，不等于本站raw normal42的零packing路径。[第5节](https://arxiv.org/html/2510.09665v2#S5)

**本站推论：**可移植的是完成事件/强引用/最小副本与有边界的预取，不是整库或新框架分支。已测这些32请求轮只有一次victim/fullR事务，随机单轮输入没有已证跨请求共享prefix；这不是每Engine总次数限额，原FULL只限单并发host slot，DROP后可复用。远程缓存、多轮重复上下文或PD多GPU的收益预算不能借用。当前SAVE批量提交已在独立验证，不重复以LMCache名义再做同一个微门。对已测一次约0.7GiB阻塞仍须相对约218s总时长界定上限；更多波次可能累计收益，但尚未实测，不能从单层带宽倍数推服务倍数。

**最短测试：**只有现有日志显示实际copy/等待占据值得优化的关键路径，才做一次层完成→该层读者的最短依赖门；无此依据不改42层forward或删除全device围栏。GPU capability/正确性不能由NVIDIA代码自动继承到Corex。

### 5. CONCUR：真正的agent级反馈准入，不适合伪装成本比赛单轮控制

[CONCUR](https://arxiv.org/abs/2601.22705)，2026-01-30；本次读[完整v1](https://arxiv.org/html/2601.22705v1)，作者[主页标注ICML2026](https://tang-t21.github.io/publication/2026-01-30-concur)。其agent级controller用KV占用与cache-hit反馈调节并发，重点保护跨生成/工具步骤的连续性。正文和该作者页本次未找到可确认的对应公开实现，记录“未确认”而非断言不存在。

**本站推论：**不需改采样的controller思想本身可迁移；但本站没有工具等待/agent复入，不能把单轮requests伪装为agent。正文也说明高cache-hit可被传输成本抵消；hit高或preempt少都不是总耗时证明。拿其多GPU大模型吞吐比推16SM小模型没有依据。

**最短反证：**现有输入/请求生命周期已经足以确认没有多轮agent边界，当前不排设备门，不更改客户端并发或请求到达行为。

## 只选择一个可小范围实施的后继候选

按“潜在幅度”和“当前可落地”分开排，避免用未知大系统压过实际小收益：

| 顺位 | 机制 | 潜在幅度/现证 | 当前决定 |
|---|---|---|---|
| 长期潜力最高 | eLLM式activation/KV物理池借还 | 可改变容量断点，但Corex VMM/allocator生命周期未证，可能需大改 | 不实现；先CPU能力/引用反证，禁止虚增可用显存 |
| **唯一近期可实施候选** | 原2048上限内的混合prefill压力子策略 | 小代码可审；是否有服务收益乃至大收益未知，论文不能替本站证明 | 只保具体设计，root若选才实施/最短测试 |
| 后备 | LMCache式层间迁移依赖流水 | 能省阻塞但当前整个迁移次数少，实际服务收益可能很小 | 不重做当前C2D/不立即加门 |
| 不推进 | SIC/CONCUR式准入/请求mixing | 持续到达/agent复入前提不足，易重做旧reserve或改负载 | 保反证，不排设备 |

唯一近期候选的最小形态：不改任何CLI/config/采样参数，不增2048上限，不换整个scheduler；只在原`token_budget`取值后，根据已存在running/waiting的合法prefill/decode状态，在压力混合步采用**不超过原预算一半的临时cap**，其它步保持原预算。半预算仅为单一可否定实现起点，并非论文已给本站标定；不开展cap扫描。始终保原max_model_len、原FCFS容器与pop、encoder/LoRA/spec/streaming未审scope回退、原allocate/None/preempt顺序；不借Future值、不预测长度、不以ID/benchmark行号驱动。缺少可安全解释的async状态则原路回退。

精确待改挂点为已归档actual df780 `Scheduler.schedule` 初始`token_budget = self.max_num_scheduled_tokens`之后；不改`max_num_scheduled_tokens`本身，也不把未用budget当已执行token。此策略与“16tile对齐只省partial CTA”的旧反证不同：它改变混合步服务节奏，但也可能增加chunk/forward数、推迟prefill完成和最后请求开始，原负面机制都保留。**本研究没有根据声称这是已证大收益，或绕过原预算调参要求。**

最短可否定验证顺序：一个实际方法CPU合同覆盖pressure/nonpressure/原守卫及原异常；若静态证明cap从不命中或只是no-op直接停止，不排观察长跑。否则只一次原参数短context-screen必要对照，实际source、DB/KV、启用命中与tokens核齐；以总耗时/吞吐为主、TTFT另列，不能拿平均请求延迟替makespan。有容量/DB失配就记未知，不凑参数、不自动补长pair或大官方。若新的形状/数值/随机行变化出现，已有accuracy不能自动继承；只在准备保留/集成时按实际风险加必要准确率门。

目前只是候选选择，不新增runtime/合同/采集器，也不干扰root在途42层VERIFY1。已经确定的小收益与失败均保留；本研究若后续被root以收益依据不足降级，也应保留这些源码/版本/反证，避免下一API再从宣传倍率重新开始。
