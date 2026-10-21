# BI-V150 KV 保存恢复：一手资料、实例预算与最短验证边界

2026-10-22，hardware_innovation。归档写锁已由root明确解除。本轮仅CPU本地源码/原件阅读、公开一手资料和独立代码审阅；无SSH/GPU、远端模型导入、共享代码库修改或push。资料截止本轮实际检索，不升级比赛框架。全部实测只属天数BI-V150；C500由队友负责。

## 当前最重要的结论

672MiB字节复制门已证明构造中的搬运和事件依赖可以工作，下一缺口是**真实executor/42层布局，以及保存完成前不复用旧页、恢复完成前不发布有效前缀**。先补这些事实，比继续测复制峰值更有价值。本实例host总限额20GiB，甚至装不下当前全部GPU KV的一份CPU镜像，故只能准备严格有界的少量抢占事务，不能照搬通用大host缓存方案。

## 一手资料实际取得了什么

本轮已找到[天数官方开发者门户](https://developer.iluvatar.com/)和[官方文档中心](https://developer.iluvatar.com/docs?role=%E6%96%B0%E6%89%8B%E5%BC%80%E5%8F%91%E8%80%85)。但针对CoreX pinned copy、stream/event的定向查询没有取得可直接审阅的厂商API正文，门户动态页也未返回该API说明。这是本次公开资料的缺口，不是断言厂商没有文档；不借其他GPU厂商文档补成CoreX硬件保证。

[PyTorch pinned/non_blocking教程](https://docs.pytorch.org/tutorials/intermediate/pinmem_nonblock.html)给出两个直接相关的反例：H2D提交后修改pinned源可破坏结果；D2H提交后立即读CPU结果也不安全。因此host内容、页所有权和完成事件都要保留，`non_blocking=True`只是提交方式。[CUDA Runtime同步行为说明](https://docs.nvidia.com/cuda/archive/13.1.0/cuda-runtime-api/api-sync-behavior.html)还指出Async调用可因内部资源等原因阻塞；它只解释兼容API设计风险，不证明CoreX的具体阻塞原因或复制引擎数量。

[vLLM官方offload文章](https://vllm.ai/blog/2026-01-08-kv-offloading-connector)讨论跨层合并页与异步保存，并明确列出抢占处理和模型计算竞态的修复。其评估是H100/500GB host/8核，不能换算成本站16SM/32GiB/6核的收益。官方[抢占修复PR29870](https://github.com/vllm-project/vllm/pull/29870)尤其说明：被抢占请求的旧store不能照常成功发布，后续重算结果也需重新存储。这里采用其生命周期反例，未合并新分支或切换已有offload后端。

进一步读固定上游v0.24.0的[offload connector worker](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/distributed/kv_transfer/kv_connector/v1/offloading/worker.py)：store延后到下一step，复用以jobs_to_flush约束，load完成才回报finished_recving。其[CPU/GPU handler](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/kv_offload/cpu/gpu_worker.py)在D2H前等待compute，持有stream/event/描述数组，完成后才回收；这是协议参考，不是本机安装文件或native op可用性的证明。

本地还有比设备名更具体的反证：稳定 `vllm_fl/platform.py` SHA `e6f231af2c90f93116ebed7a8a2ce640bcc2d4c31ba5fde2e0fa0cbd8236ea36`（与183543归档逐byte同）81–89明确对iluvatar返回 `is_cuda_alike=False`；而公开v0.24.0 [CPUOffloadingSpec](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/kv_offload/cpu/spec.py)132–136要求CUDA-alike或XPU。两处条件不匹配，不能因为torch设备写cuda就推现成native支持；本轮未取得本机该offload实现，故也不把上游guard直接写成已测安装失败。

[PagedAttention原论文4.5节](https://arxiv.org/html/2309.06180v1#S4.SS5)把swapping与recomputation视为依带宽和计算成本选择的两种恢复方式；共享物理页由引用计数和COW管理。早期策略与今天async scheduler不相同，论文里的选择和吞吐倍数不能替代本机实测。

## 本实例证据与主机预算

actual184108采集 `experiments/source-audits/20261021T184108Z-kv-copy/manifest.json` 报告：PCIe sysfs当前/最大link均16.0GT/s、宽16、NUMA0；20GiB cgroup限额，采集时usage2267643904B。这里只是一次link/usage观测，不证明独占PCIe带宽、copy engine数量、双向并行或服务内存峰值。实际设备仍仅一个16SM、32GiB BI-V150设备；服务持续记录6核quota，不按整板参数推算。

MiniCPM原BF16 KV payload按真实42层、KV heads2、head128计算：

```text
每token = 42层 × 2(K/V) × 2heads × 128 × 2字节 = 43008 B = 42 KiB
每16token逻辑页的全层数据 = 688128 B = 672 KiB
16K token = 704643072 B = 672 MiB
16K+1024out = 748683264 B = 714 MiB
KV521936 token = 22447423488 B = 20.905792236328125 GiB
```

最后一项已大于整个host cgroup20GiB，还没计API、EngineCore、tokenizer、Torch/编译器、输入、pinned缓存与在途传输。官方[通用offload指南](https://docs.vllm.ai/en/latest/features/kv_offloading_usage/)中让CPU tier大于GPU KV pool的建议适用其缓存复用方案；本站既无这一容量，也未测共享prefix命中，不能照抄。latest文档也不是比赛安装版本。

合理的首个协议预算是一个已预留、页对齐且有静态上限的host slot，只保存一个已证明有效的victim前缀，额外请求预算不足即走原recompute。**slot大小要由真实可保存prefix决定，672MiB只是已有16K构造，不擅自认定每次victim正好16K。** reservation应同时计Saved、SavePending、RestorePending及取消后尚未完成的引用；不能提交后先退预算。动态允许值受`limit−current−已测服务余量`约束，余量尚无峰值证据时不按空闲快照填满。不要在抢占热路径临时pin整份KV或复制一份golden；191545的golden/consumer是测试开销，生产协议不能照搬。

191545 normal/packed四个单样本往返wall为222.053105/235.270289/119.956194/120.716930ms，事件与wall差异和CPU节流缺证见[独立计时审计](2026-10-22-kv-page-copy-timing-review.md)。这些数值既不是生产事务的可靠上下界，也不是可直接扣除的重算耗时；此前13758 prefix-gap exposure也不是实际GPU重算量。收益必须来自同真实请求中可避免的工作，减去保存等待、恢复、host管理和调度影响后重新测量。

## actual源码对协议的约束

以下均是本机归档，优先于公网同名版本：

| 原件与切口 | 已确认事实 | 必须保留的约束 |
|---|---|---|
| actual184108 scheduler.py，SHA df780761…，1107–1128 | preempt先调用free，computed归0后重入waiting | 不能在free之后才抓旧页，也不能仅恢复computed标量假造有效缓存 |
| 同文件130–152、2082–2109 | defer_block_free默认False，仅特定connector消费者+多inflight条件启用；完成step fence后才释放 | 当前无connector不能假定已有保护；CPU schedule/optimistic submitted不等GPU写完成 |
| 同文件2355–2404、2422–2449 | finished_recving后cache有效块、再恢复可调度状态；失败截断/重算 | restore提交不是可调度ACK；还要处理取消期间完成的旧load |
| actual184108 kv_connector_model_runner_mixin.py，78–112 | worker绑定本步meta，start_load，之后get_finished/clear | 调度器和worker需明确job/epoch/完成消息通路，不能靠scheduler直接访问假定同进程tensor |
| 同mixin115–158 | 没有kv_transfer_group即不选uniform跨层缓存 | packed门不等实际packed；不为获得packed直接改官方参数或开启现成connector |
| e155 runner 1213–1216 | 原新页zero发生于更新states | 新页需先原zero、再H2D、再允许Attention读；先恢复再zero会擦除数据 |
| actual184108 Core519–635 / uniproc79–106 | async batch队列及Future有原有顺序，静态类不能代表实际executor | 保存等待不能阻塞负责提交/回报ACK的同一通道；不重排/丢弃在途输出 |

PagedAttention共享页使“保存请求所有page”和“能释放这些page”成为两个问题：若有别的引用，保存副本并不会让GPU回收该页。首次事务建议只处理已证明有效、未被后继写覆盖、完整block且所有权明确的页；共享/partial/未知布局先原路，不能破坏别的请求。保存的安全长度必须来自真实完成fence和请求epoch，不直接取乐观num_computed。

## 保存与恢复需要的四条依赖

| 阶段 | 必需的先后关系 | 持有与发布 |
|---|---|---|
| 保存准备 | 真实producer完成/不再写该页 → save stream等待 → D2H → save_done | 旧GPU页、pinned目标、map、event及epoch强引用一直有效 |
| 释放 | worker确认save_done且epoch仍有效 → scheduler确认可释放 | submit返回不释放；取消/失败也先等待在途读完成再回收 |
| 恢复准备 | 原allocator实际分配新页 → runner原zero完成 → restore stream等待 → H2D → restore_done | host源不修改/复用；目标页不交给别的请求，不能借用共享页 |
| 发布 | 真实消费者等待restore_done，worker确认可消费 → scheduler发布有效prefix | 之后才允许跳过计算；全prompt恢复仍保留原最后token/采样语义 |

`record_stream`只能协助allocator知道跨流生命周期，不能代替producer/consumer依赖；Python强引用也不证明GPU完成。首次可串行等待真实event，不先承诺和模型重叠。保存前预算拒绝可直接原recompute；提交后取消/错误需保留资源至完成。恢复尚未发布时才能安全撤回事务；部分发布之后不能静默调用原forward重试。

不更改temperature/top_p、采样行、真实token数或请求排序。少做recompute仍可能改变async discard、batch轨迹与全局RNG消耗，KV bytes相等不能证明整模型逐token等价，必须独立accuracy；SQL+C3的103/105不会自动继承。

## 最短验证次序，不加复制扫描

1. 先只跑一次root批准的隔离descriptor smoke，原模型/服务参数不变。observer不发额外GPU工作，只在WorkerFL原KV初始化成功后和Core首次step前各记录一次CPU元信息。必须实际得到42层、shape/stride/dtype/device/storage offset/别名分组、KV config和executor/worker/runner类；INSTALLED不算观测成功。缺布局、执行通路或host余量即暂停接入，不再用normal/packed假设填空。
2. systems只为一个事务准备CPU状态合同：预算拒绝、save未ACK、取消、ID/epoch复用、恢复未发布/失败、重复ACK。它不能模拟GPU完成，不能把mock ACK当设备事件。
3. 协议接通后，root才考虑一次已发生抢占的原181041长输出配置（16K/32req/1024out/并发64、seed721201，原SERVER）。先只验真实保存→释放→新页zero→恢复→同请求后继消费、字节/epoch/预算和清理；无真实恢复不报收益。128out三端preempt0，不能拿它作恢复机制正验证。已有672MiB四几何门不重跑，不扫host size、线程或stream数。

将来真实事务本身可同时记录copy submit/ACK/host wall、CPU quota及实际内存峰值，校验放窗外并标明其影响；本轮不修改门来追加测量。只有正确且有真实服务信号后再安排新accuracy与必要官方复现。

## descriptor独立终审状态

已全文审初稿3cf13981及builder，随后只加actual worker_base7da443 pin与current_stream明确unobserved；逆去这两行精确重建3cf，没有新GPU API。**历史已审版**runtime `fdf2c812edda098ce42c21915e2b9e912901bf681d02cf59a2bb7a236d559576`、builder `14a206e3416322d24bca9e3f989e071d79ddfcfab310c234325079c260ef03aa`；该回执后已被下述最终版覆盖，不能再按旧pin上传。

**当前最终版**runtime `0c892ad02fbfe663d3f7c8f668cdd000c0c1fc7860ff915db8bce5949cae0667`、builder `936c9260724f97b02dc1e69da2f4f0da7cdfaf7fdcb0e8ab866c26d9c028c59e`，派生init仍 `90fe0b381fd53ec5273c623d91b806a0fc21f5b84165beba0b015a1e07d53e74`。新增的唯一runtime delta把cross_layers字段分成缺attr→unobserved、实际None→observed_none、Tensor→原descriptor；内存逆换该块精确回fdf2，未改hook或GPU读取。此项是保守观测补强：**exact e155的587–588已初始化cross_layers及backend为None，不能称已证实normal分支缺字段**。root在新pin重审前hold旧版，未混用原件。

Core actual27b在110加载general plugin，221才绑定step_fn，故类方法wrapper时序成立；WorkerFL initialize_from_config原调用成功返回后观察，原异常先透传。默认install(False)不导入框架，只新隔离init显式True且需本次目录；只plain Tensor元信息，无值访问、GPU同步、current_stream查询、RPC或调度修改，内部storage pointer仅用于本PID别名键不输出。独立读过owner CPU合同和213→215完整copy证据，未重跑suite；缺字段/写失败仅诊断原路，不当布局通过。

root launcher `scripts/remote/launch_kv_runtime_descriptor.sh` SHA `78414492a1b053b1c88ce1f9e461bd66b0b053da33009f2cdb362a40fcab4a84` 也已全文只读审：pin0c89/936c/helper0ecf/driverbc51/snapshot0f2a，双栈/68,0预检、原driver锁、正确positional run_dir、原smoke-only/seed721201、全新source/control及DBbefore均合理。只记录本次env目录，INSTALLED仍只是预检，封存后需worker42和core两个实际JSON。该代码终审时尚无实际结果；**随后195012原件已到本地，由framework负责完整独立验收，root已回执normal42成立**。本owner不重复布局审计，只取两份cgroup记录用于下一节预算，不能把CPU合同当该实际观测的来源。

## 单victim CPU事务互审边界

另已只读审systems `biv150_kv_transaction.py` 当前 `aeea9ff44274f6b0a982861e3d14dcb3100ccaa64ea230184dba79b3cf52f791` 与必要合同 `49753260c91151c3e9bc9323f45a699935adbc0117ef5cb85a71ea8357b28ae7`，未重跑。Key含session/request/incarnation/attempt，slot全生命周期op serial抵御误用同Key的旧ACK；完整Operation等值、真实completed后才settle，cancel/失败仍保在途资源，ZERO→RESTORE→publish及发布后禁私有rollback的CPU边界清楚。

新增pure-CPU fresh-zero split逆移后精确回前版2656。实际scheduler先给running分配新页，后处理waiting，最后1047才drain全zero集合；因此helper只允许原before顺序不变、本事务独占dest是after尾段，返回保留段和owned段，真实zero ACK后才应用，避免消耗别的running页或稍后再zero已恢复页。尚无任何allocator/RPC/安装入口或服务接入。

CPU接口无当前阻断不等于GPU协议成立。未来适配器仍必须保证SAVE ACK的producer fence覆盖**所有将整体free旧页的在途写**，不能仅证明保存前缀bytes完成；原frame正常处理、实际free成功后再commit。slot serial若重建需新session身份，不能同session/Key重置后假称旧ACK安全。这些接入事实由真实descriptor/协议适配决定，本轮不代填或扩大实现。

## 195012之后可直接采用的单victim预算护栏

root要求评估1GiB静态cap，并明确这只是运行时资源预算，不修改比赛服务参数。两份实际descriptor的cgroup字段为：worker阶段usage4373532672B、Core首次step前usage4636340224B、limit21474836480B、quota600000/period100000。该时刻余量充分，但都是启动快照，不是长输出host峰值；不能由此宣称OOM永远不会发生。

初版可使用以下固定、非扫描规则：

1. `PAYLOAD_CAP=1GiB`，只有一个HostSlot和一个在途事务。cap只计pinned KV payload，不能把CPU描述对象/其它服务内存也说成被此cap硬性限制。按每页688128B，最多1560完整页/24960token，尚有262144B余数，不跨页凑满1GiB。
2. **当前接口先按真实issued、全部queued SchedulerOutput scheduled数、known IDs与实际页求R，再检查 `B=R*43008 <= cap`，超cap直接原recompute。** 不为适应cap伪造issued或改真实token数。目标16K+1024out最多714MiB，本次不需要新增截断R的通用API；partial cache选择以后若需要必须显式记录，而非在输入证据中暗改。
3. 动态拒绝条件用实际cgroup的limit−current；首次可把额外headroom guard也固定为1GiB，lazy分配前需余量≥B+guard，分配后再确认余量≥guard。预分配pool已经计入current时不重复扣减。读失败、slot已占、余量不足或CPU分配失败，在copy submit前回原路；该1GiB guard是保守实验拒绝阈值，**不是测得的峰值或生产OOM保证**，不搜索其最佳值。
4. save/restore pending及取消后未ACK期间始终占slot和payload预算，不因CPU请求已结束就提前释放；无额外golden或全GPU镜像。allocator、pinned分配及ACK归属由实际adapter处理，状态机不冒充物理内存已经分配。

normal42已证实后，c95f自行实现的narrow.copy_路径已有191545 GPU字节证据；上游native平台guard不匹配**不能反过来否定该独立实现**。现在应助审实际adapter的producer/zero/free/publish边界，下一步不是再扫布局或现成offload参数。所有建议仅内部cache事务护栏，原模型、输入/输出、位置、采样、官方SERVER与benchmark脚本保持原样。

## 实际 FullAttention 清零语义纠正及协议代码互审

本节覆盖前文关于“本模型会原生清零新页”以及 aeea 接口尚未接入的历史描述，不改历史原件。actual `kv_cache_interface.py` SHA `7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003` 的 `needs_kv_cache_zeroing` 仅返回 `has_mamba_layers`。MiniCPM 当前单 FullAttention 组为 False；df780 的1046–1049不调用 `take_new_block_ids()`，e155 的1215仅在输出字段非空时执行 `_zero_block_ids`，源码存在这个分支并不证明此模型会进入。新恢复页必须由本项目 worker 显式清零并等待真实完成，不能借用未执行的原分支作围栏。

只读完整审阅的本轮版本为：

| 文件 | SHA256 | 本次审阅边界 |
|---|---|---|
| `patches/framework/biv150_kv_worker.py` | `31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf` | 实际 normal42 页复制、清零、事件 ACK、强引用与可选回读 |
| `patches/framework/biv150_kv_protocol.py` | `50375e899acbdcee15d3cdec2ecd77875fb355c56ccbfa663271509982ddc19a` | 原调度切口、私有分配、取消/回滚与 cached-resume 发布 |
| `patches/framework/biv150_kv_transaction.py` | `616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13` | 事务 epoch/serial、未发布回滚、历史页号可复用的尾段证明 |

worker 只经显式 RPC 启用，无默认安装或顶层框架导入。严格锁 a8de/e155/7da/c95f 和已观测的 BI-V150 16SM normal42 连续 BF16 布局；不适配 packed/shared、其它模型或另一平台。SAVE 在整个 device 已提交工作完成后才读旧页，围栏覆盖原抢占整体释放页的所有已提交 writer，不只覆盖保存的前缀。UniProc 的 `non_block` 源码实际先执行 `run_method` 才包装 future，因此本范围中不另有后台 Python worker 在 fence 后继续提交旧 writer；此结论不可外推 MP/Ray。

slot 保持 raw KV、pinned host、核验 buffer 和 event 的强引用。ZERO 只清本事务私有目的 raw 页；RESTORE 必须是同一目标映射。每阶段 event record/synchronize 真正完成才返回 completed ACK；异常尝试 device settle，无法证明完成就保持引用并返回 completed=False，adapter fail closed，不释放或发布。旧 epoch/陈旧 serial 不污染现 slot；DROP 支持 nbytes0/pages[]，检查 owner、epoch 和 settled 后才放 host。

诊断环境 `BIV150_KV_VERIFY_RESTORE=1` 额外 pin 单层 buffer，首个成功 RESTORE 对42层目的页逐层 D2H、event 同步、CPU uint8 全字节比较后才 ACK。单层 buffer 重用，非整池 golden；1GiB payload cap 外另计它及1GiB动态 guard。核验失败不发布；默认未启用且不读取 KV 值。`_VERIFIED_ONCE` 只说明本进程首次成功恢复经过此核验，不代表后续每次都核验。

adapter default-off，只在隔离 init 追加安装；exact 源码 guard 后内存编译原 schedule 的唯一 waiting 切口，不写 installed 文件。原 SAVE ACK 后仍只执行一次原 `_preempt_request`；旧队列输出按原 FIFO/update 成功后才消费相应 frame 身份。恢复分配使用实际 external-computed R、delay_cache_blocks、单组 ref1/unhashed 私有页及本次追加尾段证明，不 take/drain 或修改历史 `new_block_ids`。ZERO→RESTORE 真 ACK 后暂设 R，原 schedule 若未发出该请求工作则原 free 并回滚0；有实际新 payload 才转换为原 cached-resume、发布并 DROP。发布后的页回归原 scheduler 所有权，不再当私有页回滚。

历史592d已额外保留完整 command/worker response JSON（含核验和内存字段）；原 e155 `_update_states` 返回后、Attention 前核同一 cached-state/generator 对象、输出 token、完整块替换与 CPU computed R，随后原 FIFO 输出处理也有标记。最终50375仅把 `scheduler_reserve_full_isl is True` 改为必须是 Python bool；实际字节逆换唯一一行，SHA精确回592d。恢复分配仍原样传真实 bool，False 时后继原分配无work有未发布回滚，不依赖硬True。由此避免未知实际配置导致静默未命中，未改资源预留行为。

以上为诊断证据，既不读取 generator 状态，也不证明全局 RNG 到各请求的抽样分配等价。补丁本身无采样/RNG调用、无新排序或比赛参数变化；准确率与真实恢复仍必须实测。已只读owner `analysis/source/kv-transaction/adapter-cpu-check.json`（实际f281 DTO、V2→cached完整字段/原切口逆回/默认关闭、pins50375/616）及 `analysis/source/kv-worker/cpu-contract.json`（pins31cc，header/预算/DROP/异epoch/无框架导入）。本 owner 未重跑 CPU suite、未运行设备，当前只读代码未见阻断最短诊断服务的问题，不能写成 GPU 协议已通过；root负责唯一设备context-long+VERIFY1门及完整原件。

## 后续小候选：未消费的历史页号记账（仅排队）

按 root 指示，仅查消费者与上界，不改默认、不新增设备门，也不打断当前 KV 协议。搜索范围是已取回 actual `experiments/source-audits`、`analysis/source` 与本地 plugin 的 Python 源；它们不是完整远端 vLLM 仓库，不能声称穷尽未取回的外部模块或反射访问。

已确认同一历史列表的链路为：

1. actual22e `SingleTypeKVCacheManager.__init__:75` 建 `self.new_block_ids=[]`；外部已计算页分配276、普通新页分配309对 FullAttention 等 exact spec 追加实际 `b.block_id`。
2. 同文件312–316 `take_new_block_ids` 返回原列表并换成空列表。383–410的 pop/free 只管理 request 块与池；535–537默认 `new_step_starts` 不做事。没有随请求释放删除历史页号。
3. actual2e91 `KVCacheManager.take_new_block_ids:605–610` 汇总各 single manager；`reset_prefix_cache` 只重置 block pool/cache stats，也不清历史列表。
4. actualdf780 `schedule:1046–1049` 是本地已归档原实现中唯一实际调用者，受 `needs_kv_cache_zeroing` 控制；当前 False 不 drain。实际7e3c接口决定该条件。
5. e155/上游 runner、`CachedRequestData`、connector utils 的同名 `new_block_ids` 是每请求调度 payload；`new_block_ids_to_zero` 又是另一个输出字段。不能因名字相同把它们算成 manager 历史列表消费者。当前新协议会读历史列表建立本次追加尾段证明，这是新增消费者，不是原服务已消费的证据。

因此列表长度随累计真实分配次数 A 增长，没有“最多物理池32621项”的上界：同一物理页释放后重用仍再次追加；一组跨42层，只记一次，不乘42。无重算/无新协议、每请求页只分配一次时，32请求×(16K+128out)的条件估计为 `32×ceil(16512/16)=33024` 项，另需加 smoke/warmup；不是对任何 run 实际列表长度的观测。多轮服务、抢占重算和协议私有分配会继续增加；有限任务可按各次分配事件求和，长期服务则无请求数无关的固定上限。

追加的是已有 KVCacheBlock 的 Python int 引用，不是每次额外构造 int。64位进程中仅槽位约 `8A` 字节，再加 Python list 对象/容量预留，33024项槽位约258KiB；未测 RSS/容量，不按“每项36字节”或宿主泄漏速率夸大。普通 extend 的累计 host 工作为 O(A)；当前协议 `tuple(before)` 及完整前缀证明还会在少数恢复尝试读 O(A) 历史，必须与原实现成本区分。

值得保留的后续方向是 exact needs-zero=False、已确认无其它消费者时关闭或分段控制这份未使用记账；尚未选择实现。不能当前直接 clear：本轮协议正依赖追加尾段审计，未知外部消费者未穷尽。下一轮若授权，只先补真实列表长度/累计分配及 host 成本的稀疏证据，再作一个范围严格、可原路回退的小候选并由 root 上卡。当前未实现、未测收益、未改源码；小收益也保留。

## 200957首次真实 SAVE：预算可用，碎片成本尚未知

原件 `experiments/framework/20261021T200957Z-kv-protocol-context16k-long{,-control}` 已本地。此处只做本 owner 的保存输入/预算/碎片专项审计；完整 official/DB/source/退出验收仍归 root 和 framework。实际 control 中 worker31cc、protocol50375、transaction616、copyc95f 与本节审过的固定 SHA 全同；独立 JSON 为 `analysis/source/kv-transaction/200957-save-hardware-review.json`，保留 server.log SHA `5a532c9f2129a7cc8c9cfacf1d891c4524196a254cb2c8266065ac7f822254f1`、原行号及计算。

SAVE 指令1044个唯一正物理页，prefix16704token，逐层页16384B，合42层 `1044×42×16384=718405632B=685.125MiB`。worker ACK 的 submitted/transferred/nbytes 全相同，successful/completed=True、host_held=True；随后原 SAVE_ACK_FREE、DROP completed/successful=True、host_held=False。整个日志没有 ZERO、RESTORE、RESUME_PUBLISHED 或恢复字节回读；VERIFY requested=True只证明为未来恢复预留核验，不是核验通过。restore_skips1没有具体分支 reason，**本轮不能确定为何 DROP**。

按原逻辑次序独立重建连续段，恰24段：前四段37/757/126/104页，共1024页；余20段各1页，尾部物理页号相邻差31。不能仅从差31推断分配交错原因，未记录那一分配轨迹。c95f不排序，只合并源/目的同时连续的页；实际 normal42 的 `42×24=1008` 次 copy 与真实 ACK 完全相等。逐页拷贝本需43848次，合段已减少43.5倍，说明此实现确实消除了大量 Python/传输发起工作。

但20个尾页仅13.125MiB，占payload1.9157%，却贡献840次、占调用83.3333%；前1024页672MiB只用168次。实际输入比旧构造8段更碎，且本次总payload是685.125MiB，不能把191545连续/8段672MiB单样本直接套成当前成本。此事实支持以后研究“保留哪一段已完成前缀”的成本选择，**不等于现在增加一个packing kernel或改变块大小**；当前最优先仍是完成真实恢复链路。

预算也逐项相符：payload cap1GiB尚余355336192B=338.875MiB；单层额外核验buffer17104896B=16.3125MiB，两者701.4375MiB。分配前需 `payload+verify+1GiBguard=1809252352B`，真实余量15878356992B；pin后真实余量14429618176B仍大于1GiB。此次预算护栏允许 SAVE 有实际依据，不是按20GiB填满CPU镜像。

分配前cgroup usage5596479488B、pin后7045218304B，差1448738816B=1381.625MiB；比显式payload+verify多713228288B=680.1875MiB。它是整个cgroup两个离散快照，可能含其它分配/驻留/计账变化，本轮没有分解，不归因给 pinned 分配，不报生产峰值或固定额外开销。没有 RPC 独立 wall/event、producer wait、pin 分配或各 copy 提交计时，日志 ACK 无可作这类分解的时间戳；完整服务221.1178005039692秒、32/0、32768输出仅作上下文，不能据此扣出copy成本或恢复收益。root负责唯一GPU后继门，本 owner不重跑微测。

## 后继暂态保留修复的定向终审

systems 后继 protocol `a1b691f52f3724b95bbcb11f5702611a17103161001bb929096c71ab4fa74751` 已独立只读审；实际旧文件 `analysis/source/kv-transaction/biv150_kv_protocol.50375.py` SHA精确50375，200957受测源不覆盖。新稿只调整暂态保留/释放及单次诊断，worker31cc、transaction616、init footer不变，未混入 [前缀选择设计](2026-10-22-kv-fragment-aware-prefix-plan.md)。

pending frame、placeholder、token budget 或恢复 allocation 返回 None 时，只保留原 HOST_RESIDENT 与 slot，仍继续原 FCFS waiting/普通准入；不 park、不排队重排、不提前消费 future。若本次原 SchedulerOutput 确实发出该 rid 的普通 work（scheduled tokens >0），才丢 host；不根据状态名 RUNNING 猜本次已准入。identity、terminal、epoch、状态或 digest 真失效则丢弃；实际 DROP 仍须 worker settled ACK，失败保守退出。首个 RESTORE_DEFERRED 记录 reason/pending/placeholder/budget/free 等，明确未观测 allocator required blocks，不把 free 数量当分配必然成功证据。

已读 owner 唯一新增 `tests/test_biv150_kv_protocol_defer.py`：CPU假对象验证暂态保留、原 FIFO update 后 frame 清除、无 work 持有、有 work DROP及失效释放；未模拟GPU完成。本人没有重跑测试或设备。未见该增量阻断下一最短真实服务门的问题；200957缺 reason 的 DROP 仍保持未知，不能用新代码推定旧分支。新版本尚无本人收到的设备原件，恢复/准确率/收益结论仍未成立。
