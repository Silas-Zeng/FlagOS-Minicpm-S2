# 团队复现说明：一次必要CPU审阅

2026-10-21。只读审阅`docs/candidate-usage.md`、`analysis/2026-10-21-sql-mixed-full-package.md`、`docs/team-github-handoff.md`，并核其链接的`docs/official-verification.md`；随后读root新建`docs/technical-report.md`。行号指本次读取快照，root已接手修主入口，后续行号可能变化。本agent只写本文和自身handoff，不改上述文件、README、CURRENT、默认补丁或任何模型/设备。没有重跑包装、accuracy或benchmark。

**复读root修订后更新：主要安装缺口已解决。** usage现在顶端是一份完整4aba、原13eb全新checkout、一次git apply及同checkout的`--no-deps --no-build-isolation`安装；历史deltas明确是替代路径而非叠加。污染内容、原/候选依赖身份与三marker语义已齐。仅剩小排版建议：将闲卡/禁止candidate import段从安装代码之后移至第一段代码之前。下表保留初次快照依据，不表示root尚未修。

## 结论

完整4aba补丁的包装身份、官方命令与候选绝对成绩已有依据；初次主要交接缺口是三个文档间没有一条不会重复应用旧补丁的连续安装入口。这属于文档缺口，不是包装源码失败；root现已修为canonical完整补丁一次应用、同一新checkout安装，并将旧路径标历史，复读通过。

本地只读SHA核对完整patch确为`4aba147aa0bd3ec8dd1c12b6ae94bf39537a4cbad449e68e2fcdbfbdc0f8def6`。full-package记录的一步/两补丁树身份一致、212归档仓库文件、mode/symlink及逆向回原tree已由hardware独立验证，本轮不重复运行。包装证据不能代替新一轮性能或accuracy。

## 初次快照的实际缺口与建议（主路径已修）

| 优先级 | 本次快照依据 | 团队会遇到的问题 | 建议由root修正文档 |
|---|---|---|---|
| P1 | candidate-usage:14–22先`git am` retained/default；full-package:19已说明完整patch不可叠加，但:20回链candidate-usage安装 | 从full-package应用4aba后沿链接，会再次尝试retained patch；或仅按usage顶端复现出旧默认，漏SQL+C3。full patch是普通diff，不能替换文件名后沿用`git am`。 | usage顶端仅展示干净新实验checkout/原13eb→`git apply --check`与`git apply`完整4aba一次→`pip install --no-build-isolation`**同一checkout**→原服务和验证。旧retained、联合delta与独立delta移为历史/研究路径，不再作为可叠选项。 |
| P1 | 污染警告在full-package:22/team-handoff:25；usage主安装入口未提前说明，:51–52仅说两个delta不改installed源 | 误以为切换插件目录足以隔离原版；candidate平台import实际会把全局Attention从bab2写回54c。 | 在任何安装/导入命令之前说明：原版在途时禁止retained/C3 import；原版与候选用干净独立环境，或由owner在完全闲卡/同锁内按已审记录恢复依赖并核真实SHA。分别列baseline bab2+worker446f、candidate54c+e155，不清SQLite/Tritoncache，不在当前原版运行中试安装。 |
| P2 | usage固定环境只列vLLM/FlagGems；SQL段混合历史CPU2.0.43与实际服务2.0.48；full-package靠回链安装 | 团队可能拿相同tag但不同Torch/Corex/Triton/SQLAlchemy或installed文件，严格source guard拒绝，或无法解释环境差。 | 在唯一入口附近链接一张实际环境/核心SHA表：BI-V150/32768MiB、Corex4.5、Torch2.10.0+corex.4.5.0、vLLM0.24.0+empty、Triton源3.6.0、FlagGems5.3.5/4df52d9、SQLAlchemy2.0.48；accuracy工具版本从090505 manifest取。保留旧CPU测试版本为历史，不授权升级。不要顺手开启CPU线程/编译/块尺寸/禁prefix等额外override。 |
| P2 | usage:22称“patch idempotent”；:40–49称独立mixed仍待accuracy，后文joint C3已103/105；末尾重复SQL+C2安装段 | patch可否重用、当前要复现哪个组合不直观。 | 明确“runtime安装幂等；完整patch仅在干净原13eb应用一次”。区分旧独立delta与**已测SQL+C3联合候选**，历史段保留但不引导默认安装；不能因为联合accuracy通过而替未测独立变体背书。 |

这些建议无需改变默认补丁或重跑实验。已给root摘要；root确认会直接修canonical入口和污染前置。本agent不代写root文件。

复读另确认：clone `--no-hardlinks`只读原reference、目标新checkout明确；package安装不拉新依赖；full-patch record链接与技术报告环境表可连接起来；e155/4aba身份准确。marker列为SQL_INSTALLED、DECODE_FIRST_SELECTED、MIXED_INSTALLED，且文字明确mixed只证明安装，不证明每batch分流，符合actual源。历史“patch idempotent”等措辞只余低优先级精简事项，不再影响新入口唯一性。

root13:24Z阶段回执已更新：原4K四轮全部SUCCESS、summary1905.46total/TTFT12310.56ms，16K1/4仍在运行、bab2保持；本地progress-latest.json为阶段摘要而非原8raw/2summary完整证据。这里仅记录owner绝对进度，不做与candidate的最终ratio或总体gain。

## 官方命令与成绩表述核对

- 服务命令齐全：VLLM_PLUGINS=fl、MiniCPM5-2B、9031、FULL_DECODE_ONLY、served-name minicpm、显存比例0.85、max-model-len131072，与已审driver常量一致。
- 准确率命令没有缺失：usage通过链接到official-verification:50–64，内有完整evalscope CLI、chat/completions endpoint、Level3本地dataset、batch8、timeout3600、temperature1/top_p0.95/max32768及原work-dir/ignore-errors。建议canonical入口直接链接/展示该命令，并要求保存独立run原件，不把固定work-dir中的旧report当新结果。
- 吞吐命令齐全且两个case正确：`[[4096,1024,64,256],[16384,1024,64,128]]`。团队需核0813原脚本/4轮丢首，不使用短诊断或另造平均。现有原命令无需改参数。
- 103/105属于090505受测SQL+C3；完整4aba重建树对应原受测源码，包装本身没有重新测试。3683.65/2729.07 total tok/s及355.88/816.48s明确为候选绝对结果；三文档没有把未完成原版当完整baseline，也没有自造总分。旧“pending”独立delta段需要标签澄清，但不应删除negative。
- team-handoff对新专用仓库发布、参考仓库只读、原版期间禁止导入候选的约束正确。原13eb当前仍在运行；root13:16Z回执只有4K三条raw/进入4of4，16K尚未开始。旧12:57Z进度有明确时间戳，是历史，不可升级成已完成。

## technical-report的一次实质核对

没有发现需要否定候选绝对数据、accuracy或包装结论的实质错误。特别核实了容器配额：candidate与在途baseline manifest均为`600000/100000=6核`，报告不是误用宿主可见CPU数。SQL13.405s与其中构建10.780s对应旧host诊断的inclusive嵌套值，报告使用“其中”没有相加。4.97%短对照只称单次信号；官方两档表仍留原版待验收，符合现状。

两点建议使文字更精确，但不阻断当前在途版：

1. “SQL优化不清理或改写配置库”限定为该反射替换逻辑不主动改值；真实执行的正常调优仍可新增表/行，已实测DB变化须照录，不能让团队误解为整个run DB不变。
2. growth“实际减少一次抢占到零”可改为“控制观测0→1，候选0→0；DB差异保留”，将观测与因果判断区分。warm无正吞吐信号/不集成的决定正确；不因未有严格跨DB因果估计而再追加大验证。

## 原baseline完整结束时的字段准备：现在不填结果

保留registry现有16列；已有`20261021T122607Z-original-baseline`行应**更新**，不要为同一完整run重复追加一条“更好”结果，也不要将两个case混成一个虚构input_len/num_prompts。各case数据可写独立review JSON、conclusion与report两行表。

| 待取得并核验的真实证据 | registry/report后继动作 |
|---|---|
| exit-code/result/status/benchmark_completed/cleanup及实际结束UTC | 只有完整exit0/完成门过后将status从running改complete；保留起止UTC与真实failures，不能用startup225SHA代替终审。 |
| 原8raw/2summary、原case次序、每轮请求和tokens、原2–4均值 | 用现791 validate_outputs门；分别记录4K与16K的duration/total及outputTPS/TTFT等，当前全部待原件，不预填均值。 |
| 最终manifest、完整source逐项SHA、原benchmark0813/driver791、original13eb/worker446f、installed bab2、模型/package与总显存 | 记录实际源数量与失败清单、最终after bab2及无retained证据；不假定最终仍是startup225项，不靠launch命令替代live/归档身份。 |
| server.log真实KV、GPU记录、DB before/after实际SQLite及三hash/表行数 | 如实记录KV与DB变化；同时列出candidate092944的真实KV521936、DB489/18384→501/18789作比较边界，不能写两边缓存完全匹配。 |
| benchmark开始结束、四进程最终returncode、fullpostflight与服务清理 | 记录原始PID/command/archive、68MiB/0%/9031closed及无遗留；记录失败，不先过滤后挪动首轮。 |
| 两run完整本地证据及e9dc只读comparison输出 | root运行真实比较入口；report分别新增baseline绝对两行、percase原2–4 meanTPSratio与TTFT百分比。没有总体官方公式；DB/KV/暖机漂移和单次证据限制随结果一起写。 |

最终新增派生comparison/review文件使用新UTC名字并链接原CSV，不覆盖原CSV/result或伪造complete结构。若证据仍缺项，入口必须pending且不算gain；如果已有失败/身份不符，保留invalid及原件，由owner决定下一步。本轮不编辑registry/report或生成任何baseline结果占位文件。
