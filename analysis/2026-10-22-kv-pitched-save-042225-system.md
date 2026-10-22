# 042225：真实42层SAVE与FULL两组字节证明通过

本agent唯一验收完整实际run/control，报告 `analysis/source/kv-pitched-copy/042225-system-review.json` SHA `d7213a76ff17d4a9fe46e031b2fe52ca8dfd72cf9e57e499f25fed7d3b3ad334`。归档SHA `711da3fc175f85f0678f56dbf3ae266d27af9757ce281e804834776ec6b08ab2` 已在本地实体复算。只复用旧2071的raw长负载和FULL链检查：source416→420，原SAVE连续调用断言替换后，再独立按真实页序重算新正等差几何。未执行候选、桥、旧run或测试，未新建大型验收框架。

真实420源保持原FULL基点的protocol1aff、transaction84be、init791c、runner e155及旧innovation原字节；只有新SAVE worker a662与固定818e/0a4d/SO9e33、独立manifest为约定差异。封存builder cd3d、launcher df6a与原bc51 SERVER/context-long/seed721201/VERIFY1均核，source归档/live和installed Attention54c一致，不叠进展victim或启动观察器。

Engine/worker同PID262318，真实事务R16688、1043整页，共717717504B，原源页23个连续run。新SAVE保持全部原页次序与字节，形成5段/层，42层总计210次API提交：168线性、42二维、fallback0；原c95f同页序需966次。actual current stream为0，服务中合法，不能套独立API门的非零stream要求；实际maxpitch2147483647B。提交回执 `save_submission_completion_ack=false`，worker在原完成event后才返回completed/successful。

| 证据 | 完成字节 | 调用数 | 实际结果 |
|---|---:|---:|---|
| 新SAVE | 717717504 | 210 | 42层成功ACK |
| 源free前旧c95f独立对照 | 717717504 | 966 | save_verification_layers42 / passedtrue |
| 原RESTORE_FULL | 717717504 | 2772（目的66run×42） | full_coverage / destination_boundtrue |
| 原FULL恢复后独立回读 | 717717504 | 2772 | verification_passedtrue |

这两组字节证明分别核对，未把新SAVE的 `save_verification_*` 与原FULL的 `verification_*` 混淆。原日志严格依次为SAVE真ACK→SAVE_ACK_FREE→等待→私有目的页排序→FULL真ACK→发布→DROP→runner六项检查→原output处理。三条RPC为SAVE/FULL/DROP、serial1/2/3，同key/epoch/实际请求对象，0ZERO；DROP后host引用与payload均释放。原runner缓存状态、computed前缀、整block表替换、generator及output IDs六项均true，原消费者处理16个scheduled tokens。fast462、无rollback，原metrics抢占0→1。

host payload上限仍1GiB，额外1GiB guard；本事务诊断单层buffer17088512B，SAVE前观察用量6384115712B、pin后7833116672B，20GiB cgroup下guard核通过。均为观察值，不作host峰值保证。a662成功SAVE证明实际libcudart maps严格guard代码已通过，但映射字典只存在slot、未进入ACK；本报告不冒称直接保存该PID的maps实录，也不拿微门字典代替。

原请求32成功0失败，524288输入/32768输出，耗时230.82578303012997s，2413.317926131704 total tok/s，TTFT62799.64288184419ms。**仅双回读机制诊断，不计算吞吐收益。** KV521840、CPU quota6、物理32768MiB；DB前后523表19474行，物理dc2c7646、schema0dc7a465、logicalc05d7e31三SHA均相同。

run于04:27:41.433901Z完成，04:29:03.163250Z后态为68MiB/0%、9031双栈closed、无GPU进程，420源/live一致。测前及shutdown ERROR均空，原force-kill WARN保留。完整准确率、全局随机数逐token等价、取消/多victim或默认部署资格不由本单事务诊断证明。

registry115、queue88已收口。用户明确确定收益不必大测试，本必要真实正确性门已完成；不自动追加大官方或重复长pair，下一步由root结合本证据决定，当前实现与原件独立保留。
