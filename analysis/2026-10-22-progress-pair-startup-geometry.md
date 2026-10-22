# 原FULL与进展victim首对：启动分项与几何专项

仅天数BI-V150本实例/MiniCPM5-2B。共同6a、VERIFY0、原bc51/SERVER/context-long/seed721201；root独占设备。本文仅独立解析启动分项与实际页几何，不执行systems唯一3f1dc完整验收，不把策略行为相等作为环境匹配条件，不给新accuracy或官方成绩。

## A：020721原FULL已核

A为 `20261022T020721Z-kv-progress-pair-full-context16k-long`，包SHA `73ca1a3d3ecf93d81c155041eaa4db3932a58fa234278565676580fe66472a2f`。独立记录[020721 JSON](source/preemption-snapshot/020721-full-startup-geometry-review.json)。systems完整门另已通过；本owner没有重跑。

Engine252228的DETERMINE/PARENT在第91/92行，profile仅1次、原worker整数返回22447777996、父list原样返回，三hook均恢复，四份实际loaded源身份成立。前端252059另有ARMED，仅表示入口安装，不能当第二次profile。logger前后相同，root有效级别30；INFO不显示不等于没有原始内存分项，6a取的是自然已产生的CPU字段。

| A原始字段/换算 | 值 |
|---|---:|
| weights | 5101233152B |
| nonTorch increase残差 | 1000341504B |
| Torch peak increase | 656424960B |
| nonKV，前三项之和 | 6757999616B |
| requested | 29205777612.8B |
| available原float / 原int | 22447777996.8 / 22447777996B |
| graph deduction | 0 |
| 除以688128B/model-block的商/余 | 32621 / 354508B |
| 实际KV | 521936token |

各snapshot均满足 `cuda_memory=total−free`、`non_torch=cuda_memory−Torch reserved`；before→after profile的nonTorch增量60817408B。这个nonTorch只是全设备内存与Torch reserved的差额估计，不是某allocator分配trace。

A所有选定非时间分项与215849 stable-smoke、220122 capacity-smoke逐项相同。比223613旧long，A为较低4MiB残差的一组；这是新的观察事实，不能把long开关、FULL/progress代码或某库定位成原因，也不能拿不同容量历史run替代本次A。

## A实际原FULL行为

| 事项 | A实际值 |
|---|---:|
| R / 保存页数 / payload | 16704 / 1044 / 718405632B |
| SAVE源连续段 / 42层calls | 24 / 1008 |
| 排序目的段 / FULL calls | 66 / 2772 |
| ZERO / 诊断回读 | 0 / 无，VERIFY0 |
| 原consumer scheduled token | 8，不等于8个新输出 |
| fast reject / restore skip | 454 / 454 |
| progress新decision | 无，原FULL1aff |
| DB before / after | 同523表、19474行，三SHA均同 |

真实三ACK为SAVE→FULL→DROP，同Key/rid；完整覆盖proof与host释放成立。原子后态/完整418源/32请求结果等由systems完整验收负责，本文不重复。

## B：021658实际机制通过，环境失配，不计算收益

B为 `20261022T021658Z-kv-progress-pair-progress-context16k-long`，包SHA `c6989051d9caa8e2dac548e88e85b155fab1d95c0bbacc32f4523eea97e46176`。独立记录[021658 JSON](source/preemption-snapshot/021658-progress-startup-geometry-review.json)。本owner没有运行3f1dc完整验收。

Engine253818第91/92行同样只有一次真实profile、原worker int22443583692→父list，三hook恢复；实际四loaded源与A相同，logger前后不变。init/before_create、weights、Torch reserved/peak及graph值均与A相同，但before_profile/after_profile的cuda内存与nonTorch残差各多4194304B。profile自身的after−before nonTorch仍为60817408B，故额外4MiB在profile前已经存在；不能定位为某库、allocator、进程或72942造成。

| 容量链 | A原FULL | B进展victim |
|---|---:|---:|
| nonTorch increase残差 | 1000341504 | 1004535808 |
| nonKV | 6757999616 | 6762193920 |
| 原worker返回int | 22447777996 | 22443583692 |
| /688128B的块商/余 | 32621 / 354508 | 32615 / 288972 |
| 实际KV token | 521936 | 521840 |

B available少4194304B，块数少6、token容量少96；6块为4128768B，另65536B体现在余数354508→288972。这是实际分项与容量的算术吻合，**不是4MiB具体分配根因**。共同observer准确记录了失配，没有令环境自动相等。

B真实选择也与旧015315不同，必须据本原件记录：failed index20、selected index21、原tail index30，候选9条；selected confirmed392、tail319、最高561，合法remaining632大于最小463。选中rid `cmpl-bench-1aa8c016-16-0-aa813076` 与实际SAVE/FULL/runner/consumer同Key，源码规则仍动态而非硬编码index2。选中ref1 owned1049页，但安全保存前缀仅1048完整页。

| 实际行为，允许两方不同 | A | B |
|---|---:|---:|
| R / 保存页数 | 16704 / 1044 | 16768 / 1048 |
| payload字节 | 718405632 | 721158144 |
| SAVE源段 / calls | 24 / 1008 | 26 / 1092 |
| 目的段 / FULL calls | 66 / 2772 | 66 / 2772 |
| fast reject / restore skip | 454 / 454 | 462 / 462 |
| 原consumer scheduled token | 8 | 9 |
| 新decision | 无 | 真一次非tail选择 |

两侧均真SAVE→FULL→DROP、无ZERO、host最终释放，VERIFY0无诊断回读；B的9是原update消费的scheduled token，不是声称新增9个输出。R、页图、段数和等待允许真实不同，但本次同时容量失配，不能将表中差异单独归因于victim选择。

## 收口与复现边界

A before=after=B before=after的snapshot/schema/logical三SHA全部相同，均523表/19474行；同DB不抵销KV及启动分项的明确失配。本对照**不报告正收益或负收益，gain为null**，不从耗时计算TPS百分比，不改参数或追加盲重跑追容量。

原件与机制证据保留，公平、全局采样等价与accuracy仍未证明。完整418源/退出后态/原性能文件由root与systems唯一验收负责；本owner只完成启动分项和动态几何专项。按root本阶段要求收口，本地checkpoint，不向GitHub或PR写入。
