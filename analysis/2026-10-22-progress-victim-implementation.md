# 天数BI-V150：一次受限进展victim独立实现

[唯一设计](2026-10-22-single-victim-progress-candidate.md)现已实现为独立FULL1aff副本。默认关闭；仅用于隔离候选，尚未部署或上卡，不改旧FULL/worker/事务/观察器/原稳定源码。没有使用固定request ID、benchmark行号、token内容或未来输出。

| 文件 | SHA256 |
|---|---|
| patches/framework/candidates/biv150_kv_progress_victim_protocol.py | 72942f1f0c284069492b8ee7e1ca1348743e3b9ee49e7da05b8cf9024ac610ef |
| tests/test_biv150_kv_progress_victim.py | b5a71507c742d49f34087035e50f6bd42667a847dc8ad71cb1921cd28333868f |
| analysis/source/preemption-snapshot/progress-victim-cpu-check.json | 838546644dd1c11db64eccf6b9bb1e8384abd34e65fa8ad93422c6c5d888f137 |

## 变更范围与原语义

冻结原FULL1aff的17个既有函数逐byte不变；原Core只增加每Engine一次attempt标志与两个计数，install增加原87a schedule精确两处变换/selector命名空间。原waiting restore插点保持，唯一新策略挂点是原FCFS None路径的pop下标；删新pop表达式并删原restore一行可逐byte逆回87a原方法。额外锁定自然已加载SchedulerOutput文件f281源身份。最终部署仍映射为canonical `vllm_fl/patches/biv150_kv_protocol.py`，无需改原791c init/footer。

原FULL1aff、worker5d9a、txn84be、c95f copy不改。SAVE真实设备fence和完成ACK后原free、旧FIFO frame消费、capacity早退、私有页排序、FULL字节回读/发布、cached-state/generator证明原样；不叠快照c6或内存观察器6a。本模块不直接调用采样或GPU值API，但改变victim/后续batch可能改变全局采样行与输出，不保证随机输出或FCFS公平不变。

## 选择、回退与证据

原真实None且FCFS pop才调用selector。必须原eligible/同Engine、victim为空、实际HostSlot key为空且used=0/固定1GiB；一次attempt在Request/queue/owned遍历之前记入Engine，元数据错误或空集合也不重试。原Request真实类/方法/映射对象/仍RUNNING守卫，队列只读真实tuple3中SchedulerOutput，不访问Future；R只减既有queued spans，不用placeholder或current尚未issued项代替。

index>failed、三份本schedule容器均未scheduled、非streaming decode、保护最小合法remaining及最大confirmed集合，进展严格高于tail；R完整页/逻辑覆盖/1GiB cap及真实ref1页弥补derived deficit。按confirmed最大、同值原位置偏后选择。无候选、未知或记录异常走原tail；缺host实际余量仍由原worker真正SAVE判定。一次只是主动替换次数，后续真实None可原tail继续，不能宣称总preempt=1。

新稀疏事件 `PROGRESS_VICTIM_DECISION` 带selected布尔、原tail/failed/selected对象ID与动态原索引、confirmed/R/bytes/private/free/derived需求/候选数。**DECISION先成功输出，再increment selected计数**：事件attempts=1，若selected=True，该事件selectedcounter仍0；后续SAVE/RPC为1。后验应核实际顺序和selected字段，不能错误要求decision计数已为1。元数据错记PROGRESS_VICTIM_REJECTED后原tail，原preempt异常在helper的except退出后发生，不增加元数据错误context。

## 唯一必要CPU合同

`python -X utf8 -m unittest discover -s tests -p test_biv150_kv_progress_victim.py -v`

首轮1test/0.092s/exit0。使用实际Request06b1类AST及原87a内层while语句，不import框架/torch或执行模型init；验证动态tie后方、三容器各自排除、保护集合、Request身份/streaming/private/cap/prefix/未知队列回退、slot owner/bytes、queued2≠placeholder11的R、首次None才attempt、第二次None原tail、原current索引/budget/allocator调用与同异常context。token容器禁止值读取，Future对象禁止任何属性读取。完整schedule双切口编译/漂移拒绝/逐byte反向、17函数及worker/txn SHA亦核。

它不是完整scheduler、GPU或随机数模拟；不证明实际资格、选择/SAVE/FULL/consumer、字节或收益。初次编辑时多文件apply_patch因handoff上下文不符整体拒绝，拆分后成功，无部分runtime写入；没有合同或设备失败，也没有跑旧copy/协议套件。

hardware已独立只读runtime/17函数/冻结worker事务/唯一合同与check，未发现进入一次最短VERIFY1机制门的阻断，未重跑测试。systems负责新独立417源包装：固定原FULL416，仅替canonical协议并加新manifest，init791c/原innovation字节不动，不叠6a/c6。当前只准备包装，真实门由root串行启动。下一阶段必须不同tail的真实decision、SAVE选中同对象、动态FULL42层全字节回读、runner/consumer、32/0/全源/DB/post；机制通过后才谈匹配性能和必要accuracy，不继承103/105。
