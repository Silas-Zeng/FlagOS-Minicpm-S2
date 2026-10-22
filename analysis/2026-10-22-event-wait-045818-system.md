# 045818：Event完成性通过，typedblocking未观察到等待CPU下降

唯一实际系统验收JSON `analysis/source/event-wait/045818-system-review.json` SHA `b21fb3425bc962672938bc59ecdaa677cb972d1732875e33f2641b95cae78efc`。61项seal及完整文件集合、source2、冻结outer32a075/gate67090/契约41ba、实际Torch/Corex/e155源身份、实际加载libcudartd39d、原命令/环境、只读DB实体和清理后态均核。两个安装cpp缺失保留，不把源收集当语义通过。归档1843997B/SHA30da2ff8c5d0b82fb43e7c8cdba1767a4e5f6d0562d650fa9565fde1af70a148。

A generic `torch.Event()`、B typed默认、C typedblocking，固定非零实际copy stream，每trial八次32MiB pinned D2H。六窗A/B/C/C/B/A各四trial，共24trial、144项完成/query/完整host字节/两端guard/源不变检查全部通过，RNG保持，进入wait前全部early_complete=false。被测synchronize返回后先核完整host与endquery，再独立回读source；没有用后续同步掩盖被测等待失败。

| route窗口 | wait wall均值 ms | wait线程CPU均值 ms |
|---|---:|---:|
| A | 9.429327 | 9.442166 |
| B | 9.428015 | 9.440097 |
| C | 8.688993 | 9.449237 |
| C | 9.428666 | 9.440751 |
| B | 9.427978 | 9.439402 |
| A | 9.430027 | 9.443412 |

三路等待线程CPU均约9.44ms，没有typedblocking降低CPU的信号。三个计时采样区间不同；全部逐trial threadCPU高于wall已原样保存，最大比1.464，首C较低wall不能当收益，原因未定。GPU event约9.415ms、提交单列排除，不将此门外推模型prepare_inputs_event暴露等待或E2E。六窗v1 cpu.stat均未观察到nr_throttled/throttled_time增长，额度6CPU、原56Torch线程保持。

DB前后均523表19474行，物理dc2c、schema0dc7、logicalc05d三SHA相同。04:58:26.010254Z后态68MiB/0%、无GPU进程、9031双栈closed，源码前后不变，controller与worker exit0。首本地审计误套三路KV门的quota_us键，实际Event gate保存raw.quota/period；局部修正说明另存后续审通过，没有设备或测试重跑、没有改原件。

registry116/queue89已收口。按用户最新要求，仅完成已授权native Corex阻塞事件对照门，之后维护GitHub；冻结新研究、自动服务测试和大测试。本门不接入服务，也不因负信号自行重复。
