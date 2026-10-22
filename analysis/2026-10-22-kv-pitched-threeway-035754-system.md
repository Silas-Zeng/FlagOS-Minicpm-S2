# 035754三路SAVE：系统原件验收通过

本agent独占本系统报告，hardware另写计时专项，不共用报告路径。本轮 `20261022T035754Z-kv-pitched-threeway-gate` 已exit0，本agent唯一进行本地stdlib原件验收，未执行候选、桥、设备或任何旧测试。结果 `analysis/source/kv-pitched-copy/035754-system-review.json` SHA `9d0bcd7beff67ed8ddaba8f18feedbef5ad8bcf2026115f66dd582ea297615d6`。

root归档1862094B、SHA `fa80a90332005eda7cc77862c82c85876a27ee9e10692456409b7abf909b4bbd`。本agent独立核86项seal及完整文件集合、7项source前后和设备结果中的source身份；outer `b2c65963…`、gate `9b16aec6…`、runtime818e/桥0a4d/c95f均吻合。实际g++编译exit0、stderr空，so15936B/SHA `9e33ecbf…` 与前门相同；ABI头指纹、ldd/rpath/readelf及进程实际加载Corex libcudart `d39d5796…` 均核。controller260580、唯一worker260602，没有模型或服务。

BI-V150为16SM/32GiB，非零Torch stream handle `94323367614720`，同流event完成后再验证CPU数据，实际maxpitch2147483647B。两case均完整保留真实SAVE原逻辑页序及全部KV字节，source、三个host视图均含16KiB storage offset。

| 真实页序 | R / 页数 / 单层字节 | A原c95f | B同桥C-linear | C同桥2D |
|---|---|---:|---:|---:|
| 015315 | 16928 / 1058 / 17334272 | 37 | 37线性 | 11（2线性+9二维） |
| 021658 | 16768 / 1048 / 17170432 | 26 | 26线性 | 6（2线性+4二维） |

B通过提交前受控 `max_pitch=PAGE` 展开，`fallback_pitched_segments=9/4`，是对照模式而非实际设备pitch不足；C按真实maxpitch，fallback0。两case共30项完整字节、CPU oracle、计数、所有host及source guard、输入不变检查均true，计时后7项均true，CPU/GPU RNG保持。独立CPU按页号和页内word号重算payload SHA，也与实际输出一致。

两组完整正确性之后，仅首case做一次64call镜像窗口：

| 窗口 | wall ms/call | event ms/call | nr_throttled / throttled_time 增量 |
|---|---:|---:|---:|
| A | 0.682748388 | 0.679097235 | 0 / 0 |
| B | 0.655123797 | 0.652384877 | 0 / 0 |
| C | 0.631449424 | 0.628297448 | 0 / 0 |
| C | 0.631230563 | 0.628322840 | 0 / 0 |
| B | 0.654983385 | 0.652412593 | 0 / 0 |
| A | 0.689953056 | 0.653520525 | 0 / 0 |

每窗口v1 cpu.stat原值、增量、quota/period与进程CPU时间均已保留并核算；CPU quota6、56Torch线程未更改。六窗只证明本门未观察到这两项节流计数增长，不能追溯032653 wall波动的原因、证明无其他host影响或把累积线程ns当wall。计时准备、分配、descriptor、producer和字节比较在窗口外；这是一次单层三路局部成本信号，尚无42层服务、稳定E2E或accuracy结论，不自动重复本门。

DB前后均523表19474行，实体复算物理 `dc2c7646…`、schema `0dc7a465…`、logical `c05d7e31…` 三SHA同。03:58:09.177091Z后态为68MiB/0%、无GPU进程、9031双栈closed，source不变、编译/worker/cleanup无错误。controller于03:58:09.190532Z完成，registry114/queue87已如实收口。

后继另隔离准备仅SAVE的worker部署；原1aff/84be/791c/e155冻结，先等待worker精确接口与互审，再由root唯一GPU运行原long VERIFY1。不得把本API门当完整服务验证，亦不修改当前已验运行树或共享代码库。
