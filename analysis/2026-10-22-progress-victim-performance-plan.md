# 天数BI-V150：进展victim候选的最短性能对照建议

当前唯一机制门为root启动的 `20261022T015315Z-kv-progress-victim-context16k-long`，runner250079，72942/bbb49/1f8及417源已由root核。**本文写作时完整机制结果未到，未批准或启动性能pair**；只给下一动作条件，不新增runtime/包装/测试。

## 先满足真实机制条件

必须由完整原件证明一次DECISION selected=True且不同原tail，严格后方/未scheduled/保护关系成立；同一selected request/epoch真正SAVE→RESTORE_FULL→DROP，动态R与全42层字节回读通过、runner六检查、原consumer在原update之后消费，32/0/完整源/DB/后态通过。DECISION自身selectedcounter0、后续RPC/consumer1是固定实现顺序，不误判。无选中/只安装/选中后仅普通重算或没有恢复证据，不算该受测机制通过，先保负结果或未验证，不能直接用其耗时建立收益。

已复读原FULL `_wrap_preempt`、`_commit_resume`、`_wrap_runner_states`和`_wrap_update`：安全R在SAVE时扣实际旧queued跨度，恢复后只有形成真正调度输出才发布，原consumer报告的是该恢复输出本次实际scheduled token数。**新victim改变R、已确认输出和恢复后suffix长度，consumer不应硬要求等于旧8/16或与基线相同**；只核同对象/正确阶段/正数实际消费。保cached-state/generator身份不保证全局随机输出相同。

## 唯一比较对象与共同观察

机制通过后，只比较冻结原FULL1aff（原tail选择）与72942（一次受限选择），双方worker5d9a/txn84be/c95f/e155完全相同，原bc51 context-long/seed721201/SERVER不变，VERIFY0。不是和无协议stable比较，也不拿当前VERIFY1回读诊断耗时作性能baseline。

双方使用同6a启动内存观察器最后footer，完整init均39fb，同一套原内存profile1/原返回/三hook恢复门。建议新独立builder均从固定214400完整FULL416起点构造：full保1aff、progress只换72942，双方同添6a与独立pair manifest，得到各完整418树（init修改不增加文件数）。这样能复用原输入映射和固定观察器，避免将旧progress manifest误当新当前身份。它是包装建议，**当前未写builder或生成树**。不得改已受测bbb49/1f8/原innovation或用临时插件覆盖在途源。

6a只观察启动阶段已有标量，双方加载前观测一致；仍承认额外Python/日志扰动。candidate的一次页元数据遍历和DECISION日志是实际策略开销，应留在其测量中；不为基线增加假decision，不提前运行selector或关日志伪造净收益。既有FULL稀疏RPC/consumer日志双方保留，不新增逐步observer/profiler或Future计时。

## 最短顺序与停止条件

按设备唯一owner串行一次FULL baseline，正常结束封存再一次progress candidate。用新起点实际DB快照；要求baseline before=after=candidate before三SHA一致才启动后者，结束后candidate after也核。双方物理显存/CPU配额/并发host工作、实际启动KV容量、6a全部非时间分项和原服务参数逐项相同。不能改util、预留dummy、显式KV大小或恢复DB凑配对。

容量或启动分项失配、DB变化则保原件并标不可归因，不直接再刷5分钟追配对。方案只请求首个必要A/B；小正信号保留，是否追加一次复核由root在看到首对后决定，不提前安排多轮。

后验把两个层次分开：

- **环境比较门**须匹配DB/KV/启动分项/参数/源约定差异，才能描述整体策略的duration、total TPS、TTFT差。accuracy/官方总分不在此门内。
- **策略实际行为**必须动态保选中对象/原tail/进展/原preempt累计、R/页数/源目的run数/copy字节、fast/restore skips、原consumer token数和host释放。这些可以因策略不同而改变，不能硬要求与基线相同或为匹配而禁用选择。正差只属于含选择遍历、传输差异及调度变化的累计策略，不称纯pop/减少重算/更早释放的独立收益。

原日志没有每个请求最终完成时间与完整WAITING分布；不新增计时器也能否定“整体更快”的假设，但不能由更短R/更少skip或被恢复对象更早完成推导整批makespan因果。完整32请求正常完成与消费链必要；真实选中未发生的candidate即使较快，也只能记录未命中及代码开销样本。若有正信号且准备纳入默认，再做必要准确率与官方复现；旧103/105不继承。
