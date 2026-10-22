# 015315进展victim机制门：不同tail选择与FULL恢复已通过

2026-10-22，BI-V150。唯一 `20261022T015315Z-kv-progress-victim-context16k-long` 已exit0。本agent对完整本地原件**唯一执行b7ff**，报告 `source/preemption-snapshot/015315-progress-victim-review.json` SHA `f776f89ba579fcdc8bc24ecd6cfd10da1547ae2cb5faa75b9b15fdea2aa225fa`；执行命令/exit0/包SHA见 `015315-audit-execution.json`。旧f43未实际执行，修复只处理Windows远端POSIX比较；未重复旧suite/设备或改运行资产。

| 实际证据 | 本轮结果 |
|---|---|
| 选择 | Engine250261，真实None/28候选；原tail index30、已确认327；所选index2、已确认552，合法剩余上界472 |
| 保护/范围 | 非failed index1，后方且未scheduled；min remaining455/max confirmed569均未选；单次attempt，后续selectedcounter1 |
| SAVE/FULL/DROP | 所选真实rid完成serial1/2/3真ACK，无ZERO，host真实释放 |
| 实际稳定前缀 | R16928/P1058/728039424B；选择时owned私有1059页，不把owned与整页稳定前缀混同 |
| SAVE源 | 37连续段、1554次copy |
| 恢复目的 | 65连续段、FULL2730次copy；42层整页回读2730次、全部字节相等 |
| 后继原路径 | runner六checks全真、原consumer9 token、fast454；原metrics抢占0→1 |
| 完整负载 | 32成功0失败，524288输入/32768输出 |
| 资源与身份 | 417归档/live完整源，72942/bbb49/1f8，原init791c/worker5d9a/txn84be/e155/c95f，原bc51/SERVER/seed721201，CPU6/32GiB/KV521936 |
| 后态 | 01:59:22.547218Z，417源无变、68MiB/0%、无GPU进程、9031双栈closed；测前/shutdown ERROR均空，forcekill WARN保留 |

索引只是本次真实对象定位，运行规则按合法进展动态选出，未将index2或benchmark序号写为策略。安装marker不是结果；本轮已具备真实选择→同对象传输/发布→原消费证据，且worker字节未变。一次主动替换不等于承诺后续原路抢占数永远为1；本轮原metrics恰为1，仍据实记录。

## DB变化和结论边界

测前519表19340行，实体/结构/逻辑三SHA分别89743b20…/29d740d5…/71ac1989…；测后**523表19474行（增加4表134行）**，三SHA全变：

- 实体 `dc2c76463fc6c1ef0674b16ca4374125b3ee4551fa0b1886253093f310b237da`
- 结构 `0dc7a465bf12e53e054381d9e865460e7e4fe70287cc8c3683a41b0a4914ab39`
- 逻辑 `c05d7e3182d1837929b48d5699c6515786351eb8d22f73eb53227a39fb3c49c8`

原duration238.5769370230846s、totalTPS2334.9113579494883、meanTTFT63043.00184814201ms保留为绝对诊断值。**VERIFY1含完整回读/日志，且DB变化；本轮不计算性能收益，不以旧FULL/快照耗时作对照**。正确恢复/原消费不等于更短makespan、FCFS公平、全局随机数逐token等价或新accuracy/默认资格。

包owner SHA `38c096b9b254ee9846364912503d197897f5357db357422813368adca493794b`。registry110×16列、queue84与阶段/本agent交接已收口，原raw/失败旧稿保留。用户最新改为先进行实验、稍后自行操作，**当前暂不发布或提PR，也不为发布停写**；root尚未执行本阶段push/PR。本agent不执行远程/设备/推送。下一仅在root正式授权后准备同条件VERIFY0性能包装，不自动新跑机制门或追样本。
