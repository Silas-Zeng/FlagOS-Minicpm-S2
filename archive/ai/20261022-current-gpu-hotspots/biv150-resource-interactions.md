# BI-V150资源交互：单项负结果不等于组合负结果

2026-10-22，hardware_innovation；仅CPU/公开一手资料与本地归档，不SSH/GPU、不改运行源。适用当前实例16SM/32GiB、warp64、6CPU/20GiB主机；不将完整板卡参数缩放给实例或C500。

## 已知与未知

当前6f/54c的114435真实mixed三步均D1/P2047，2D占可见kernel累计60.2339%、GEMM31.7161%，不是全服务占比。w16严格过但慢31.71%；121701 Vlate严格过且regs102→100、shared65536→49152、spills均0/w8/s1，wall慢1.4523%、Event慢1.3014%。这些负结果全部保留，只否定已测单项，不否定新的资源交互。

| 项目 | 一手证据与边界 |
|---|---|
| warp64 / ivcore11 | 本地actual compiler `a0d2bbda…`:126/110；[FlagTree iluvatar compiler](https://github.com/flagos-ai/FlagTree/blob/main/third_party/iluvatar/backend/compiler.py)亦明确warp64、capability71映射ivcore11。不是NVIDIA SM71硬件。 |
| 每kernel上限 | actual `tmp/current-biv150-loader-source/driver.c` SHA`6d1b04ccaad92e4b513b79139a4d56980cf580f530cf134447e6840f3e98d847`:78/81，`max_shared_mem`取PER_BLOCK_OPTIN，`max_num_regs`取PER_BLOCK，不能当SM总池。 |
| 每SM shared / register file / thread / CTA上限 | root124857实际SDK读取：shared131072B、regs262144、threads8192；perblock threads4096/shared131072/optin131072/regs262144。**最大CTA数仍未知**（actual头无对应枚举），实际分配粒度/驻留不由这些数独自确定。[公开driver源码](https://github.com/flagos-ai/FlagTree/blob/main/third_party/iluvatar/backend/driver.c)支持区分perblock与perSM查询。 |
| async / pipeline | actual compiler:299/307–309/329–337已有SME load、调度/软件pipeline、prefetch及async-copy lowering；不等于已证明本kernel真生成异步指令或有效重叠。actual:386明确ivcore11没有硬件named barrier/setmaxnreg，warp-specialization需shared软件barrier，不能照搬Hopper/Blackwell。 |
| 矩阵峰值 / HBM带宽 / cache容量 | 矩阵峰值和实测带宽仍未知；root124857 SDK报L2=16777216B、global/localL1支持=1、SMclock1500000/memclock1600000/buswidth2048（原字段单位按SDK）。[厂商天垓150页](https://www.iluvatar.com/productDetails?fullCode=cpjs-yj-xlxl-tg150)明确完整产品64GB/350W，却未给本次所需每SM/矩阵/带宽数值；支持/开发者页未返回可读规格。没有采用第三方256TFLOPS/1.6TB/s或按32/64直接折半。 |

本地actual编译器：`experiments/source-audits/20261021T183920Z-compiler-cache/installed-triton/backends/iluvatar/compiler.py` SHA`a0d2bbda2f779b528147a238ff6fc558d026478f72d3d12d51d27f48f1aa570a`。[官方2026-10-12 iluvatar手册](https://github.com/flagos-ai/FlagTree/wiki/User-manual-for-iluvatar)可核Corex4.5/Triton3.6部署关系，但不是实例硬件规格。公开main新增的FA pipeline/chain-dot pass不在该actual源，不能当已安装功能或升级编译器。

## 组合一：Vlate＋保留原kernel缓存偏好（优先，有新的实际分支证据）

actual loader:146–157仅当`shared > 49152 && shared_optin > 49152`时执行`cuFuncSetCacheConfig(PREFER_SHARED)`及`MAX_DYNAMIC_SHARED_SIZE_BYTES`设置。原64KiB进入，Vlate恰48KiB跳过，因而A可能同时跨过loader状态阈值。**这直接支持检查A+B，而非宣布已定位1.45%回退原因**：Corex可能忽略偏好，SM/L1/shared是否共池也未知。

B只在独立child里给Vlate的真实CUfunction设置与baseline同一缓存偏好，kernel、shared需求、w8/tile、数学及输入不变；不修改installed loader或全局context。先从actual SDK头核API/枚举、保存原function属性/调用返回；没有per-function getter就标不可观测，不能用context cache状态替代。`MAX_DYNAMIC_SHARED_SIZE_BYTES`是容量上限，不等于实际分配，不能为“相同”盲设未需要的数值。

最短判定：沿已过8f833门的D1/P2047/KV16K，原版vsVlate+B，先严格bits/整KV/RNG/流，再一次32ABBA并记资源/CPUstat/API返回。Corex不支持或无区别即保反证停；只有真实局部正信号再谈服务。现有A负与旧w16负不排除此B，亦不承诺组合正。

## 组合二：Vlate＋仅内层的一步K预取／有限软件流水（次选，尚未实现）

A释放了16KiB活跃shared且略慢，可能少了提前取V带来的延迟隐藏；此因果未证。B的目标是在当前PV期间准备下一tile的K，而不是全局再扫stage/warp：固定w8/BM128/T64/s1、原QK→softmax→PV顺序与acc；只对`j+1<loop_hi`预取原下一K地址，最后/partial tile不越表、不新增无效页访问，普通BF16且cache在本次Attention期间不被写。这样用部分A腾出的资源交换真实load/compute重叠，理论K/V字节与dot数不变，寄存器/shared可能反增，未证明会更快。

[Triton官方tl.range契约](https://triton-lang.org/main/python-api/generated/triton.language.range.html)区分内层`num_stages`与kernel参数：前者尝试流水更多load，也可禁止acc多缓冲。这是候选实现语义参考，**不是本机支持证明**。若借loop-local属性，先核actual语言签名与生成TTGIR；若手工lookahead，仍先比实际IR是否被消除/重新前移。不能引用[TE-FL文档](https://docs.flagos.io/projects/TransformerEngine-FL/en/latest/getting_started/install.html)的“stage1禁多缓冲”作为BI证据，该段明确属于Ascend故障。

最短判定仍仅同一真实层fixture：编译记录原/A/B资源与load-wait/布局信息，编译资源拒绝或无新流水即停；数值过后只一次32ABBA，不扫多个深度。软件barrier/双accumulator导致额外负担也保留。无需新框架、现成3D路由、量化、spec或官方参数改动。

## 解未知所需的最少运行时观察

root已完成124857只读属性查询，primary context前/后active0，19项属性均rc0；本owner没有调用设备API。后继尚缺实际kernel属性/驻留，可由唯一设备owner在既有短门进程内取，避免另开benchmark：

- 按实际SDK头解析`cuDeviceGetAttribute`映射，分别记录MAX_SHARED_MEMORY_PER_MULTIPROCESSOR、MAX_REGISTERS_PER_MULTIPROCESSOR、MAX_THREADS_PER_MULTIPROCESSOR、MAX_BLOCKS_PER_MULTIPROCESSOR及per-block/optin/warp/SM数；逐项返回码，不支持就是未知，不抄CUDA枚举整数。
- 对原/候选真实CUfunction记录NUM_REGS、LOCAL_SIZE_BYTES、SHARED_SIZE_BYTES、MAX_DYNAMIC_SHARED_SIZE_BYTES、MAX_THREADS_PER_BLOCK；若实际头/API支持，再取preferred carveout和精确occupancy（同512线程、实际dynamic shared）。已有n_spills来自LOCAL_SIZE_BYTES/4，不能把报告值当全芯片寄存器容量。
- 需补读的精确SDK链：`/usr/local/corex-4.5.0/include/IX/mapping_cudart.h`、`IX/ixrt/ix.h`、`IX/ixrt/driver_types.h`、`IX/ixrt/ix_runtime_api.h`及其必要直接include；已有030314/024142归档只证明部分alias，尚非上述调用全部可用。保实际库/头SHA、原始字段与返回码。

按实际SM shared128KiB，floor(128/64)=floor(128/48)=2，故Vlate单项不支持shared驻留CTA翻倍。regs/thread的粗界仍受分配颗粒/标量寄存器/blocks上限等约束，不能宣称实际occupancy；cache偏好阈值属于另一独立状态。组合二若逻辑上仅加一个16KiB K tile，48+16=64KiB仍在相同粗shared界，但实际lowering资源须重读。属性能排除不可能的机制，不能代替实际时间。当前没有新组合设备结果。


补充actual SDK与只读collector（尚待root返回查询值）：`tmp/current-biv150-sdk-source/ix.h`真实定义IXDRVfunction为struct指针，cuFuncGetAttribute/cuFuncSetCacheConfig经mapping_cudart映到ixdrv*；PREFER_SHARED枚举真实为0x01，函数carveout/maxdynamic属性均有声明，但没有FuncGetCacheConfig，context getter不能替代。MAX_BLOCKS_PER_MULTIPROCESSOR不在该actual enum中，必须保未知。设备属性collector独占同目录`query_biv150_resources.cpp`最终SHA57326c2e1f2298654c3c0fa7fffbe2e5597dc6658775499c1f49262220a72e4b；SDK编译枚举，dlopen actual libcuda仅Init/DeviceGet/19只读属性和主context状态，不建context/分配/stream/sync/Set/kernel。只读函数属性必须同进程真实JIT handle，不能从其他进程传整数。初始生成过度C++转义在CPU准备检查发现并弃用，未编译/设备；最终无该转义层。root唯一owner编译执行，本owner未运行。


124857最新原始回执覆盖前述“待查询”：root编译57326collector并只读执行成功，记录16SM/warp64/32GiB；19属性全rc0、primary context前/后active0，无kernel或分配。raw包`124857-biv150-resource-query`15223bytes，SHA`510c7a4f5d4ca3a155aa9c5551d6c162774844d30764d05fc56358a134859b9b`。当前先按owner回执更新，完整包正在下载，本owner尚未独立读其JSON。async engine=1/concurrent kernels=1是SDK报值，不证明本Attention的global→shared async重叠；L2=16MiB不等于完整cache拓扑；不把时钟/位宽折算成实测带宽或套完整板卡矩阵吞吐。


## 130457组合一真实负结果与组合二单点准备（覆盖上文历史状态）

root唯一owner回执：130457三臂strict正确性全部通过。原版wall11.0918682813/Event10.9864487648ms；A=默认Vlate为11.2275998594/11.1361632347；B=Vlate＋PREFER_SHARED为11.2581162031/11.1335206032。B较原wall慢1.49883%、Event慢1.33867%；仅cache因素B对A的wall慢0.27180%、Event快0.023730%，没有可确认收益，不集成并停止cache点。A/B为独立module/function、同binary58a45…/compilehash e239…/shared49152/regs100；B一次PREFER_SHARED返回rc0、enum1。两者前后max_dynamic131072/static0，carveout返回rc801不支持，原绑定恢复。rc0仅证调用成功，不证偏好实际改变硬件；本owner按owner回执记结果，未运行/冒充独立全原件审计。

root随后授权且只准备组合二：tmp/next-v-late-k-lookahead，policy1919c50be7914d7d77ff81910e84835fa6ab0589f9e9ba677dab3aa0885e7559、gateab9a47874b4234c2f7d9dbd51c98053204a4953685cafcb5a90130915e1ce5c2、generated06ad08f22f275bb696143bbe9fdcd19821d262d01d99f57860e8606863f43644。只在原Vlate上增加一个下一K及页向量carry；首/next/partial/空loop边界精确保原，QK→softmax→accscale→PV数学顺序和3DC2不变，w8/BM128/T64/s1，不叠cache设置。唯一CPU合同首次0.0530856s通过，framework全文静态终审ready；未导入设备框架、未上卡。按root要求同worker数值/资源通过后直接32ABBA，真实IR与资源首次编译时落run/source，不另开compile-only。下一步只由root串行一次，IR未保留新carry/有效顺序或无收益即停，不把hash变化或逻辑16KiB预算当流水/驻留证据。此状态覆盖上文“尚未实现”“当前没有新组合设备结果”等历史描述，组合二仍无GPU结果。
