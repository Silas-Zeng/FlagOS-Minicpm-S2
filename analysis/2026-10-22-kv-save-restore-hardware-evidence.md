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

root launcher `scripts/remote/launch_kv_runtime_descriptor.sh` SHA `78414492a1b053b1c88ce1f9e461bd66b0b053da33009f2cdb362a40fcab4a84` 也已全文只读审：pin0c89/936c/helper0ecf/driverbc51/snapshot0f2a，双栈/68,0预检、原driver锁、正确positional run_dir、原smoke-only/seed721201、全新source/control及DBbefore均合理。只记录本次env目录，INSTALLED仍只是预检，封存后需worker42和core两个实际JSON。最终已通知root可排最短观察，**本轮尚未收到实际descriptor结果**，不能写真实normal/packed/executor结论。

## 单victim CPU事务互审边界

另已只读审systems `biv150_kv_transaction.py` 当前 `aeea9ff44274f6b0a982861e3d14dcb3100ccaa64ea230184dba79b3cf52f791` 与必要合同 `49753260c91151c3e9bc9323f45a699935adbc0117ef5cb85a71ea8357b28ae7`，未重跑。Key含session/request/incarnation/attempt，slot全生命周期op serial抵御误用同Key的旧ACK；完整Operation等值、真实completed后才settle，cancel/失败仍保在途资源，ZERO→RESTORE→publish及发布后禁私有rollback的CPU边界清楚。

新增pure-CPU fresh-zero split逆移后精确回前版2656。实际scheduler先给running分配新页，后处理waiting，最后1047才drain全zero集合；因此helper只允许原before顺序不变、本事务独占dest是after尾段，返回保留段和owned段，真实zero ACK后才应用，避免消耗别的running页或稍后再zero已恢复页。尚无任何allocator/RPC/安装入口或服务接入。

CPU接口无当前阻断不等于GPU协议成立。未来适配器仍必须保证SAVE ACK的producer fence覆盖**所有将整体free旧页的在途写**，不能仅证明保存前缀bytes完成；原frame正常处理、实际free成功后再commit。slot serial若重建需新session身份，不能同session/Key重置后假称旧ACK安全。这些接入事实由真实descriptor/协议适配决定，本轮不代填或扩大实现。
