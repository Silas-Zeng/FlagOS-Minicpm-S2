# 实际V2调度路径的输出增长预算审计与修订

2026-10-21。仅CPU源码、原始描述符和必要合同。旧9245runtime、105930冻结源、启动参数和V2环境均未改。

## 真实失败原因已经定位

112603隔离smoke exit0，实际EngineCore156959输出的29项guard中只有 `not scheduler.use_v2_model_runner` 为false；其余28项true、setup_errors为空。actual use_v2=True，scheduler为内置AsyncScheduler；单组Unitary/KVCacheManager/FullAttentionSpec、42层、16block、BF16/head128、FCFS/reserveFullISL等均exact。它准确解释110747只有INSTALLED而没有FIRST_CHECKED，不能把220.369s视作策略已启用的性能。

## 为什么可以审计后支持，不能只删flag限制

依据实际文件 `analysis/source/growth-admission/scheduler.py`（df780761…）与 `async_scheduler.py`（da6343d7…）：

1. **分配与准入不分V1/V2。** running/waiting循环、完整输入准入、allocate_slots、None后原FCFS break和coordinator实际页预测器均在V2分支之前。后面的V2分支只是把resumed合入new payload、携带all_token_ids，以及cached-request序列化差异；候选不碰这些对象。
2. **placeholder含义保持。** 原base `_update_after_schedule`先增加computed并判断prefill；实际Async随后对非prefill加1个输出placeholder，无spec时draft列表为空。V2额外更新next_decode_eligible_step=current_step+pp_size；本scope PP1，因此下一调度步即到eligible，没有跨PP多步cadence。原future终点 `max(prompt+合法max_tokens,current+placeholders,computed)` 再裁max_model_len，仍保守覆盖已调度范围，不依赖V1输出payload或把placeholder当已完成输出。
3. **不接管释放协议。** 实际constructor将defer_block_free初始化false，仅有KV connector消费者且多batch时才开启；本scope无connector。新revision另外显式要求defer_block_free is False，避免将暂未回free队列的页误作已释放。完成、取消、抢占仍走原free；live running/free每次重读，无持久reservation ledger。带延迟释放或connector的路径不支持、不猜预算。
4. **精确类型与来源。** 只支持已审内置Scheduler和AsyncScheduler两个exact类型，拒未知subclass；不额外import/支持FL的MTP调度器。V2 flag必须是真bool，允许True或False。新增actual Async整源SHA、它对base的继承/未覆盖schedule、三个原method身份守卫，其余模型、precision、并行、prefix、feature限制保留。

因此这次是根据实际分配/状态语义支持一个已审调度分支，不是切换环境把V2关掉，也不是不加边界地接受任意V2配置。

## 独立新文件与组装

| 文件 | SHA256 |
|---|---|
| patches/framework/biv150_growth_admission_v2.py | 72d6f3822c96be028f6ab3cd818de1da6bafdb38d52a50a12633851717332803 |
| patches/framework/biv150_growth_admission_v2_source.py | e5bad3d863a36d0d24bc3650c513600e23909d2224fb315bb8eb99943f8b0d9a |
| tests/test_biv150_growth_admission_v2.py | 2ceeb15965b43ccb60228b07882776b7c31405ef7e68fedc2711b5a70cf0d2a9 |

默认关闭，显式install(enabled=True)。新source变换器仅接原080656 init SHAe043b789…，不接旧growth或诊断init；结果init SHA **830ff5805cb4d989cbc9225ef423720a6e261754ba180d2ca495e76434d7e421**。保持三个旧SQL/C2/C3模块和runner不变，在独立source新增v2模块与general hook，不与旧v1包装叠加；未知原函数身份会拒绝安装。

旧 `biv150_growth_admission.py` SHA9245dd08…已复算不变。新module相对它只改scope/type/来源与版本标识，future_tokens、growth_demand、allocate原调用、FCFS回退和所有数学均原样。

## 唯一必要CPU合同与设备边界

```text
python -m unittest tests/test_biv150_growth_admission_v2.py -v
1 test OK，0.016s
```

合同直接抽取actual base+Async的原 `_update_after_schedule` 两步执行，确认computed/placeholder增长、无spec空列表、PP1下一步cadence、future96token预算及真实predictor剩余页；同时核6源SHA、default off、未知subclass和deferTrue回退。源变换后语法与两个新模块py_compile通过。framework owner已独立终审72d6/e5ba：无阻断最短服务项，仅独立复跑此1合同0.017s通过，没有重跑旧7项或增加suite。没有设备操作。

后继最短服务必须从**真实EngineCore**看到 `FIRST_CHECKED` 与 `FIRST_DEFERRED`，不能再只看INSTALLED。启动前marker可要求INSTALLED，CHECKED/DEFERRED应在并发负载后验收，不能将负载尚未开始时没有CHECKED当启动失败。DB、KV、driver/seed/请求计数必须对齐，保守未来预算降低并发、TTFT恶化或总耗时无收益都要如实保留。CPU交付时尚无设备结论，后续真实screen见下节；仍无新accuracy或官方收益结论，不继承旧C3准确率。

113208 bucket首轮已使DB由501表18789行扩为506表18926行；后继growth必须保存并核对这个**新basis**，不能与旧501表基点直接归因。只登记root串行队列，不默认当前设备已空闲。

## 115247真实激活，首轮DB扩展，不判最终性能

完整原件已本地独立核22源SHA、bc51/shape/seed、32完成0失败及524288/32768tokens。EngineCore162561 FIRST_CHECKED free31595/future1151，随后FIRST_DEFERRED free2702/future2722，策略真实检查并延后准入，解决旧版未启用问题。238.11336583085358s/2339.4570819502455total tok/s，meanTTFT68405.78491348424ms；KV521936，preempt0→0，对照114713为220.249703s/KV521840/preempt0→1。

但本轮DB506表18926行→512表19130行，新增6表204行，三hash变化，不能仅将较长耗时定为策略回退；只补一次必要warm115950，结果现已独立审完，见下节。11:59:21.132870Z cold fullpost68/0/closed已核，详见115247的independent-screen-review.json。没有新诊断、调参或追加CPU合同；候选默认off保留。

## 唯一必要warm完成：无正吞吐信号，停止集成验证

115950完整原件独立核22源SHA、真实EngineCore164138 CHECKED+DEFERRED2696free/2722future、32/0及同tokens。**221.23383624106646s/2517.95118443368total**，meanTTFT67130.2737761871ms，KV521840/preempt0→0。DB before/after512表19130行三hash完全相同且等于115247after，12:18:37.889080Z fullpost68/0closed。

对114713的描述差：吞吐−0.4448385%、meanTTFT+7.5110987%，KV现同521840；但DB506→512仍不同，不将此作为精确因果回退估计。没有正吞吐信号而首token延迟更高，按root决策**不服务集成、不扩大accuracy/official，不再补轮次**；保留默认off源码及所有negative，供未来不同负载研究。调度减少重计算不自动等于端到端性能改善。
