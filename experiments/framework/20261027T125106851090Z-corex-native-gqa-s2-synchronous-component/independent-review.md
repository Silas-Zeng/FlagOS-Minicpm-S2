# 原生同步GQA完整loop增量独审

**无确定组件启动阻断，可由root执行唯一N64／S2／KV4096的原数值门后ABBA。** 最终tar `6f975b7c7cf0602ff86ce8872fabcd56d1b5d9a4b53c66f96e68bc3fe5f2f4eb`，116350B／23pins及tar成员逐字独核。CU `8aa05659f5111c30d90c65c4c796dbd6fa946e40f470953ae47b1bf54992bf7f`与实际123155编译输入一致；compile proof实际通过，variant仅synchronous_0。单页[v3独审](../corex-native-gqa-page16-v3-20261027/independent-review.md)及已通过映射资格复用，不把它当历史loop资格。

新增历史数学核查：所有32个PV C分量保持，各自乘原rho后作为下一MMA的C输入；QK每页从0开始，8次D16 MMA／8个PV输出片段及P组装保持。L用device fmaf，对照原641478 ASM824／831及tail1644／1651；本次LLVM实际`llvm.fma.f32`和ASM四处`ml_fma_f32`（full／tail各两项）吻合，不再依据原LLVM裸mul/add误判。实际资源shared8192／private0／SGPR62／VGPR76／双方spill0，只说明编译资源，不推occupancy或收益。默认没有V overlap／双缓冲，不混未来宏1变体。

S2绝对页序／上下界独核0、1、15、16、17、31、32、33及131071／131072等边界，无漏重；`lower>=length`在Q／table访问前return且不写scratch，原reducer的seg_valid继续遮蔽poison。新增尾页是整物理合法页SME读完后清无效值：CPU以任意uint16位型独立模拟valid1…15的K／V清理，word写者唯一、有效位不变、无效全+0；奇数V切口的有效低半字保持，均不越8KiB。K／V copy completion及barrier后才清／消费，页末同步后才复用stage。相对原masked load多读取合法页内无效槽的事实保留，worker因此新增未使用K/V槽NaN poison后输出不变门，不靠P=0掩盖NaN。

bridge仅接受N64／BF16／实际NHD strides及S2输出layout，按caller strides写partial／max／sum；mutates三输出schema、device guard、当前CUDA stream、输出地址和keepalive未见新增风险。worker A从实际backend捕获原producer及原reducer，直接A重放必须匹配实际输出／编译身份；B复用同输入和原reducer。finite最终输出及**所有partial状态跨臂硬逐位**、原FP64、tail NaN、空段／0长／负零／子正常／非有限分类、同址换值Graph、输入／RNG／输出guard均仍在失败即停路径。首次C++真实ninja命令检查宏0／目标／优化flags且拒泛fast-math；旧owner finally与v3 AST相同，未重复不变清理审阅。

计时只为producer＋原reducer的完整CUDA Graph ABBA，writer在setup一次且不计入本性能；未改writer，不能称writer＋Attention计时。实际长度统一4096、cache容量16384，已修timing-shape／scope，不称084521长度多重集或官方16K。23pins包不含本报告；CPU审阅未SSH/GPU、未改冻结资产。数学／运行失败或无益按既有规则停止，不调容差；即使组件正仍无生产、官方或模型资格。
