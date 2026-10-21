# KV191545：复制门通过，单样本计时不能当稳定带宽

2026-10-22，hardware_innovation 独立 CPU 原件审计。范围仅天数 BI-V150；沐曦－曦云 C500 由队友验证。本 owner 没有运行 SSH/GPU，没有改 runtime、gate、launcher 或原始实验文件。本批完成后暂停文件写入，交由 root checkpoint、同步私有实验库与离线归档。

## 已确认的结果

root 串行完成 `experiments/framework/20261021T191545Z-kv-page-copy-gate{,-control}`，19:16:59Z exit0。归档 tgz SHA256 本人重算为 `7b491c525759e3320ecac8cd385d31fd1f434784ade63eef16bb2ab02a554316`，全部8份 source SHA 与manifest/results一致。gate为93eb02c7…、policy为c95f59a5…；归档已使用长模块名，不再含会遮蔽stdlib的 `source/copy.py`。

四个构造case、每case正确性和warm各一次，共八pass的40项byte/guard/未选页/事件消费者检查全部true，四case RNG均不变。每个方向复制 **704643072 bytes（672MiB）**，对应42层、16K token的该BF16 KV构造。actual backend1219与reshape helpera351生成NHD normal和packed42布局，42层消费clone读实际factory视图；normal第0层stride(8192,4096,256,128,1)，packed为(344064,4096,256,128,1)，第41层offset335872个BF16元素。这里只证明这两种源码支持的构造，不是实际服务tensor布局观测。

正常保存、源页毒化、恢复和消费之间的事件顺序在此门中通过；completion_ack仍是false表示submit返回本身不承诺完成。postflight于19:18:05.738516Z为68MiB/0%、两栈9031关闭、8源无漂移。原191017 cases=[]的模块命名失败保留，不能算作复制正确性或带宽结果。

## 原始成本与异常边界

每格都是单次warm观测，ms；没有重复分布、稳定区间或因果layout对照。

| 构造 | 每向copy调用 | save wall/Event | restore wall/Event | roundtrip wall |
|---|---:|---:|---:|---:|
| normal42，连续 | 42 | 25.946121 / 24.756731 | 196.106984 / 26.488735 | 222.053105 |
| normal42，8run | 336 | 27.699296 / 25.073376 | 207.570993 / 194.106018 | 235.270289 |
| packed42，连续 | 1 | 24.943508 / 24.734741 | 95.012686 / 26.496109 | 119.956194 |
| packed42，8run | 8 | 25.027936 / 24.747791 | 95.688994 / 26.758972 | 120.716930 |

normal连续restore的wall减Event为169.618249ms，两种packed分别68.516577ms和68.930022ms。normal8run的restore Event本身升至194.106018ms，不能用“Event都约26ms”概括。D2H与H2D都传同样字节数，不足以从这些单样本判H2D硬件慢、碎片映射必慢，或packed服务必快；也不能把较小Event除字节数写成稳定带宽。

测试额外内存需与服务分开：每构造显式golden+host为1432682496B、device raw为728039424B；全程GPU allocated峰值1456078848B包含测试消费者clone。cgroup memory仅在离散时刻记录，**不是host峰值**；20GiB限制内的这些观测不能用来推生产KV容量或完整offload host需求。

## 源码计时窗口可以确认什么

归档 `source/gate.py:129–202` 的 `pass_once` 中，4个timing Event在窗外预record并同步，排除了它们的首次惰性初始化。timed save先等待ready完成，然后wall从进入transfer上下文之前开始，直到end_save.synchronize返回；Event则是begin_save到end_save。同理，restore的poisoned.synchronize在窗外，wall覆盖stream上下文、wait/record、全部narrow.copy_主机提交、上下文退出和end_restore.synchronize返回。CPU全字节校验、allocation、poison和消费clone未直接计入copy窗。

PyTorch文档定义Event elapsed为两个record之间的时间，synchronize等待事件完成，事件首次record才初始化；它没有承诺该数字等于copy engine的有效DMA忙时。[PyTorch 2.10 Event](https://docs.pytorch.org/docs/2.10/generated/torch.cuda.Event.html)。本机是CoreX兼容实现，文档只作API语义依据，不替代其runtime实测。

据此可以作有限推理：若主机在begin record之前，或end完成之后返回计时器之前被延迟，wall会明显大于Event；若42或336次copy提交中途被延迟，两个record之间的设备时间也可能包含等待下一次主机提交的空隙。因此normal8run的194ms Event也不能单独定位成DMA有效传输成本。当前数据没有这些主机时间点，不能给出各段占比。

## CPU quota 是有依据的候选解释，尚未被本轮证明

save完成后、restore开始前，脚本先对672MiB pinned内容执行全部CPU `torch.equal`，再提交poison并同步。CPU字节校验不在restore wall窗里，仍可能消耗同cgroup的CPU quota；GPU事件同步不重置CPU调度周期。Linux CFS按quota/period分配组CPU时间，耗尽后等待补充，`cpu.stat`提供节流累计信息。[Linux CFS Bandwidth Control](https://docs.kernel.org/scheduler/sched-bwc.html)。CPU intra-op线程可独立配置，但本门没有记录实际线程数，不能假定等于quota或可见CPU数量。[PyTorch 2.10 CPU线程设置](https://docs.pytorch.org/docs/2.10/generated/torch.set_num_threads.html)。

同实例前面的服务持续记录6核quota，root亦指出这一约束；**191545归档本身没有逐窗口cpu.stat、线程数、调度轨迹或CPU时间**，只有memory cgroup观测。因此“CPU检查触发节流并延后restore”是与代码顺序相容的假设，不能断言已经证明，更不能按100ms周期从wall差倒推确切节流次数。host API阻塞、线程池/allocator/驻留效应、CoreX事件/复制实现等尚未分离。正常byte检查通过证明数据和该事件依赖正确，不证明计时没有这些混杂。

## 本批结论与恢复入口

保留四case逐位成功、实际调用数和以上原始成本。可以确认合并连续页复制及事件恢复消费者在构造中可工作；不能报告稳定硬件带宽、生产packed布局收益、实际服务offload节省或模型accuracy。

独立机器可读审计在 `analysis/source/kv-page-copy/191545-cost-review.json`，保留source/manifest/result SHA、全部原始window与wall−Event差值。下一 API 若继续该方向，先读systems的布局/协议未测说明和本报告，实际服务布局与请求生命周期仍是未测入口；本批不实现新runtime、不追加GPU门，也不修改现稳定SQL+C3。root负责后续授权与统一归档。
