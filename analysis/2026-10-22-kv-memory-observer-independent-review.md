# 启动显存纯观察器独立审阅（天数BI-V150）

framework_innovation，CPU-only只读；没有修改hardware实现、执行合同/框架/远端或GPU。目标是解释两source启动KV容量差异的真实分项，**不是再跑几轮性能直到碰到相同容量**，也不从96token差反推某个profiling字段。

## 最终身份与历史hold

最终 `patches/framework/biv150_kv_memory_observer.py` SHA **6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c**；唯一合同 `tests/test_biv150_kv_memory_observer.py` SHA **0becd99b5de8c98926538a9e174ebe68b31476c3079a5c4703eea40f8dcd33d5**。作者报告1test/0.002s通过，本owner全文只读实现/合同并实际核SHA，没有重复运行。

旧b092首稿从general install直接import WorkerFL/io，作者主动hold：可能提前加载设备相关模块，不能承诺纯观察。最终6a去掉importlib/所有framework主动导入，改延迟父入口；b092不能部署或引用为最终通过。init只接受完整e043 stable或791c协议既有footer，再最后append同observer footer；不插在原protocol前，不改a8de/e155源码。相同791c本身不证明是哪份协议资产，未来builder仍须各自完整source清单/pins，不接受任意同init的混合source。

## 实际调用与原语义

install默认False不动作；显式启用也只从sys.modules取自然已加载abstract4190，核原Executor.determine_available_memory源/方法身份，武装一次父入口。actual abstract:146只发原字符串collective_rpc；UniProc4625没有override，ExternalLauncher子类才有额外行为，最终exactUniProc检查将其排除。

原父调用时才从已自然加载module/实际driverwrapper取WorkerFL实例，校验UniProc4625、Wrapper7da、a8de worker、6d8 io及原managed wrapper/__wrapped__链和profiling generator。全部通过才接两hook，再原父RPC**恰一次**；未知/缺模块NOT_ACTIVATED仍执行原父一次，不使内存计算no-op或报错。原list对象/原异常直接返回，finally按identity恢复worker方法、profiling CM及父方法；不覆盖别人在此期间替换的函数。

`_wrap_profile`保留完整原with包yield，因此原__enter__/__exit__和异常抑制语义由原CM决定；实际a8de CM没有finally，body异常不做after measure也保持。observer只以ContextVar强持原本产生的profile_result，在原determine返回/抛异常后读其已有CPU标量；ContextVar在finally reset。观察输出/元数据读取错误不应替代原返回/异常。

没有新增MemorySnapshot、CUDA/stats/sync/allocator/采样API、GPU tensor分配或值读取；caller链只留有限代码位置，logger只读现态，不执行filters或isEnabledFor、不改级别。原peak若由before_peak+increase重构，graph deduction若由requested−nonKV−available重构，都明确放 `derived_only_not_new_samples`，不能假称新硬件采样。仅记录本来已发生的原profiling结果。

## 验证边界与后继验收

合同用CPU metadata/CM/父调用stub验证return、CM抑制、同Exception对象、未自然加载四场景，原list identity、原方法调用各一次、三hook恢复、ContextVar reset；**不运行actual WorkerFL或GPU**。静态source/调用链审阅未发现进入最短独立观察门的阻断，已回root/作者，可冻结模块；这不等于新builder/部署也已过。

后继同一observer必须分别装到两份已固定source，只增加该文件/init最后footer；用root最短smoke原driver收真实ARMED→DETERMINE_RETURN/PARENT_RETURN（或原异常/未激活）记录。**ARMED≠观察完成**；若缺profile/字段则unobserved，不从其它run补齐，不归因容量。PARENT记录需原返回/三hook恢复，已有分项和KV最终结果再由root对照；不得为了补缺值再调用GPU统计或重新profile。当前本owner尚无该observer实际原件，也没有收益/原因结论。
