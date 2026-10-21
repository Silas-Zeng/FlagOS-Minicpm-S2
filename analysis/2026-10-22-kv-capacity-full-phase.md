# KV容量早退与完整覆盖恢复：本阶段记录

本阶段沿用上一轮工作，只覆盖天数BI-V150和MiniCPM5-2B。沐曦C500由队友负责。原服务参数、bc51负载脚本、模型精度和固定框架版本保持；root独占设备，三个子智能体并行做本地研究、实现与互审。

## 已完成的真实测量

| UTC run ID | 目的 | 结果与限制 |
|---|---|---|
| 20261021T212106Z-kv-capacity-context16k-long | 容量必要下界早退，VERIFY1 | 32成功/0失败；462次实际早退，42层717717504B回读通过，原输出消费16 tokens。227.191134395秒只属诊断。 |
| 20261021T213016Z-kv-capacity-pair-stable-context16k-long | 冻结080656，VERIFY0基线 | 32成功/0失败；220.505020230秒；KV521936；DB519表19340行三SHA前后不变。 |
| 20261021T213616Z-kv-capacity-pair-capacity-context16k-long | 累计67e4候选，VERIFY0 | 32成功/0失败；218.917006328秒；KV521840；DB与基线前后相同，仍因KV容量失配不可归因收益。 |
| 20261021T214400Z-kv-full-restore-context16k-long | 完整覆盖恢复省ZERO，VERIFY1 | 32成功/0失败；实际SAVE→FULL→DROP，无ZERO；718405632B全42层回读通过，原消费者8 tokens。226.794827790秒只属诊断。 |

四个完整run/control目录均位于 `experiments/framework/`，原CSV、日志、GPU样本、源码、精确命令和后态全部保留。213616的容量限制在读取性能结果前即已记录；不补基线追求匹配容量，不从两个绝对时间计算可归因提升，也不把本累计对照说成单独早退的收益。

原件包SHA256依次为：

- 212106：`8e04b0b6301c724741759d3a2926e17726b011448ec28b8a14a7ac2ce50af537`
- 213016：`5b45a043eb5e6c85ab144270fe21cce560b3f3dfa355352cbb0840c51966de6e`
- 213616：`49e79345ccc94f442c3ab46277691dfa0101882d4914ff7d5737f1782cc26d4d`
- 214400：`21ae6e302795fba5d6b09b6597d26cd0e58d95c3805cffe079ded2934ca981ea`

容量机制实际验收见 [机制结果](2026-10-22-kv-capacity-mechanism-result.md)；两个VERIFY0的机器审计位于 `analysis/source/kv-worker/capacity-pair-*-review.json`。213016的shutdown EngineDeadError原样保留，exit0与32成功不代表日志没有告警。

## 完整覆盖恢复的独立候选

下一候选明确增加真实 `RESTORE_FULL` 操作，从SAVED状态重新验证42层整页覆盖、绑定实际目的页，保留原恢复前device fence、真实完成事件、强引用和失败生命周期。它取消该完整恢复中的ZERO阶段，不伪造ZERO ACK。只有缺少资格且尚未提交时才能走旧ZERO/RESTORE，提交后失败不降级重试半写页。

三个独立候选及唯一联合CPU合同已互审：worker `5d9a082f…`、transaction `84be2242…`、protocol `1aff952a…`；完整身份见 [worker说明](2026-10-22-kv-full-restore-worker.md)和[事务说明](2026-10-22-kv-restore-full-transaction.md)。CPU合同不执行GPU copy/event，不替代设备证明。

真实门 `20261021T214400Z-kv-full-restore-context16k-long` 已于21:49:12.117141Z exit0，新source `code/kv-full-restore-20261021T214400Z`，builder `b4e04e50…`、launcher `63947c7f…`，原bc51/seed721201/VERIFY1。实际KV521936、R16704/1044页，SAVE24段/1008calls，恢复目的66段；FULL与回读各2772calls、全42层718405632B通过、没有ZERO、454次早退、runner六检查与原消费者8 tokens通过。DB519表19340行三SHA不变，21:49:38.171431Z后态416源一致、68MiB/0%、无GPU进程、9031双栈关闭。原shutdown EngineDeadError/WARN保留。

这是明确删除本事务清零工作的实现证据，尚不是吞吐收益或完整模型accuracy。source清单SHA `a67c717f5e1f7ab5e2240dc9cd8623c02a91aa2b2958b9ee0bf206c791183829`，包装清单 `93375c426c9fb0b4d5abdb869ba94a8fab0a01ce1863ab0e1bd9785f586827fe`；独立整体验收及硬件几何核对已落盘。

## 后续方向及反证

6个逻辑block相差4128768B，只证明KV池最终量化结果不同，不能直接认定某个内存分项相差同样字节。214400又为521936，不支持“增加协议模块一定少6块”的简单归因。

随后已完成两个最短启动观察：`20261021T215849Z-kv-memory-stable-smoke`（412源）与`20261021T220122Z-kv-memory-capacity-smoke`（418源）。二者使用同6a772a观察器，原bc51 smoke-only/服务参数/VERIFY0，均正常exit0；原件包SHA分别为 `f9e37bd5b7f02d9d39fcad7291a27727e26efff7840ecf8c579f5eac10842044` 和 `b2bab46a3cda84b0654354e7848af52b40711061d61992690bc233b01f6ff290`。两run及控制目录均在 `experiments/framework/`，DB三SHA前后全同，后态空闲通过。

两次全部内存组成原值相同：weights5101233152、nonTorchIncrease1000341504、peakIncrease656424960、nonKV6757999616；requested29205777612.8、available22447777996.8、原int返回22447777996，graph扣除重建0。各自profile调用1次、原Parent list同值、三个hook恢复，KV均521936。**这次没有复现容量差，历史根因仍未知。** 当前INFO日志缺失有实际root WARNING30继承链支持，不改日志配置、不全局DEBUG或导出环境。

下一次性能验证计划在双方共用此单次启动观察器的前提下比较冻结capacity与FULL，附带真实分项，隔离省ZERO。仍需新包装固定身份和实际DB/KV匹配；这里仅是后继计划，没有新性能结果。观察器的stdout/CPU路径可能影响启动，不能把新值当历史值或声称完全无扰动。

按硬件和输入研究的chunk对齐方向已给出具体反证：[固定预算调度研究](2026-10-22-fixed-budget-scheduling-review.md)。实际Attention启动规则含一个上界CTA，向下对齐可能只把有效CTA变成早退CTA，且总M形状更多；构造模型不等于服务实测。因此当前不直接增加这一实现，也不重复已有growth、终止输出回收或参数扫描。

所有新协议均为隔离实验候选，未通过新的完整模型accuracy与官方复现门，不进入默认提交代码。共享代码库不推送；本阶段资料在一致收口后发布到专用私有实验库，最新覆盖边界以 `CURRENT_WORK.md` 和发布回执为准。
