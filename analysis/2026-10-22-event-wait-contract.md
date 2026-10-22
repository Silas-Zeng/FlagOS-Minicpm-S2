# 实际Event等待契约：generic/typed与Corex缓存分支

2026-10-22，仅天数BI-V150。结论是**目前不能把`torch.Event()`换为`torch.cuda.Event(blocking=True)`当成已证有效或值得先上卡的优化**。实际头文件存在Corex专用Event缓存分支，acquire只传timing；两份Python绑定cpp缺失。旧caller证据也反对仅凭6CPU就优先改输入准备事件。本报告只读源解释，没有候选实现/测试/SSH/GPU。

## 精确原件与已经证明的链

root纯CPU取证 `experiments/source-audits/20261022T044741Z-event-wait-contract/result.json`，本地完整SHA **41ba9a3bcc40ef826ac9fa350be134aa66a86a4e3cab4aa5c9234624c3bfe5eb** 已核。status为`read_only_collection_not_semantic_pass`，没有Torch导入、库加载或设备调用。关键文件：

| 层 | 实际文件/指纹 | 可确认契约 |
|---|---|---|
| typed Python | torch/cuda/streams.py `c8cb35dc…` | `Event`继承`_CudaEventBase`，构造器把blocking等参数传super；synchronize调用super |
| generic binding头 | torch/csrc/Event.h `65a898ae…` | THPEvent持c10::Event；不能从头推Python参数怎样映射 |
| typed binding头 | torch/csrc/cuda/Event.h `28b6ba6e…` | THCPEvent含ATen CUDAEvent；与generic不是同一内部对象 |
| generic后端 | CUDAGuardImpl.h `6a3ed3bf…`、InlineEvent.h `a121d49f…` | PYTORCH_DEFAULT→DisableTiming；BACKEND_DEFAULT→Default；record和synchronize交后端 |
| typed后端 | ATen/cuda/CUDAEvent.h `abfeb895…` | 非缓存createEvent用flags_；synchronize调用cudaEventSynchronize |
| Corex | driver_types.h `93c8f434…`、mapping_cudart.h `ca962a4e…`、ix_runtime_api.h `7dca9b91…` | BlockingSync=0x01、DisableTiming=0x02，CUDA名映射IX，声明ixEventSynchronize |

generic InlineEvent的flag默认PYTORCH_DEFAULT。其CUDA createEvent switch只显示两种flag映射，没有显示BlockingSync位；typed Python虽然接受blocking，但安装包缺`torch/csrc/Event.cpp`和`torch/csrc/cuda/Event.cpp`，**尚不能闭合Python参数→实际flags的绑定链**。不能拿另一个上游版本补成本实例事实。Corex声明/宏/位值也不证明真实CPU会睡眠、不会自旋或有性能收益。

## 决定性的缓存反证与补件边界

实际CUDAEvent.h 145–150：在`__ILUVATAR__`且event cache启用、非IPC时，先根据DisableTiming位算timing，再`event_cache_->acquire(timing)`，没有传blocking。非缓存createEvent才向SDK传flags_。generic GuardImpl 203–216同样在缓存分支仅`acquire(timing)`，否则才createEvent。

root补件已到 `experiments/source-audits/20261022T044741Z-event-wait-contract/cache-supplement.json`，SHA **e55d45a4a9a61358f06e36bcd5e92ed0e3c955355b47a3171a7d416619fc4fc2**。其中实际CUDAEventCache.h **630a80220f0156f5140dcaf4bf59f67cffcc3d400f3e3eb3fdf2fbbed8f50e55** 只声明`acquire(bool timing)`并注释true=Default、false=DisableTiming，内部仅两个deque；没有blocking缓存键。`isCudaEventCacheEnabled`只有声明，对应CUDAEventCache.cpp也缺失。

因此即使typed绑定正确设置BlockingSync，**缓存分支也可能未保留该位**。补件不能证明运行时是否开启缓存或具体创建/等待实现；仍不把“可能睡眠”写成“会睡眠”。是否默认开启、实际编译分支、wheel与源码是否吻合需保未知。不能为绕开缓存随意开启IPC、禁全局缓存或替换已经record的event；这些会引入额外语义/性能变量。

## e155的三个构造点不能混算

源为固定e155：`experiments/framework/20261021T214400Z-kv-full-restore-context16k-long-control/plugin-source/vllm_fl/worker/model_runner.py`，完整SHA **e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1**。

- **314**属于生成输出`AsyncGPUModelRunnerOutput`。独立copy stream先wait当前compute流，提交sampled IDs及可选logprobs/expert D2H，340 record；**348** `get_output`先synchronize，再释放GPU强引用及读CPU列表。该等待包含其前面的compute/copy依赖，不能把整段时间等同可删除的CPU自旋。
- **435**属于`AsyncGPUPoolingModelRunnerOutput`，不是本模型正常token生成的证据；455是对应pooling消费同步。不能因构造长得一样就扩大修改范围。
- **758**是持久`prepare_inputs_event`。3832在复用CPU准备buffer前同步、3836 finally record；4164包围原_update_states/prepare。这里保护跨步异步H2D读取，不能删同步、改record顺序或靠全device sync掩盖竞态。

## 现有caller证据的性能边界

hardware已独立解析旧 `experiments/profiles/20261021T061506Z-host-gap/host-window.pstats`（SHA **f4902a604f0a5813e4c1148d3e16534ec3afa0951010d67c7b83a7c42a67dd62**），本owner只读其交接与原源位置，不重跑pstats/套件：输入准备8次Event.synchronize共 **64.628微秒**，其余8次`get_output`共 **157.091821毫秒**。不能将后者错算到758，CM generator的进出次数也不等于独立步数。

该旧窗口整runner为dfd532…，输入准备方法与e155相同，但窗口受旧SQL长CPU间隔主导；所以既不能证明当前prep绝对没有机会，也不能从6CPU规格推定有大机会。pstats C方法时间不区分CPU忙等/睡眠或GPU尚未完成。即使输出等待157ms属实，blocking最多可能改变CPU等待方式，不能让未完成的compute提前完成；它未必减少wall，唤醒也可能更慢。

## 下一最短必要门，而非现在自动上卡

补件后仍未证明缓存/绑定兑现blocking。758不应仅因上游PR/CPU规格就优先上服务；314的较大旧等待预算也不自动授权改输出。用户随后要求合理使用空闲卡，root据此已授权**独立三route短门**直接比较实际行为，先不改服务/758：hardware写worker、systems写outer，本owner只跨审。此授权覆盖“尚不自动上卡”的等待状态，不表示参数契约或收益已证。

只有root判断契约和实际预算足够时，才在独立e155源上针对**一个构造点**比较generic原路与确能传达BlockingSync的device事件，保持实际current/copy stream依赖和原消费方法。最短门需覆盖：事件尚pending时等待；sampled IDs及可选CPU输出逐位一致；GPU tensor引用直到完成；跨两步buffer安全；原异常/返回。禁先全device sync使事件已完成，也不在record后换event。采同工作量短镜像窗，等待线程CPU/进程CPU/wall分开、v1cpu.stat在窗外；CPU降低但wall回退或依赖错即停止，不自动服务长pair/大官方。此处仅条件计划，**没有实现或执行**。
