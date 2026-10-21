# 首次RUNNING分配失败CPU快照：独立实现与诊断交接

只用于天数BI-V150、原MiniCPM5-2B/SQL+C3稳定080656。默认关闭；只观察一次，不实现victim选择，不叠capacity/FULL/6a，不改变原serve/bench。root的A2/B2使用各自冻结资产，本模块没有进入它们。

## 最终文件与指纹

| 文件 | SHA256 |
|---|---|
| patches/framework/biv150_preemption_snapshot.py | c6b3baa96db494e7c22d8c7a3f02980d06d3469c491bf850e9ebac77675204f6 |
| scripts/remote/prepare_preemption_snapshot_source.py | ce4e9773900316c1c19c70acc2dfba5822da08bbdc9e32fa5945b76ab3a666ac |
| scripts/remote/launch_preemption_snapshot.py | 6ec5d60bf606b8f6c9cee19a1dbce52517b086c65a4d89ad58bf55b37da10812 |
| tests/test_biv150_preemption_snapshot.py | 014a9f6bd55609791386743ec39371b70dbdfd4fbeb255c1ca752b16751d8f5f |

源/合同/反向证明与globals首次核查在历史 [`cpu-check.json`](source/preemption-snapshot/cpu-check.json)，SHA b172c5a1a52f78bed47b31f5a232c5f4917d9399bac5e6ee485993597893e771；后继延迟安装记录 [`late-arm-check.json`](source/preemption-snapshot/late-arm-check.json)，SHA c6aedb167f70860e89776ab8c0ac56cbf88fe798adb98bc8c3a11bd51810cf1c。旧d38/429/78e/9f2逐byte保同目录，未部署。hardware对新三件最终diff审阅无阻断、未重跑合同；尚未执行builder整复制/launcher/设备，不能把预计413算实际通过。

## 挂点和不变项

actual df780文件中Scheduler.schedule:388–1100的dedent完整方法SHA为87a6016cdb08ae0d5bdb3fc2c14cb6974467a76b58d0ed41c35aadf1b697a8dd。唯一变换：RUNNING内层while原allocate返回None、成功分支break之后，原victim选择/pop之前，加一条callback，直接传已有request/newtokens/budget/index/num_scheduled_tokens。删除该行逐byte逆回原方法，原None/FCFS pop/PRIORITY代码/原preempt/返回均保留。方法只内存compile，不写installed源。

默认install(False)不动框架。显式启用先验证e043完整原init末尾footer/e155原runner、原Core及其step方法，只挂CORE_HOOKED；构造完成后首次step才用sys.modules自然加载的10份固定actual源码及原schedule/allocate_slots/_preempt_request方法身份安装schedule，Async必须继承原schedule，成功另记SCHEDULE_ARMED。a4de只复制并复用静态_scope函数，**不install旧probe**，不主动import framework/worker。

修订理由：actual Core27b:110先加载general plugin，137才get_scheduler_cls，本地无证据证明Async更早已自然加载。旧稿若在general时要求全部10模块，可能提前拒绝；不是已测设备失败。采用上述延迟验证避免为不确定性新增设备门。首次setup失败将该Engine记为disabled，原路且不逐step重试。

Core包装只在原构造完成后的step设置ContextVar，资格沿已审MiniCPM BF16/42层/单卡/Async V2/FCFS/FullAttention16/no connector/no lookahead/deferFreeFalse；原调用恰一次、原返回/异常，finally reset。每Engine第一次失败最多尝试一次，之后Core直通、不再逐步遍历或打印。元数据读错记录INCOMPLETE，仍执行原pop；scope读错在except结束后才调原方法，避免给原异常添加观察异常context。

## 快照语义

记录完整running原顺序/opaque ID与对象身份、prompt/合法max/已确认输出/known/issued/placeholder、当前尚未issued调度项及真实queued spans、owned页/唯一ref1非null私有页/shared/hashed/null计数。只读queued entry的原SchedulerOutput，不访问任何Future方法，不取token内容、tensor值或GPU API，也不调用allocator/prefix查询/predictor。

安全R按 `floor(min(issued−所有queued span, known−1)/16)*16`（不足16为0）记录；本schedule尚未issued项只单列，不再扣一次。逻辑页覆盖只证明有完整非null唯一页描述，配合1GiB字段仍**不是成功SAVE资格**：host/pin余量未观察、无实际copy。

free直接读原free队列整数；需求只在exact FullAttention RUNNING num_cached_block快路径用 `max(ceil(min(min(computed,maxlen)+newtokens,maxlen)/16)−len(owned),0)` 推导。scope保证无新prefix/encoder/lookahead/水位；明确字段标为derived，不能说已捕获allocator内部local。若不符合快路径则INCOMPLETE，不偷偷额外调用查询。

对schedule globals做AST/symtable核查：实际依赖是导入类型/辅助函数/time模块/builtins及导入时赋值的logger，没有global语句或之后重新绑定的模块状态；浅copy仍共享模块和logger对象属性。这只针对固定模块/无其它wrapper范围，不保证任意后来修改global名字的插件。

## 最短验证与下一条操作

唯一CPU合同最终1test/0.058s通过：完整源码/AST逆回和漂移拒绝，直接执行actual内层while AST原版/新增callback版对比原分配、pop、preempt、返回和同异常；首次/零失败/读错原路、禁Future、Core上下文与异常context，另补首次step延迟arm恰一次/缺模块原异常及不重试分支。补充分支初次曾因测试fixture的self指向Engine而失败，只修fixture参数名，失败保late-arm记录。它不是整个scheduler/GPU模拟，不证明实际snapshot已命中。没有重跑旧COPY/协议套件。

独立builder从73e5/5bef固定参考中的原410输入全树核验，e043完整append得到init01c42c，添新runtime+a4de+manifest预计413，保原e155/既有BIV模块及内部文件别名规则；全新目录拒覆盖。launcher沿原锁/双栈空闲/DBbefore和原bc51 context-long/seed721201，仅启动一个child。root既有seal负责DBafter/live/post。

由root在当前A2/B2结束并确认设备空闲后上传三新文件及普通a4de/helper/driver素材，核上表SHA，执行：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/launch_preemption_snapshot.py
```

原driver的require marker发生在load之前，因此只用CORE_HOOKED做快速入口预检；它不代表schedule已装或快照完成。**真实诊断通过必须有实际SCHEDULE_ARMED，且负载后出现恰一条FIRST_RUNNING_FAILURE complete=True及同PID FIRST_CHECKED eligible=True**。无真实失败/INCOMPLETE不算通过；实际全running/页/R分布、原输出32/0、原参数/413source/live/DB与后态另验。不加smoke或重复旧suite，一次诊断的CPU页遍历/日志有扰动，不报性能收益/accuracy。

## 实际执行进度与本地后验

root已逐pin上传新三件并启动独立 `20261021T230548Z-preemption-snapshot-context16k-long` /runner240134。其在途检查见Engine240315同PID CORE_HOOKED→SCHEDULE_ARMED（87a逆回true）→FIRST_CHECKED eligibleTrue、KV521936；frontend240147因原Core未自然加载REJECTED另列。当前仍等完整失败快照/正常退出/源和后态原件，**不把这些安装事件当诊断通过**；上文“尚未执行”仅是准备阶段历史状态。

本地唯一后验入口 `scripts/review_preemption_snapshot_run.py`，SHA **6eb45eceb46405e448e1388940c238e6f1c008123e5566b158910ed4e05bdcf0**，只compile/原固定raw函数413适配语法检查，未运行实际inspect。固定413/原参数/source/live/DB/post，恰一完整失败及唯一同Engine四段事件；动态核逐请求实际长度/队列跨度/R/静态cap/逻辑页与derived需求，不继承构造或旧轮R。结构候选排除失败请求自身，只在保留该请求继续的前提下讨论替代释放容量，不生成选择策略或性能收益。

```powershell
python -X utf8 scripts/review_preemption_snapshot_run.py 20261021T230548Z-preemption-snapshot-context16k-long --output analysis/source/preemption-snapshot/230548-review.json
```

该命令待root完整原件到本地后才执行。旧入口e0ea逐byte保同source目录；本次只作同Engine链/排除self两项静态收紧，未改部署资产、未新增设备或CPU套件。逐请求长度只能由快照实际元数据说明，不能用bench总token量反推每条服务prompt恰为16384。

## 完整原件到齐后的实际验收

上述命令现已对root完整封存的230548原件**唯一执行一次**，exit0/1.465s，无解析修复或设备重跑。报告SHA06c16d26e8eee184269d46d09f488da5b63867f90e57900eaaf1484c23ae53e4，执行回执a63180798d9be08b2f3c1a27f88214888e2e855d61c0210bcb8e6c55918eadfb；[实际中文结果](2026-10-22-preemption-snapshot-230548-result.md)给出动态31条/长度/页/R与限制。前文待执行描述保留为准备阶段历史，不能再作为当前状态。

真实同Engine完整链/恰一completeTrue失败、413/live/原参数/32-0/DB三SHA同/后态通过。31条实际running prompt全16384，outputs327..569，free0/推导需1；只足以证明该时刻存在进展差异，不证明任何换victim收益或准确率。没有新增policy。
