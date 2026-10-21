# capacity与FULL共同启动观察器：独立VERIFY0包装

2026-10-22，systems_innovation。root通知完整ZIP221629通过、临时写锁解除后接续同一项目。六轮固定692d680已发布远端e1e4740a/15983项，新包装及本记录是其后新增，不能冒称已在旧发布/离线包中。root独占SSH/BI-V150，本agent只CPU准备新文件，不改旧包装/冻结源/官方脚本与服务参数。

## 最新首pair完成与唯一复核

首组222731/223613已经唯一c0全审及独立字段核：同KV521840/实际启动分项/DB四快照/418源base/几何及hardware实页IDs相同，FULL测得TPS+0.198765756%、duration−0.198371462%少0.434074268s，仅一次小信号保留，非稳定收益或独立ZERO时间。详细2026-10-22-kv-observed-pair-first-result.md、observed-pair-first-comparison.json。root只授权一组必要A2/B2复核且无论正负/失配收口；A2 224411 runner236809在途、B2待，代码与参数冻结，registry106/queue82，不预填复核结果。以下仅capacity完成/FULL待为历史。

## 既有实际capacity侧：222731完成，FULL结果尚待

222731已22:32:35.393293Z exit0，framework唯一c0入口全审通过（report ece929ae…），本人另核原字段未重跑入口；418/同6a-init39fb/原bc51long-VERIFY0，32-0/218.81890873378143s/2545.7397773504263total/KV521840，DB51919340三SHA前后同、post22:33:26.459826Z过。实际profile1/原int22443583692→父真list/三恢复，profile_nonTorchIncrease1004535808/available22443583692.8；R16688/717717504B/SAVE966/ZERO-RESTORE2772/fast462/consumer16/host释放，无回读。4MiB分项由hardware专项解释，不倒填历史；当前FULL实际结果未齐，不预判资源匹配或pair收益。registry105/queue81，以下“仅CPU/未设备”段落为包装交付历史。

## 要比较的行为

对照是冻结capacity67e4/worker31cc/transaction616，候选是冻结FULL1aff/worker5d9a/transaction84be；各自此前独立VERIFY1已证明真实42层字节与原消费。新轮两边共同6a启动观察器、VERIFY0、bc51 context-long/seed721201。它比较这两个模式的整体端到端差异；FULL还包含SAVE能力字段与完整覆盖验证，因此即使R相同，也不能用总耗时差估计独立ZERO阶段时间。

不新增COPY/DTO/事务CPU套件，不重跑VERIFY1长轮或盲目启动样本。小差异保留，负结果也保留；DB/KV/真实R或恢复机会不同时明确限制，不改util/KV参数或加buffer凑容量。新accuracy/官方复现资格仍未继承。

## 两份完整416输入与同一418输出

| 模式 | 完整source manifest | 原innovation manifest | 冻结原树 |
|---|---|---|---|
| capacity | 73e5d880f5a92f528618ffda71677c2b56c4b49ae582258dc0946ff20809a436 | 5bef5daf33f8d4ed31f4d146106ff2eb23f5a05f317c256f544a07332a6f872d | code/kv-capacity-20261021T212106Z |
| full | a67c717f5e1f7ab5e2240dc9cd8623c02a91aa2b2958b9ee0bf206c791183829 | 93375c426c9fb0b4d5abdb869ba94a8fab0a01ce1863ab0e1bd9785f586827fe | code/kv-full-restore-20261021T214400Z |

本地独立只读实核两完整map恰仅四项不同：协议、事务、worker三个实现模块，以及各自原innovation manifest；init791c、a8de WorkerFL、e155 runner和其它源码都相同。新builder逐项核416完整原树/三个角色pin/原manifest自述output map，才向ROOT/code全新直接子目录复制。

两边都只在**完整原init及原协议footer末尾**附同6a footer，791c→`39fb96f474c4bacc79ba4cdc1ae27ce877f9dd654825c792dc8446ac620b08e0`。新增同一biv150_kv_memory_observer.py与独立memory-observer-source.json，最终418文件；原innovation字节/三个实现模块不改。新manifest沿原schema记录variant capacity/full、完整input/output map、两个reference SHA、原innovation SHA、preparer/helper/observer SHA，另有kind声明共同VERIFY0模式。

6a的原EXPECTED_INIT_PREFIXES仍是stable/capacity键。FULL使用其中已允许的791c前缀值，不能把原字典直接与新capacity/full表判等，也不改6a去新增key。旧0ab0/5bdb只支持原smoke，不扩写或覆盖它们。

## 新文件、调用与前件门

- `scripts/remote/prepare_kv_observed_pair_source.py` SHA **fc937baf735e5694ce9d75c99c200e43b26524b9c24db09ed6939fc408ca2467**。
- `scripts/remote/launch_kv_observed_pair_screen.py` SHA **d768860b8f9d9491b6ea473ab1e0219cfb9a04351806e0cd67685b95fcdf981e**。

launcher每次只启动一个job。root先用 `--variant capacity`，完整结束/封存后，再用 `--variant full --match-capacity-control <新capacity-control>`；FULL缺前件或capacity携前件均参数拒绝，不自动接续第二job。

双方新run名为UTC-kv-observed-pair-{capacity,full}-context16k-long，source为ROOT/code新直系kv-observed-pair-{variant}-UTC。固定所有helper/observer/builder SHA，准备期获取原framework-device.lock，检查单BI-V150/32GiB、68MiB0/无GPU进程/9031双栈闭，准备并封存新418源/命令/DBbefore。退出准备锁后才启动bc51，让原driver自行重取同锁，避免嵌套死锁；每次最后再次核源与空闲。

FULL前件必须是本launcher相同SHA、capacity variant、原418源完整archive、已exit0并有fullpost/source无变/68MiB0/双栈闭/无GPU进程、owned进程已退出或Z。原capacity DBbefore=after三SHA（实体/schema/逻辑）且新FULL DBbefore同其after，全部用已pin SQLite helper实体复算；任何不符拒绝启动而留preparation-failed.json，不重置DB或偷偷追样本。

前件还必须实际同PID唯一profile1、原worker int→父真list、三hook恢复、完整原内存标量，不能仅ARMED。两次driver command都保持原bc51 `--context-long-screen --seed 721201`，环境VERIFY_RESTORE=0，require实际JSON DETERMINE_RETURN。该marker是入口预检，后验仍需各自协议真实操作链/数据完整/内存/KV/CPU/DB/host工作；不把共同observer称完全无扰动。

## 必要检查与纠正记录

仅做两Python compile、AST所有顶层赋值名唯一性和INPUT/OUTPUT标量类型、两真实reference map/原init精确append、所有helper/三角色pin、旧0ab0/5bdb/be934 SHA不变检查。root另外AST抽取新observer_receipt读取真实215849/220122日志，各返回profile1/int22447777996/三恢复全真；本agent只保存root回执，未重复该CPU兼容核。没有运行新prepare/全树复制/套件/GPU。

草稿复制区间误匹配了旧EXPECTED_CAPACITY_MANIFEST内部子串，留下旧INPUT/OUTPUT字典重定义；root及framework只读预审发现后已删除。它未部署或执行，最终AST唯一名/标量检查覆盖这一失误，不能仅凭compile宣称安全。首轮静态检查器把Path(...)也送literal_eval而失败，只修解析器跳过非字面量，不改运行代码。证据及完整差分在 `source/kv-memory-observer/observed-pair-wrapper-check.json`。

root、hardware、framework均已对最终fc937/d768全文只读终审无阻断，审者没有重复copy/suite/GPU；定稿后两code pin不再静默变化。framework负责实际新418/VERIFY0验收入口，不能直接硬套2071的416/VERIFY1回读要求。

## 后验与可比性边界

capacity实际应SAVE→ZERO→RESTORE→DROP；FULL实际应SAVE→RESTORE_FULL→DROP、zero_calls0/zero_stageFalse/fullcoverage真实ACK。两边VERIFY0无回读，不要求伪造verification_passed。R/页数/连续run/copy量/fast/consumer按各run实际记录；保存前缀或恢复机会不同必须列明，不能把所有总差归因清零。

实际启动同PID/profile1/原返回/三hook恢复只是数据可信前提，不保证两启动KV/内存项必然相等。DB相同也不代表Triton或主机cache/并发host工作严格同，需保留原CPU配额/物理显存/host约束。215849/220122的相等只属于那两次启动，不能回填本轮或历史6块原因。

本记录与queue81当前是包装准备，不是新设备结果。registry104维持真实已验行；root后续串行执行、采样和既有seal留DBafter/live/post，完整原件到齐才验收/登记/比较。无性能收益、accuracy或默认集成结论。
