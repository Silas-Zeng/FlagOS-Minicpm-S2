# 完整R等差SAVE：最小worker接入与42层验证边界

仅天数BI-V150，2026-10-22。本轮只读规划，不新增worker/安装器/服务包装，不运行设备或重复验收。root独占GPU；systems负责032653唯一完整审计，hardware负责该门计时专项。

## 已取得的设备证据与仍未覆盖的范围

原件在 `experiments/framework/20261022T032653Z-kv-pitched-copy-gate{,-control}`。本人只读 `results.json` 头部/源身份和原编译命令，没有重跑完整审计或计算计时。设备门报告两组真实SAVE页序的一层完整字节、独立CPU页号/页内offset oracle、旧c95f、真实非零stream、guard、RNG通过，段数37→11与26→6。实际SO为 **9e33ecbf9cf57f52469db6b1d509a600cd1a8eeafe78a54095e88dc474c71fc0**，由真实Corex头文件和libcudart编译/链接，设备maxpitch=2147483647B。完整通过与性能结论以两owner的实际审计为准。

这是每层约17MB目的数据的一层门；不直接证明实际42个storage、约0.7GiB payload、整batch描述符、worker阶段库加载和失败强引用。模块支持42不是已执行42的证据。没有模型/accuracy或E2E收益结论。

## 唯一接入差异

复用固定FULL416树，协议 **1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8**、事务 **84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883**；从worker **5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477** 创建独立候选副本。原source/worker不覆盖，不叠72942进展victim、c6快照或其它新策略。

唯一传输替换挂点是5d9a第254行SAVE分支：`info = _copy(policy, raw, slot["host"], packet["pages"], range(count))`。新helper建立完整R正等差plan、校验所有42层Tensor/layout/extent并构造一个batch，向当时Torch当前流的原生handle提交。**原 `_copy` 保留不变**，继续服务FULL H2D、旧ZERO/RESTORE及诊断回读；FULL的整页覆盖证明和caps格式不因SAVE实现变化而放宽。

原SAVE源页与runner实际请求表一致、normal42/model/source guard、1GiB payload+1GiB guard、42个pinned host分配与headroom再查、producer device fence都保留。原 `_finish` 仍在真实submit后于同一个当前流记录Event并同步，之后才SAVED和成功ACK。原异常settle、失败Receipt、slot生命周期、epoch/serial、取消、Core旧FIFO/准入/页排序、R/digest/known token与采样路径不改。

## 强引用与错误是最重要的新边界

不能只把PreparedSave放helper局部变量。必须在首次可能提交前把它及bridge写入原slot（例如 `save_prepared/save_bridge`），它们间接强持全部42个raw/host、ctypes descriptor数组及动态库；原slot本就持raw/host。若API中途异常、随后device settle失败，RPC栈退出仍须保留这些资源，不能因helper返回/异常释放。成功Event完成后才可释放PreparedSave；桥可作为同进程固定资产缓存至退出。DROP仍只允许settled slot。

`CopySubmissionError.submitted_calls`只数SDK成功返回，并不证明失败那次内部没有工作；包括0在内均走原实际settle。新helper不拦截异常并重试旧copy，不先假造成功/完成ACK。超过设备maxpitch的显式linear展开仅能在首提交前发生。原worker的submitted标志可以继续保守表示“可能提交”，不把它误当真实成功调用数。

## source与SO部署的最小要求

新隔离source必须实际包含canonical新worker、py **818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd**、cpp **0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44**、已编译regular-file SO及其确定SHA，完整manifest记录所有改变。SO不能由运行中的worker临时g++构建，不能从任意环境路径加载；可直接复用032653实际SO9e33，或新CPU编译后重新冻结其实体SHA/头文件和库身份，不能静默把重编译物当9e33。

旧5d9a的原源身份guard保持；新worker额外精确锁py模块与邻接SO，控制器锁cpp、ABI取证和实际libcudart **d39d579627d19ddb903855ebc4859661579633a7ecc4d1ad51866d79296ba527**。原协议1aff未硬编码worker字节身份，由包装完整source map核新worker，不改协议来绕过guard。Bridge只在worker真实已有Torch/设备context、严格scope通过后显式构造，绝不在general注册、driver/controller导入或模型profile阶段加载。加载和首次准备成本属于真实候选成本；不靠额外请求移出性能窗。若资产/ABI/能力不符，在任何新copy前明确失败/标明未命中，不能静默宣称新路径已生效。

实际SAVE ACK可增加提交实现/线性与二维调用数/原连续调用数/SO指纹等小字段以证明命中，必须同时保原caps和byte/complete语义；不把这些计数称DMA描述符。原Core/事务对无关ACK字段无需变化。

## 是否需要额外42层门

**进入性能比较前必须有真实42层新SAVE的完整字节证据，但不必先单独造一个22GiB合成KV池门，再跑同样的真实服务。** 若单层计时值得继续，最短可合并为原long/VERIFY1的一次真实事务诊断：模型原样加载、真实抢占SAVE用42层batch，同key原FULL/42层恢复回读/runner六checks/实际consumer/正常32-0与完整后态。

原FULL的回读只比较“恢复GPU页”与“已保存host”，不能独立证明新SAVE曾正确读42层源。为避免此盲点，该诊断的SAVE完成后、原源free前，可复用已经预算并分配的**单层verify_buffer**，逐层用冻结c95f按原源页映射回读，再与新host对应层逐byte比较；每层通过实际Event后才能读CPU字节。所有42层通过才SAVED，已有原FULL诊断仍照常执行。无需新增0.7GiB影子host、额外GPU buffer、改变R或新接口；预算/强引用/异常settle仍归原slot。该额外D2H仅VERIFY1诊断开启，明确排除性能与未来VERIFY0，不把它的时间当SAVE加速。

该合并门同时覆盖真实42个独立层storage、约0.7GiB总payload、worker加载/原producer→Event→ACK以及真实恢复消费。若root先需要更便宜的42batch地址覆盖门，也只能作为选择性的较小合成42层辅助，不能冒充实际内存压力；本规划不预排此额外门，不新增测试。任何失败保原件而不重试掩盖。通过后才考虑同原参数/共同观察器/VERIFY0/DB与KV后验匹配的首组比较；收益未知，不继承原FULL准确率或默认集成资格。
