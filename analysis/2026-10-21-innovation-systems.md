# 系统创新候选：避免容量压力下的昂贵重计算

2026-10-21，systems_innovation。仅本地 CPU、已下载原始证据和公开一手资料；没有 SSH/GPU、运行器/候选修改或新设备实验。当前唯一 GPU 的正式两档实验由 root 拥有。本文是待验证设计，不能记作已实现、已通过正确性或性能收益。

## 现在已知什么

SQL 修复、C2 launch 与 C3 mixed 的现有成果继续保留；同源 C3 已以 103/105 独立通过准确率。最新 warm 16K/1024/32-request 的 C2 231.322s 与 C3 220.368s 在已知 DB/KV 初态相同，约4.97%仍是单次短测信号。正式4K四轮已完整且独立复算：丢原首轮后3683.65 total tok/s、355.88s；16K尚运行，不能预告总体增益。

下一系统问题应从**剩余实测成本**出发。warm C2 的一次 [metrics观测](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/metrics-observed.prom>)确实显示 preemptions_total=1，但它是一个时点的服务累计值，不是最终负载内次数。当前没有证据说明 C3 无抢占，更没有精确的重复计算 token/耗时。因此以下两项按验证成本排序，不能直接认定“大收益”。

## 规则与已有能力的边界

项目于2026-10-20保存的 [官方页面核实](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/docs/official-verification.md>)允许 KV/内存管理、动态 batching 和实际框架实现；禁止改官方 benchmark/启动参数、直接开现成量化或投机、仅路由现成替代算子、合并新框架分支。本次打开 [比赛页](https://flagos.io/race-detail-season2?id=539vlt2p&lang=cn) 返回不可达，未重新取得 live 页面，规则依据明确限于本地已核实记录与 AGENTS。不存在新规则或额外批准流程。

固定 [vLLM v0.24 scheduler配置](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/config/scheduler.py#L124-L134) 已有默认 `scheduler_reserve_full_isl=True` 和 `watermark`；前者检查完整**当前输入序列**，后者是全局水位。不能把启用这些现成功能写成创新。公开固定版 [KVCacheManager](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/core/kv_cache_manager.py#L339) 的 full-sequence 检查使用 `request.num_tokens`；它不等于按每个请求剩余生成上限预留未来 KV。这是下面第1项的差异。

实际归档 [插件scheduler](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/source/plugin/vllm_fl/worker/scheduler_fl.py>)只对子类加MTP结构化输出逻辑，普通调度委托上游 AsyncScheduler。本文查阅的公开 v0.24 源只能用于机制审计，**尚未取得本机安装 scheduler/KV manager 的单独 hash 快照**；实施前由 owner 做一次精确源码核对，不能把公开同版视作运行文件已逐字一致。

## 候选1：按真实请求的输出增长做有界准入预算

**目标：** 避免刚完成昂贵长 prompt 的请求，因为另外请求持续生成而被反复逐出/重算。现状不是“缺少任何准入检查”，缺的是未来增长与重计算成本之间的权衡。

按 scheduler 已拥有的实际 prompt/computed/output 长度、每请求 API `max_tokens`、真实 block size、prefix hit、空闲块与在途 placeholder 建立只读 admission ledger。新请求保留原 FCFS 次序，只在即将跨容量边界时延缓队首的首次准入；不改变已选请求 token ID/采样参数，不提前结束请求，不读取 benchmark 路径或4K/16K标签。预算必须以去重后的物理 page/refcount 为准，不能简单相加逻辑长度多算共享 prefix。

第一个可执行版本应只有一个通用分支：当所有拟保护 running 请求的**合法剩余生成上限确实可容纳**，而再准入一个完整 prompt 会使这些上限无法容纳时，将该次准入延迟到释放足够块；如某单请求未来上限本身超过可容容量，立即回原策略，不能因保守预留而永久不准入。该设计是自行实现请求级 ledger 和生命周期维护，不改现成 watermark/启动参数。之后若要用较短动态 horizon，必须根据真实服务状态推导并单独验证，首版不写任意“1024”或“并发30”。

**容量反证先摆明：** 42层、2KV heads、head128、BF16 的KV为42KiB/token。当前521840tokens只能同时容纳29条完整17408tokens（30条还差400tokens）；31条16384prompt尚能容纳，但平均再生成约449tokens就触边。这只是无prefix/忽略碎片的账本，不是实际调度轨迹。把31活跃减到29可能降低decode批量、增加TTFT，完全可能抵消避免重计算的收益。官方4K较少容量压力，策略应自然基本不触发；准确率32768上限也不应导致只因保守账本而大量闲卡。

**源码落点：** plugin `AsyncSchedulerFL` 对 waiting准入增加ledger检查；保留原allocate/free与running优先顺序，针对finished/abort/preempt/resume更新账本。公开 [scheduler](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/core/sched/scheduler.py#L482-L525) 在分配失败时逐出请求，`_preempt_request`会释放块并将computed重置；新策略必须兼容现有async placeholder和已在途batch，不从调度线程直接修改worker表。

**最短验证：** 当前正式任务结束后，先使用它已有的最终metrics/日志计算抢占的可能上界；没有明显容量重算证据则不实现。若值得做，核对实际scheduler源并写少数必要ledger边界检查，再直接同seed的32请求16K/1024单档对照，记录完成数/tokens、相同KV/DB、TTFT、preempt/recompute计数和总耗时。先看总耗时是否下降且TTFT无明显恶化，再支付准确率或完整官方成本；不为证明这条建重型模拟器。

**停止条件：** 官方16K无显著抢占/重复token，或者更少驻留使walltime/TTFT变差。一次metrics=1不足以单独推动大改。Sarathi-Serve提供的 [chunked-prefill与stall-free调度机制](https://arxiv.org/abs/2403.02310)说明批次组成须同时考虑延迟与吞吐；本系统已具备chunked prefill，本文不重复发明它，也不迁移论文加速倍数。

## 候选2：少量被逐出请求的精确 KV 暂存，替代重复 prefill

这是更大改造的后备，仅当原官方16K证实同一长prompt的重计算成本明显、候选1的并发损失又抵消收益时进入。内存不足时仍执行原准入/抢占决定，但将**被逐出请求已经算好的、可安全读取的KV页**放入有界pinned host槽；恢复时重新分配原 GPU pool内页并恢复精确字节，随后仅计算真正缺少部分。它不提升GPU KV池容量，不更改精度、不剪token、不改变prefix语义；目标是减少浪费的FLOPs。

设计要保留原GPU大tensor地址/stride与graph绑定，只复制payload和映射；暂存索引使用request生命周期ID和epoch，不能用会复用的物理行号。原42层BF16 cache按实际backend layout枚举真实页，不能假定packed storage或共享层均独立。D2H开始前必须等待所有可能写旧page的已在途步；D2H结束前不能让页被新请求覆盖。H2D恢复须先完成再把请求标为可执行，cancel/abort释放host槽且不复活旧epoch。这些是正确性要求，不能用“non_blocking=True”替代依赖关系。

**为什么可能值得：** 一条16384输入约672MiB，连1024输出约714MiB。只有当双向拷贝和排队成本小于被替代的长prompt重算时才有意义。量级公式为 `T_transfer ≈ 2×KV_bytes / effective_link_BW + per-page_launch + fences`；例如假设实测有效20GiB/s，672MiB往返的理想下界约65.6ms，**20GiB/s是条件示例，尚非本机PCIe测量**。若每层/每页逐个copy把launch和同步放大，或host pinned占用触发CPU/内存压力，实际可能差很多。不要据公开总板互连规格推当前单device的PCIe有效带宽。

现有 [runner KV分配/reshape路径](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/remote-source/model_runner.py:7111>)和 [preemption处理入口](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/remote-source/model_runner.py:4159>)提供源码切口，但单加runner copy无scheduler握手是不完整实现。插件保持单设备与async scheduling，不改变官方启动选项，不装现成connector假称自己的工作。

[InferCept](https://arxiv.org/abs/2402.01869)研究暂停状态的保留/交换/重算权衡，[FastSwitch](https://arxiv.org/abs/2411.18424)研究上下文切换的KV传输成本，可作为设计依据；两者工作负载/调度目标和本比赛不同，本文不采用其公开倍数。当前 [vLLM Ascend preempt offload说明](https://docs.vllm.ai/projects/ascend/en/main/user_guide/feature_guide/preempt_offload_connector.html#notes-and-limitations)明确只支持其专门P/D decode场景，不能用于本单卡mixed部署；其basic copy、host预算不足fallback、async限制可作为反例，**不是可切换的BI-V150现成路径**。

**最短验证：** 先确认当前原日志真的重复prefill严重；随后只做一次真实KV页D2H/H2D roundtrip+bytes校验、包含分散page和生产/消费流依赖，用所测带宽与一次重算时间比较。若负面立即停止，不先实现完整offload服务。最小gate若明显正面，再实现仅1个待恢复请求槽的协议，真实服务32req/16K/1024短测记录同步开销、暂存命中和实际避免重算token；改变了async状态机，必须独立准确率，不能继承C3通过。

## 本轮决策

第1项比第2项更适合先试，但两项都等待现有正式16K证据，不为“多创新”盲目实现。本轮实际新增的是机制研究和4K局部证据审计；M分桶已有其他owner负责，不重复；共享graph pool/内存释放、线程扫描、sampler compile、扩大batch cap既有反证不重开。若正式16K表明容量重算很少，则这两项降级，优先真实有信号的M分桶/GEMM或既有局部候选。

完整接续和中间决定保存在 [子智能体交接](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/docs/agent-work/systems_innovation.md>)；raw owned by root，记录更新仅使用原始证据，不改官方CSV、分数或运行任务。
