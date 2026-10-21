# 天数BI-V150：一次受限的进展优先victim候选，仅设计

230548实际快照已验收，见[结果](2026-10-22-preemption-snapshot-230548-result.md)与[完整JSON](source/preemption-snapshot/230548-review.json)。root仅授权本文具体化一个后继候选，**没有新runtime、builder、CPU合同或设备执行**。受测FULL1aff/worker5d9a/txn84be、capacity、观察器和原df780都不改。

## 唯一建议与本轮实际非空证据

仅在原RUNNING `allocate_slots` 真实None后，FCFS原pop处允许**每Engine整个运行至多一次**替换victim。目标是保留当前失败请求和可能先完成者，把原来进展最少的尾部留在运行集合；在其它合法对象中选择已确认输出最多者，检查是否能缩短恢复后的尾部。它是待否定的启发式，不承诺公平、吞吐或更早恢复。

候选集合必须同时满足：

- 原FULL严格模型/单卡/normal42/Async V2/no spec/no encoder/no connector等scope；当前单host slot及事务为空，本Engine未尝试过替换。
- 对象为当前实际running成员，原running index严格大于failed index；未出现在本schedule的scheduled_running_reqs、num_scheduled_tokens和req_to_new_blocks中。失败对象自身永远不选，禁止按请求ID、文本、benchmark序号或未来输出评分。
- 非streaming、已在decode；不在全running的最小“合法max减已确认输出”集合，也不在全running的最大已确认输出集合。两集合都保护，不能将它们称真实最早完成者。
- 进展严格高于原tail，安全R按原issued减全部旧queued span并保留至少一known token取整；R≥16、payload≤1GiB且完整逻辑prefix覆盖；只读当前真实owned唯一ref1非null页，可释放数足以弥补本次exact快路径derived deficit。hashed页不排除其可释放性，但绝不当fresh恢复目的页。

评分唯一为 `已确认输出数` 最大，同值取更靠后的原running位置，尽量少偏离原尾部规则；无任意权重或阈值。集合为空、未知元数据/源码、slot非空或已用过替换时直接原tail。只需在首次可判断的真实None遍历一次，不新增逐token排序器。静态1GiB资格不证明host实际余量；实际SAVE/ACK仍完全由原worker判定。

230548按这些条件确有**28条结构候选，即原index2至29**。failed为index1/output560，index0/output569同时落入两个保护集合；原tail index30/output327因“严格高于tail”排除。唯一规则会选原index2/output552，剩余合法上界472，owned1059、R16928、payload728039424B；原tail剩余697、owned1045、R16704、payload718405632B。替代者比tail多释放14页，保存量同时增加9633792B。该对象由合法进展规则选出，**index2只用于说明这份原件，不能写入实现条件**。本轮读JSON的集合计算只用于设计，不是新scheduler模拟或性能结果。

## 精确挂点与原语义边界

实际df780:522–568的None内层在FCFS执行 `preempted_req = self.running.pop()`；其后仍原 `_preempt_request`、preempted列表append、与failed同对象时break，以及重试allocator。最小实现只把这个FCFS pop的下标从默认尾部变为严格guard得到的原j；不调换整个running列表、不碰WAITING选队/重新准入顺序。原while条件使用实时len，j>req_index意味着当前failed对象和其前缀的位置不变，后继原req_index递增可继续正常访问收缩后的列表。

这能避开PRIORITY分支针对**本schedule已经scheduled**对象的撤销tokens/blocks/spec/encoder和返还budget路径：不仅j>failed，还要显式证明对象不在三份当前容器；scope已排spec/encoder。任何不符回原tail，不支持PRIORITY，不尝试任意已scheduled对象。但这只保护本schedule，**旧batch_queue中已issued frame仍存在**，不能跳过、等待Future或伪称无在途写入。

实现时应在独立FULL协议副本的原schedule内存变换中组合这唯一pop改动，保原waiting restore插点。两项改动分别可逐byte逆回相应固定前件；不先装快照c6再叠协议wrapper。FULL原SAVE的device fence/真实完成ACK→原free、FIFO旧frame处理、源身份与digest、私有目的排序、RESTORE_FULL/回读/发布、runner cached-state/generator不变证明全部保留。worker/txn字节不动，不截断R或改准入。

只允许一次**替换尝试**；选择完成、原pop前即记used。其后即使SAVE失败也不再新选其它victim，不在已free/绑定/发布后改走另一对象。原FULL若SAVE失败但真实settled，仍按它现有契约让已选对象走原重算；未settled照原fail-closed。原调度若仍需额外抢占则原tail继续，不能声称总抢占数被固定为1，也不能保证原failed绝不在后续原路被抢占。所谓保护仅约束本次主动替换集合。

## 可否定点与最短后继门

最强反证是：较高进展对象本来可能更早释放页，抢占它推迟容量释放；更大SAVE或更碎目的copy抵消尾部改善；APC复用与额外原路抢占改变实际恢复等待；选择后实际不能SAVE/restore；或原尾部根本不是最后完成者。原tail策略的公平目的也会受损。改变batch成员/全局采样行分配后，原103/105准确率不能自动继承，保generator身份不等于全局随机输出不变。

若root下一阶段批准实现，一个定向CPU合同足够验证实际内层while AST中单次pop替换、j>failed未scheduled/保护集合/slot/used回退、原allocator调用/顺序/异常和逆回；**现在不执行**。随后只一次原context-long/seed721201/原SERVER、VERIFY1诊断，不新扫shape或先跑官方全量：必须真实记录原tail/选中对象/原因与索引、未scheduled证明、后续原preempt数，且实际选中不同于tail。复用原FULL字节门，动态R/42层全量回读/真实SAVE→FULL→DROP、无ZERO、runner6checks和原consumer、全部32/0/源码/DB/post。未命中、缺字节/消费证据或安全回退即记未验证/失败，不算策略成功。

只有机制正确后，才用冻结FULL与新selector、共同观察器、VERIFY0及相同DB/KV/原参数作最短长负载比较；不仅看总耗时，也保实际等待、抢占与最终consumer。失配不追容量或强改参数，负结果保留。若有正信号再安排必要准确率门，不能用一次快照/字节恢复通过代替准确率或官方成绩。
