# 首组共同观察器capacity/FULL：约0.199%单次小信号

2026-10-22，天数BI-V150。首组新长负载两侧已结束，保留这项小正差，尚未证明稳定收益。root在复核结果出现前明确只追加一组必要A2/B2，无论正负或失配均结束此性能重复，不追容量/改参数或择优；A2当前224411 runner236809，B2与结果待。新模型accuracy/官方复现与默认集成资格未新增。

| 原raw指标 | 222731 capacity | 223613 FULL |
|---|---:|---:|
| 成功/失败 | 32/0 | 32/0 |
| 输入/输出token | 524288/32768 | 524288/32768 |
| duration秒 | 218.81890873378143 | 218.3848344660364 |
| total token/s | 2545.7397773504263 | 2550.799836270839 |
| mean TTFT毫秒 | 62472.47070692538 | 62338.00159151724 |
| KV token容量 | 521840 | 521840 |

按原raw独立复算：FULL TPS变化 **+0.19876575624233617%**（ratio1.0019876575624234），duration变化 **−0.1983714617063148%**，少 **0.434074267745018秒**，TTFT变化 **−0.21524539350935568%**。这些是这一组A1→B1观测，不是独立ZERO阶段计时或统计置信的效果量；不把0.43秒直接归因2772个zero_。FULL也有能力字段/覆盖检查等差异，root要求小收益保留，故不按最低百分比淘汰。

## 已实际匹配的条件

两侧同418/init39fb/6a观察器，原bc51 context-long/seed721201/SERVER/模型、packages/installed/native fingerprint，CPU6/物理32768MiB；DB四快照519表19340行、实体89743b20/schema29d740d5/逻辑71ac1989均同。原startup非时间分项全相同，KV都521840，available22443583692.8B/nonTorchIncrease1004535808B；每轮实际同PID profile1/原int→父list/三hook恢复。不是沿旧smoke的521936推算新轮，而是新轮实值。

两侧实际R16688/P1043/717717504B、SAVE源23run/966copy、目的66run/恢复2772copy、fast462/原consumer16/runner六checks/host释放均相同。hardware专项更核实际SAVE源page_ids及恢复目的page_ids逐项相同，见source/kv-memory-observer/223613-full-memory-transfer-review.json SHA9f319d02d09a906916eca753862b4c90b8ea27062e5bef07d94418360f7272ca；本agent没有重复该数组专项。

capacity实际SAVE→ZERO→RESTORE→DROP、ZERO2772calls；FULL实际SAVE→RESTORE_FULL→DROP、zero_stageFalse/zero_calls0/fullcoverage/destbound真ACK。两侧均VERIFY0，无本轮字节回读；先前各自VERIFY1独立列证据，不能伪造verification_passed。新source唯一约定三模块差异及两manifest元数据变化保留，源、参数和原件都没有为好看结果改写。

## 审计与边界

framework分别唯一c0审计通过，222731-capacity-review.json SHAece929aef6d788658b7482ff5d22052cea7694cf5aa4e24f664e207327646f27、223613-full-review.json SHA4fb9b2caa35e77ed4b3267bcdc30a3a5d5963cc2f498d0dab5b1920129b909ab。本agent只读报告后独立核原raw/TPS公式、选定源角色、原observer与ACK/consumer、DB字节/metadata、post字段，不重跑同入口/套件。字段核222731-/223613-registration-crosscheck.json；原raw直接可复算的比较在source/kv-memory-observer/observed-pair-first-comparison.json。

FULL22:41:18.016675Z exit0，post22:42:01.143516Z全源无变/68MiB0/双栈closed无GPU进程，测前与shutdown ERROR均空，原forcekill WARN保留。capacity测前ERROR空而shutdown有ERROR，单独分类，不泛称两者都有ERROR。两包owner SHA分别8ded4126824d40bac5869cbb254238b9de9dbcceaa67907a7e73b926030f991b、12ab2569ba15acfca31ad3a3ec9bafab6af8e3c0a42cfbc97c870dc5ac73046e。

共同observer仍有stdout/CPU扰动；同DB不代表所有Triton/主机cache或并发host状态精确同。首组顺序固定、只有一次，没有随机交替统计或完整accuracy。实际资源/几何对齐增强可比性，仍需按预定唯一复核收口，不能取最好值或因为第二组不利而继续刷样本。registry106数据×16/queue82保存首组与A2在途，后续先收到原件再执行唯一验收，不预填第二组均值/结果。
