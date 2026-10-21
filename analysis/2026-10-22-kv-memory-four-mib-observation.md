# 222731：首次观察到4MiB非 Torch估计差额与六块KV容量差一致

仅天数 BI-V150 / MiniCPM5-2B。本报告独立核启动内存标量与容量算术，不重复 framework 的完整原件门，不把 smoke 与长轮作性能对照；没有新增 SSH、GPU、参数修改或测试套件。

## 本次已解释到哪一层

222731 的原 `non_torch_increase` 比215849、220122均多4194304B，原 `non_kv_cache_memory` 同增4194304B，原 worker int 返回值同减4194304B；实际 KV 从521936变为521840 tokens。**本次原内存公式的分项传播已经有直接原件证据；具体哪项分配、库或进程造成该4MiB差额仍未定位。** 不能把本轮分项倒填所有历史521840轮。

`non_torch_memory` 是 actual `a8de` 的 `mem_get_info` 总占用减 Torch `memory_reserved` 所得差额，不是逐 allocator、逐进程的分配 trace。这里使用“非 Torch估计差额”，不把它直接命名为某个库新增的真实4MiB allocation。

## 原件与实际观察身份

- 新原件：`experiments/framework/20261021T222731Z-kv-observed-pair-capacity-context16k-long` 及 `-control`。
- root封存 tgz SHA256：`8ded4126824d40bac5869cbb254238b9de9dbcceaa67907a7e73b926030f991b`。
- 实际 `server.log` SHA256：`025144e6b17575129965e8dbdefc5bb82655e1770aa6fd92e88518f04d0ff21d`；control源码清单 SHA256：`c9f240d96f9137f006d5dece1ad55a59785b76cddd1d916be15ca441c5fbb3fb`。
- 本owner专项 JSON：[222731-four-mib-review.json](source/kv-memory-observer/222731-four-mib-review.json)，SHA256 `de35192db67a72681663f984e472e40e128d0a681fea730928ab0dff96de0574`。

逐原日志核：API233778只有ARMED；Engine233942在第46行ARMED、第91行一次DETERMINE_RETURN、第92行一次PARENT_RETURN。profile_context_calls=1，原 worker整数22443583692与原父list `[22443583692]` 相符；worker_method/profiling_context/parent_method三个恢复标志均True，没有拒绝或不完整事件。

实际加载的 WorkerFL `a8de`、io_common `6d8b`、UniProc `4625`、worker_base `7da4` 四源SHA与前两轮相同；control中原worker、runner e155、同observer6a字节也独立核真，新init为39fb。观察器没有新GPU采样；原 wrapper/__wrapped__、caller链与当前UniProc身份成立。logger前后不变，仍向root WARNING30传播。

## 逐项对照

下表前两轮数值完全相同；新列均取222731真实DETERMINE_RETURN。时间字段变化保存在JSON，不混入字节差额。

| 原字段 | 215849 / 220122 | 222731 | 差额 |
|---|---:|---:|---:|
| init与before_create `cuda_memory` | 153092096 | 153092096 | 0 |
| init与before_create Torch reserved | 0 | 0 | 0 |
| before_profile `cuda_memory` | 6318718976 | 6322913280 | +4194304 |
| before_profile `non_torch_memory` | 1092616192 | 1096810496 | +4194304 |
| after_profile `cuda_memory` | 6654263296 | 6658457600 | +4194304 |
| after_profile `non_torch_memory` | 1153433600 | 1157627904 | +4194304 |
| `weights_memory` | 5101233152 | 5101233152 | 0 |
| `torch_peak_increase` | 656424960 | 656424960 | 0 |
| `non_torch_increase` | 1000341504 | 1004535808 | +4194304 |
| `non_kv_cache_memory` | 6757999616 | 6762193920 | +4194304 |
| `requested_memory` | 29205777612.8 | 29205777612.8 | 0 |
| worker available原float | 22447777996.8 | 22443583692.8 | −4194304 |
| 原worker int / 父list元素 | 22447777996 | 22443583692 | −4194304 |
| graph estimate / 重构扣减 | 0 / 0.0 | 0 / 0.0 | 0 |
| 实际KV tokens | 521936 | 521840 | −96 |

before_profile Torch reserved始终5226102784、Torch peak始终5118105088；after_profile分别始终5500829696、5774530048。物理总显存均34359738368B。对应before/after free_memory分别减少4194304B，所有 `cuda=total-free` 与 `nonTorch=cuda-reserved` 等式成立。

特别是 profile 时段自身非 Torch差额三轮相同：

`after_profile.non_torch_memory - before_profile.non_torch_memory = 60817408B`。

因此，本次与旧两样本之间的4MiB差额在 `before_profile` 已存在，且到after仍保留；不能据此归因为 profile_run 当中新增的临时峰值。只把出现区间限制到原init基线之后、before_profile快照之前，仍不足以识别具体初始化操作或分配来源。

## 原公式与六块算术

固定 `collaboration/FlagOS-S2-vllm-plugin-FL/vllm_fl/worker/worker.py` SHA256 `a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24`：

- `:97–120`：总占用/保留内存的估计差额定义。
- `:171–185`：CM使用原init作为before_create，after−before_create得到non_torch_increase。
- `:565–572`：nonKV = nonTorchIncrease + peakIncrease + weights。
- `:595–599`、`:652`：requested−nonKV−实际graph扣减，然后原int返回。

所有上式由三轮真实字段独立复算。每个全模型16token块含42层，两KV头、BF16，每块688128B；算术如下：

| 返回值整除688128 | 旧两轮 | 222731 |
|---|---:|---:|
| 商 | 32621块 | 32615块 |
| 商×16 | 521936 tokens | 521840 tokens |
| 余数 | 354508B | 288972B |

6块为4128768B；4MiB=4194304B，比6块多65536B，恰解释余数再少65536B。商与真实KV日志一致，但本专项没有新取得 installed `kv_cache_utils` 生成器的floor源码/所有中间值，故保留为“原返回与实际池的算术一致”，不冒称新观察了该内部算法。

## 不能推出的结论与后续

不能据此确定是长轮标志、协议模块、VERIFY开关、编译cache、驱动库或观察器造成4MiB。旧220122同capacity runtime/同observer却为521936，也不能把额外protocol模块固定解释为少六块。init与profile之间包含多项操作，当前只有阶段快照，没有分配调用栈或所有权trace；观察本身也有CPU/日志扰动。

新轮仍是原context-long/VERIFY0，完整源码/DB/bench/协议消费者门由framework负责，不与旧smoke比较吞吐。本专项独立核418源后态子集/68MiB0%/9031双栈closed；root已封存DB519表19340行前后三SHA相同。没有调整利用率、强行固定KV容量或再追匹配启动样本。

root接续串行FULL时，按同观察器记录本轮分项；是否形成可比pair仍取决于actual KV、DB、CPU/源/参数及后验条件。即使下轮匹配，也只对该对照成立，不补造历史因果。

## 本地验收脚本的失败与修复边界

本owner首个专项命令同样尝试 `ast.literal_eval(EXPECTED_LOADED)`，因固定6a字典引用两个顶层字符串Name而ValueError，无通过文件；随后用已知四源显式SHA完成本专项。framework的a5b验收入口独立遇到相同问题，保留旧a5b及first-attempt原件，最小新增两个白名单Name的静态解析后成为c0c80dcf。

本owner已只读核c0c80dcf相对a5b仅该helper与一处调用，无observer/framework执行；未重复其完整raw门。此前只读审漏掉Name引用的事实保留，不把基础设施失败当设备数值失败，也不覆盖任何受测运行源码。


## 223613 FULL补充：本次配对的启动分项与实际页数组相同

后继 `20261021T223613Z-kv-observed-pair-full-context16k-long` 原件到齐后，本owner只核必要差异，不重复c0c80完整门或性能计算。专项JSON `source/kv-memory-observer/223613-full-memory-transfer-review.json` SHA **9f319d02d09a906916eca753862b4c90b8ea27062e5bef07d94418360f7272ca**；FULL log SHA `d27de1b97f0736a215d07b996133074700256fb266bf07859a1efe45f0fd91cd`，source-map SHA `2748cb691ccceed556fc8012eeb6a0cf540f399093d01bbcca3bfe4afe85c8a3`。root完整tgz身份未包含在本次派工回执，本JSON不补造该值。

Engine235489第91/92行真实单次DETERMINE/PARENT、profile1、原int/父list与三hook恢复通过；选定非时间worker/profile/snapshot/derived/logger/返回字段与222731**全部相同**，loaded四源身份也同，KV均521840。profile_time、各timestamp、PID与源路径自然变化，不称整个原件只有时间差。两个新long样本都带同4MiB residual分项，只支持本次容量条件，不据此归因long标志或某次初始化操作。

进一步实际命令差异：capacity是SAVE→ZERO→RESTORE→DROP；FULL是SAVE→RESTORE_FULL→DROP，没有ZERO RPC，真实FULL ACK zero_stage_executed=false/zero_calls=0/destination_bound/full_coverage均成立，覆盖717717504B。两轮真实R16688/1043页；SAVE23段/966calls、目的66段/2772calls，不仅几何相同，SAVE源页数组及RESTORE目的页数组也逐项完全相同。FULL本轮VERIFY0没有诊断回读，不把先前VERIFY1冒称本次全42字节验证。

这为同一pair的启动与传输几何提供必要共同条件；DB/CPU/完整source后态和总性能由framework完整门另核。本专项不把2772个ZERO调用的消失换算成DMA时长、吞吐收益或新accuracy，也不修改当前源/参数。
