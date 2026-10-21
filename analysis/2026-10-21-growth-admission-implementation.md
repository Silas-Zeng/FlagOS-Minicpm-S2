# 输出增长准入候选：最小实现与交接

2026-10-21。root 本轮明确授权 CPU-only 独立实现；没有改变正在运行的080656源码、正式driver、benchmark、启动参数或设备任务。GPU仍仅root使用。

## 从证据到切口

root于UTC10:17:06记录正式16K已进入第2/4，首轮128成功0失败、816.56s/2728.78 total tok/s；一次metrics累计preemptions=6、KV97.6885%、waiting34，远端保存在official092944/observations/20261021T101706Z。这不是最终或分档精确抢占计数，也不证明每次都重算全部16K。它支持准备一个可短测的准入候选，不支持提前宣布收益。

本机安装源码已只读取回 `analysis/source/growth-admission/`，先前“公开同版但实际未核对”的边界已消除：

| 实际源文件 | SHA256 |
|---|---|
| scheduler.py | df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090 |
| kv_cache_manager.py | 2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320 |
| block_pool.py | 3fc5dfe0ab7ccc6206f6eb7886b2aad15384f92708e6b9f7e5ec7838b7379abe |
| kv_cache_coordinator.py | 9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b |
| single_type_kv_cache_manager.py | 22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914 |

`Scheduler.schedule` :874–897 的waiting allocation已把完整prefix hits传给manager；返回None后原循环break而不pop候选，因此可以无重排地延缓FCFS队首。`KVCacheCoordinator.get_num_blocks_to_allocate`和SingleType实际方法已正确处理：已有/预分配页相减、活共享prefix不重复占free、ref_cnt0但即将被touch的cached页从free扣除。无需自己扫描pool或复制页数公式。

## 已实现的内容

候选模块为 `patches/framework/biv150_growth_admission.py`，SHA256 **9245dd089a310620840a1c056544e66fb2dd0ea24f41ef8f0e4b22721bac7e49**。

- 默认关闭：导入模块及`install()`均不import vLLM、不安装；只有显式代码`install(enabled=True)`在Iluvatar安装。五实际源完整hash、原函数/别名身份守卫；未知源拒绝安装。与其他schedule/allocate wrapper叠加时拒绝，防止混淆。
- 只包装Scheduler.schedule的ContextVar作用域和KVCacheManager.allocate_slots。scope严格限实际MiniCPM目录、BF16/2048/42层/16Q/2KV、单组FullAttentionSpec/16block/head128、UnitaryCoordinator/FullAttentionManager、FCFS、单TP/PP/DP/DCP/PCP，无spec/LoRA/ubatching/sharedKV/connector/MM/structured/streaming-resumable/V2。
- 只读真实running列表及actual pool free，每次重算，不保存请求ID reservation ledger。每个请求终点为合法`prompt+Request.max_tokens`，与已调度异步placeholder/computed范围取最大，再裁到原max_model_len。不改请求max_tokens、tokens、computed或KV。
- 对所有running和本次waiting candidate分别调用实际predictor，`apply_admission_cap=False`，明确不让回收型cap截断未来长度；已有分配/预分配页自然相减，前缀触碰成本计入。汇总尚需free页与原watermark，超出真实free则仅returnNone，原waiting loop break，running分配仍完全原路径。
- empty-running直接原路径，保证有限running集合排空后队首可以尝试准入；超长单请求未来容量不可能容纳、非审计请求/分配状态也回原。完成/取消/抢占只用原机制，下一次live running/free会自然反映释放，无旧ID预留残留。
- 首次真实defer输出`BIV150_GROWTH_ADMISSION_FIRST_DEFERRED`；安装有INSTALLED。`stats()`为CPU进程内只读副本，包含checked/deferred/fallback分类。不输出请求内容或逐步大量日志。

**安装位置很重要：** 必须在EngineCore创建scheduler前显式安装（例如隔离候选插件scheduler模块的受控入口）；只在GPU worker的model_runner footer导入不会覆盖另一进程的scheduler。本文没有给冻结目录加footer或开关，集成由root在独立新source中进行并交叉审查。

## 最必要CPU合同

`tests/test_biv150_growth_admission.py` SHA256 **da154cbf431257ab3350f4f935b11da5fb32f9965c332f37f986f6f8df0b9122**。不导入torch/vLLM、不建调度模拟框架；AST只提取上述实际SingleType/coordinator的原计算方法，保留它们的执行公式。

```text
python -m unittest tests/test_biv150_growth_admission.py -v
7 tests OK（最近0.034s；只是本机CPU合同）
```

七项覆盖默认关闭/5源hash、future容量精确边界及原调用透传、free prefix touch与live shared prefix、完成取消/ID复用/已预分配页、empty/超长/不支持状态/running原路、async placeholder/max-model边界及异常后的ContextVar reset。没有服务或accuracy通过声明。新增hook合同检查原init只append、语法、拒重复transform、actual方法安装两次不嵌套。根节点仍需跨owner代码审查，随后按现有设备队列串行上卡。

## 保留的风险与最短下一步

这是容量保护策略，不保证收益。完整未来输出预算可能使16K常驻从31降至29，降低decode批量并增加TTFT；空running/超长/unsupported fallback继续承受原重计算风险。它不改变采样代码或RNG状态，但改变批次成员与执行时机可能改变无独立seed时的随机数分配/数值，因此必须独立accuracy，不能声称请求输出逐字不变或继承C3通过。

按root安排完成当前官方和original baseline后，在新隔离source以原SERVER、同seed/DB/KV运行一次16K/1024/32req最短pair；确认真实EngineCore安装/defer marker、32成功/零错误、tokens与TTFT/总耗时、实际preemptions和DB变化。若无信号或TTFT明显恶化，记录负面停止；不先重跑大accuracy/官方吞吐。若收益值得保留，再独立准确率与原官方四轮。不能并发第二个设备任务。


## 显式general-plugin接入变换器

`patches/framework/biv150_growth_admission_source.py` SHA **b0d5516684e4092dd643836c7bf43ffcd3681d855a32033d6745f13fda0cb709**。输入是exact冻结080656的`vllm_fl/__init__.py`（SHA e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff），纯bytes在EOF的`register_model()`函数末尾追加4空格import及`install(enabled=True)`，不改platform `register()`，不改runner或retained三个runtime；拒绝不认识或已变换source。仅提供transform_source接口，未写入任何冻结源或自动启用。

实际归档pyproject的general entry是`fl=vllm_fl:register_model`；其原`register_quant_linear()`已在新增hook前解析current_platform，避开platform注册期的循环。公开固定版[vLLM插件加载器](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/plugins/__init__.py#L62)在调用general hooks前置plugins_loaded=True；[EngineCore](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/engine/core.py#L102)在构造scheduler前加载general插件。它们支持root选定的接入时机；本轮没有把公开loader/core冒充新增实际hash证据，真实新source启动仍需EngineCore首次CHECKED marker证明。runtime重复install识别两包装marker并原样返回，单边安装拒绝，原method源码/alias guard保持。

为了区分“安装成功”和“策略确实执行”，首次有效预算计算打印`BIV150_GROWTH_ADMISSION_FIRST_CHECKED pid=... free_blocks=... future_blocks=...`，每进程仅一次；首次defer另外一次，无逐步日志、计时或profiling。

同一冻结init只在内存变换后的SHA为 **d9e2caf40f8d126ec4344b6c98605847f9b4be438eb9961a2eb3bb0f40671ef9**，供root隔离组装复核，没有改源文件。

## 独立交叉审查完成

framework_innovation已独立读取runtime9245、transformer b0d5、tests da15和actual scheduler/sizing/coordinator，复跑7合同0.030s全过；未见阻断最短服务试验的问题。它核实同轮新准入在下一waiting allocation前已append且statusRUNNING，future预算会包含新请求；predictor/ref0 prefix/FCFS break/empty排空/ContextVar reset/重复安装均吻合。尚缺actual async_scheduler和core loader的本地源码核对；真服务阶段必须根据FIRST_CHECKED的PID确认EngineCore实际进入scope，不能只看泛化INSTALLED。跨owner通过不等于设备或accuracy通过。


## 实际AsyncScheduler继承已核对

新增实际只读源 `analysis/source/growth-admission/async_scheduler.py`，SHA **da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884**；作者与framework reviewer均完整读过。AsyncScheduler仅改init、update_after_schedule、update_request_with_output，没有schedule override；actual AsyncSchedulerFL也没有schedule override，因此base Scheduler.schedule包装会被继承，前节关于actual async未审的限制解除。尚需真实EngineCore FIRST_CHECKED证明实际启用；不新增测试/改runtime。
