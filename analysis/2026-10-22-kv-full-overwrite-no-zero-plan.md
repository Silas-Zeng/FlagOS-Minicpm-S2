# 完整私有页恢复前省去重复清零：独立设计，尚未实现

仅针对本项目天数 BI-V150 16SM/32GiB、6CPU、20GiB host、MiniCPM5-2B BF16、单组normal42。root允许先研究，不修改被冻结的0e2115页序protocol、31cc worker、616事务或当前成对VERIFY0服务。当前唯一设备任务由root管理；本文无SSH、GPU操作或新代码。

## 本轮只保留这一条新框架方向

已重新读旧growth/full-output reserve115950负结果及terminal181041反证，不重复保守准入或终态排空；systems另研究454次defer的便宜必要条件，本方案不与其混合。这里消除的是事务层实际无消费者观察的中间数据写入，不换算子、不启现成backend、不合新分支，也不改变容量、token数、请求FCFS或原服务参数。

204159已真实确认一次685.125MiB完整前缀恢复。私有页排序使ZERO/RESTORE/诊断回读各2772次，字节/consumer检查通过；专项JSON为 [204159原件审计](source/kv-transaction/204159-private-order-hardware-review.json)。当前ZERO把42层R完整页全部写0，随即同一组页被H2D从已完成的pinned snapshot逐字节覆盖，期间未发布/未执行消费者。若覆盖范围证明成立，ZERO写出的值不会被读取，是具体可删工作。

**可避免工作上界只可写为**：本例718405632B GPU写入、2772次zero_提交、一个ZERO RPC及其事件阶段；RESTORE前仍需自己的producer围栏，不能把它也算删除。ZERO没有阶段时间，成本可能小，不能承诺“大收益”或按调用比例报TPS。方向的收益潜力高于再节省几个Python字段，是否值得集成仍以匹配服务为准。

## 原生FullAttention和文档能证明什么

actual `vllm/v1/kv_cache_interface.py` SHA `7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003`：`needs_kv_cache_zeroing`只返回has_mamba_layers，本模型False。actual df780 schedule1046–1049因此不drain/new_block_ids_to_zero，e1551215分支存在但本模型不执行。这说明本模型原生没有“所有FullAttention页都必须先写0”的无条件要求，**不等于任意部分恢复都可省零**。当前ZERO是本项目初版恢复协议新增的保守步骤。

[PyTorch2.10 copy_](https://docs.pytorch.org/docs/2.10/generated/torch.Tensor.copy_.html)定义把源元素写入目标，且CPU/GPU non_blocking可能异步；[empty](https://docs.pytorch.org/docs/2.10/generated/torch.empty.html)不保证分配数据已初始化，不能把malloc/旧数据本来为零当理由。本方案依赖显式完整覆盖，不依赖初值。官方[device synchronize](https://docs.pytorch.org/docs/2.10/generated/torch.cuda.synchronize.html)与[Event](https://docs.pytorch.org/docs/2.10/generated/torch.cuda.Event.html)区分设备全部流完成和具体事件完成；它们仅作API设计语义参考，CoreX实际支持仍以本项目191545/202526/204159已完成事件和字节门为证，不能从NVIDIA文档推BI-V150硬件引擎能力。

## 完整覆盖证明必须逐项成立

actual worker31cc `_context`已锁42个独立normal BF16 storage、shape `(pool,2,16,2,128)`、stride `(8192,4096,256,128,1)`、offset0，raw view为 `(pool,16384)` uint8。逻辑整页覆盖全部16token、K/V、两个KV head与128维，无额外未写padding；其它layout/量化/Mamba/shared/跨层alias全部原路。

当前 `plan_snapshot` 先从真实issued扣所有queued scheduled、限制known−1，R向下取16整页；SAVE在原writer完成后复制这R页，真实D2H done ACK后保持host源不变。恢复分配的是R/16页新private、ref1、unhashed、非null、唯一块；未发布、无pending旧frame、同epoch/token digest。

c95f `PagePlan`校验唯一逻辑source/destination映射及范围；RESTORE host是 `(R/16,16384)`，目的raw每段 `.narrow(0,d,count).copy_(host.narrow(0,s,count))`，双方shape完全相同、uint8、连续，没有broadcast/类型转换或按数值掩码跳写。plan的所有段总页数等R/16，故每个目的字节有且仅有一次对应源写。完整copy后的BF16位模式不依赖此前是否零；consumer只在真实H2D ACK/可选回读后看到新页。

必须排除R非16对齐、部分head/维度写入、partial-byte copy、目标页内有要保留的旧内容、Mamba状态/未知feature、共享/alias、页集合或storage签名变化。R之外的后继partial tail是原scheduler新算token和actual writer的责任，不属于此次恢复省零范围，不能将其混进“已完整覆盖”的证明或宣称整个pool无需初始化。

## actual writer依赖不能删

actual1219 `do_kv_cache_update`与writer `triton_reshape_and_cache_flash.py`（f18224e5…）按slot_mapping写新token，negative slot提前返回。它只写调度的有效slot，不能拿“后继writer总会覆盖”证明旧prefix全部有效；真正覆盖旧prefix的是本次raw H2D。

SAVE前整个device fence覆盖原preempt将释放的全部旧writer，仍保留。RESTORE自己的现有 `torch.cuda.synchronize()` 也必须保留：新分配页可能来自其它刚释放请求，不能因为取消ZERO就丢掉旧writer→新H2D的依赖。H2D完成event record/synchronize、VERIFY1的42层逐字节回读和原runner更新/Attention消费先后仍保持。不能用CPU phase变更、future.done或metadata guard代替其中任一完成围栏。

## 状态机的最小语义差异：无伪ZERO_ACK

当前路径为：

```text
HOST_RESIDENT → 私有ALLOCATED → ZERO_PENDING → 真ZERO_DONE
              → RESTORE_PENDING → 真RESTORE_DONE → 原schedule有work → PUBLISHED
```

若以后root授权实现，建议独立定义明确的“完整页覆盖恢复”操作/模式，例如 `RESTORE_FULL`，而不是构造没有发生的ZERO Receipt：

```text
HOST_RESIDENT → 私有ALLOCATED且完整覆盖证明成立
              → RESTORE_FULL_PENDING → 真RESTORE_DONE → 原schedule有work → PUBLISHED
```

需要同时审的实际接口：

- transaction：只能由ALLOCATED、无inflight/cancel、同页/bytes/epoch的完整覆盖证明提交新操作，唯一真实ACK后到RESTORE_DONE；原ZERO路径保留供不匹配条件回退，不允许直接把phase改成ZERO_DONE。
- protocol：在原private分配/可选已审排序/bind之后选择这个模式，R、预算、页集合、digest/old frame处理和payload不改；完整command/ACK记录明确zero_stage_executed=False，不打印ZERO_ACK或伪转移字节。
- worker：slot仍SAVED时接受同owner/key/storage/serial、完整R与真实页集合的新恢复操作，把目的映射先绑定在slot强引用/状态里，再保留原producer fence→完整H2D→done event→可选42层回读→ACK。旧设计通过ZERO存下destination_pages，这个绑定职责必须显式搬到新操作入口，不能顺手丢掉同映射校验。

这会涉及事务/worker/adapter协同，故当前只有设计，不能在冻结31cc旁删一行zero_便称已实现。若新操作任何完整性条件不满足，在提交前走原ZERO路径；提交后的失败不能静默重试旧路径或复用半写页。

## 失败与取消仍保持私有回滚

完整覆盖是成功后的属性，不是“开始提交就当已恢复”。例如42层只复制了20层即异常，目标仍混有旧数据；不能发布R、hash这些块或交Attention读。若真实device settle成功，可按当前FAILED/未发布逻辑原free全部私有目的页、清绑定、回到computed0重算；不能把部分拷贝的bytes ACK成完整成功。若不能证明settled，保留raw/host/event/map强引用和slot，不free/不DROP/不publish，失败退出。

取消、旧epoch、目的页/源storage签名变化、host snapshot不再持有均拒绝成功；提交后取消也等真实完成。发布以后回归原scheduler所有权，仍不可用私有rollback接口释放。需要验证而非承诺全局RNG分配不变；补丁无新采样调用不自动保证batch轨迹相同，最终accuracy独立测。

## 最短后继与可否定条件

先完成正在进行的页序VERIFY0匹配pair及阶段归档，不插队或叠候选。以后若root批准实现，只写上述独立显式模式及一项必要CPU状态合同（完整覆盖准入、不伪ACK、partial拒绝、异epoch、失败未settle保留/settled回滚），不重复复制四几何suite。

最短设备门仍用同真实长输出/原参数、VERIFY1：证明新mode真的执行且没有ZERO RPC/zero_calls，R页全42层bytes相等、6runner检查及后继原输出消费/清理通过。旧191545已有带poison的全页复制反例覆盖基础copy完整性；必要新poison只作诊断、不可计为性能，不能在正式路径重新填一遍而抵消省零。之后独立与仍执行ZERO的冻结页序版比较，DB/容量/CPU/原参数一致、VERIFY0、原件分目录；没有阶段或匹配服务信号就保留负结果，不能用本例685.125MiB×理论带宽伪造收益。

当前没有新实现/合同执行/设备结果。所有硬件事实仅本实例；20GiB host预算和原1GiB slot/guard均保持，不把该方向包装成扩大容量或已减少重算。

framework已全文只读复核本设计，无完整覆盖/生命周期设计阻断；特别确认显式新操作、迁移目的绑定、保RESTORE自己的device fence、强引用/失败回滚均不能漏。该审阅不授权实现、不证明设备正确；如后续实现，仍逐项审全R×42 uint8 plan、host immutable/strongref、绑定后异pages/签名和cancel/epoch，R外suffix不冒称已恢复。当前先完成页序pair与归档，仍无代码。
