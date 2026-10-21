# 启动内存标量观察器：两冻结源的独立最短包装

2026-10-22，systems_innovation。只CPU准备builder/launcher，无SSH/GPU/整复制测试或新套件。root拥有单卡，计划在这两次startup smoke及独立审计后统一专用实验库发布/ZIP；不改共享代码库，不重跑长baseline。

这不是性能pair，也不把6块KV池差异预设成某个实现成本。既有213016 stable KV521936、213616 capacity KV521840，FULL214400 KV521936等事实说明启动容量会变化；现有日志不能分解出差异来源。本门只记录原determine与原profiling context已有CPU标量、原返回及原方法链，缺实际数据时记unobserved/未激活，不增加GPU采样或改容量算法。

## 最新实际结果：两个startup均通过，内存分项相同

215849 stable与220122 capacity均已原件独立审计exit0/pass，412/418全部源/原init完整append与原manifest字节/原bc51 smoke-only-VERIFY0/完整8in32out请求/CPU6/物理32GiB/DB实体/post通过。实际PID231345/231998，各自同PID profile1、原int22447777996→PARENT真list[同值]、三个hook全恢复；没有拒绝/未激活/不完整事件，只有API/Core可能各自ARM，不能要求所有ARM同PID。

两轮所有原memory数值（排除timestamp/profile_time）完全相同，KV均521936：requested29205777612.8、weights5101233152、torch peak increase656424960、nonTorch increase1000341504、nonKV6757999616、graph estimate0、available22447777996.8B。双方DBbeforeafter51919340三SHA897/29d/71ac同；post分别22:01:02.902726Z、22:03:14.114658Z全源未变/68MiB0/双栈闭无GPU进程。ERROR测前及shutdown皆空，forcekill WARN原样保留。

本次未复现旧6块差，不能回填历史原因/分项，不报性能或实现零成本。两份独立JSON与systems-startup-comparison.json/readonly复算入口在source/kv-memory-observer，hardware另解释真实公式/logger。registry104/queue80完成，按root要求本批收尾后临时停写供一致发布ZIP，goal继续；以下准备期未设备表述均为历史。

## 固定资产与完整输入

- 同一观察器 `patches/framework/biv150_kv_memory_observer.py` SHA **6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c**，hardware所有、framework已终审。
- 已有唯一CPU合同 `tests/test_biv150_kv_memory_observer.py` SHA **0becd99b5de8c98926538a9e174ebe68b31476c3079a5c4703eea40f8dcd33d5**；owner1test0.002s，本agent不重复。
- 新builder `scripts/remote/prepare_kv_memory_observer_source.py` SHA **0ab0ce3ab3d8cde4a8e725d9fdfd3e62726fcf95613fbc1e55b850b3e48a9029**。
- 新launcher `scripts/remote/launch_kv_memory_observer_smoke.sh` SHA **5bdb67afe573d9ffc803e40bafcaee2e7e7fd85e8b831bb94137516e85c060fd**，只接受stable/capacity参数。

builder先核source helper0ecf，再只读固定212106-control/source-sha256.json SHA **73e5d880f5a92f528618ffda71677c2b56c4b49ae582258dc0946ff20809a436** 与其plugin-source/innovation-source.json SHA **5bef5daf33f8d4ed31f4d146106ff2eb23f5a05f317c256f544a07332a6f872d**。从后者input_sha256得到冻结080656 stable完整410项身份，从前者得到原212106 capacity完整416项身份；实际ROOT/code原树须逐项完全相同，不能只凭几个core hash拼接或使用新FULL树。

| variant | 原树 | 原完整init SHA | 完整尾部append后的init SHA | 新source项数 |
|---|---|---|---|---:|
| stable | code/sql-mixed-20261021T080656Z | e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff | 00e8def05ec16d3dcc01bcfe47c976dd4954402984b0a9ba1162d4b72547c3f4 | 412 |
| capacity | code/kv-capacity-20261021T212106Z | 791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8 | 39fb96f474c4bacc79ba4cdc1ae27ce877f9dd654825c792dc8446ac620b08e0 | 418 |

AST只读取已固定观察器的INIT_FOOTER/允许前缀，不执行观察器。新目录只改变init精确append、新增同一观察器模块及独立`memory-observer-source.json`；原worker a8de、runner e155、capacity67e4/616/31cc/c95f与**原innovation-source.json完整字节**不改。新manifest记录原input完整map/新output map、参考manifest/observer/helper/preparer SHA和原innovation SHA，不覆盖旧manifest来伪装其原输入身份。

沿既有source_files规则仅允许内部普通文件alias，复制忽略pycache，前后原树/副本map一致；已有输出目录/已附observer或身份不符拒绝，不覆盖旧实验。原module源码guard与完整原SQL/C2/C3/协议footer保持，observer必须附其后，不能插入中间绕开初始化顺序。

## 原命令与最短启动

root上传固定资产后分别调用launcher `stable`、`capacity`，每次独立UTC run/control/source目录，**先结束并seal第一个再启动第二个**。launcher检查68MiB0/无GPU进程/9031双栈闭，固定builder/helper/observer/原bc51/DB helper，执行新source准备，封存源码/命令和DBbefore。原bc51自身同锁/清理仍保留，root既有seal收DBafter/live/post，不新增长时间DBbeforeafter性能门。

原driver只用 `--smoke-only --seed 721201 --require-log-marker '"event": "DETERMINE_RETURN"'`，环境 `BIV150_KV_VERIFY_RESTORE=0`。不启context-long、不改原SERVER/模型/参数/benchmark。输出在framework独立kv-memory-stable-smoke或kv-memory-capacity-smoke目录，不能混到official baseline；smoke中的必要原请求也不计作吞吐结果。

marker需要真实DETERMINE_RETURN，ARMED/INSTALLED仅武装不能通过。purpose进一步要求同PID profile_context_calls==1、原int返回/worker/profile/原三快照已有CPU标量完整、PARENT_RETURN原list、worker/profile/parent三个hook恢复全true；REJECTED/NOT_ACTIVATED/OBSERVATION_INCOMPLETE、missing字段均不能当成功解释内存。

## CPU准备与边界

本agent只做builder/heredoc compile、固定pin和两原init逐byte append推导，证据 `source/kv-memory-observer/wrapper-check.json`；没有执行builder全目录复制/shell/新CPU套件/GPU或伪造run。root、hardware、framework均已全文只读终审最终0ab0/5bdb，无运行阻断；没有重复copy/suite/设备。两文件冻结，自交付后字节未变，不静默更改。

实际门必须记录原determine返回、requested/nonKV/weights/torch/nonTorch/graph等分项及原profiling路径是否完整，区分直接字段与重构量；缺字段明确不可解释。一次启动标量只提供组成快照，不证明GPU峰值、长期稳定、6块差由代码引起或性能增益。最终保留source/args/DB/原日志/driver采样/post与失败事件，启动后不能为凑容量改参数/加buffer/无限重试。
