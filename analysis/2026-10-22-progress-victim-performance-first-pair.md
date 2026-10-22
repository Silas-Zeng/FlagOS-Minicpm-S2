# 进展victim首个VERIFY0 A/B：完整结束，容量失配不计算收益

2026-10-22，仅BI-V150。原FULL1aff A020721与进展72942 B021658均已32成功0失败、完整源与后态验收通过。**实际KV容量和启动分项不匹配，recorded_environment_match=false，TPS/duration/TTFT三收益字段均null。** 保留原绝对值和动态行为，不用原耗时差宣称策略收益，也不称“收益为零”。本首对按root决定结束，不追加盲复跑或第三run、不改参数追容量。

| 原raw绝对指标 | A 原FULL 020721 | B 进展选择 021658 |
|---|---:|---:|
| 成功/失败 | 32/0 | 32/0 |
| 输入/输出token | 524288/32768 | 524288/32768 |
| duration秒 | 218.39959823712707 | 218.51338428491727 |
| total token/s | 2550.627402689529 | 2549.299219464107 |
| mean TTFT毫秒 | 62408.937510466785 | 62356.0446958727 |
| 实际KV token容量 | 521936 | 521840 |
| profile nonTorchIncrease字节 | 1000341504 | 1004535808 |
| 可用KV原字节标量 | 22447777996.8 | 22443583692.8 |
| 当前源与资源 | 418，CPU6/物理32768MiB | 418，CPU6/物理32768MiB |
| DB before=after | 523表19474行，dc2c/0dc7/c05d三SHA同 | 523表19474行，同A且前后同 |

同6a观测记录了B的nonTorch组成比A多4,194,304字节（4MiB）、available相应减少，KV少96token。**具体分配者或原因未证，不归因于协议，也不补填其它历史run。** 物理显存相同不能替代实际KV/启动分项比较门，未为凑容量刷样本/加dummy或改util。DB四端、原SERVER/bc51/contextlong/seed721201、packages/installed、CPU与约定source差都匹配；source仅当前canonical协议1aff/72942及新pair manifest不同。环境门没有把R/消费者/段数当相等条件。

## 实际策略行为分别保留

| 行为字段 | A 原FULL | B 进展选择 |
|---|---:|---:|
| 新选择事件 | 无；原tail代码路径 | 真一次DECISION，9个候选 |
| 失败/选中/原tail running index | 没有新decision，不倒推快照 | failed20 / selected21 / tail30 |
| 已确认进展 | 不由R反推 | selected392 > tail319；保护max561/minremaining463 |
| 真实稳定R / 页数 / bytes | 16704 / 1044 / 718405632 | 16768 / 1048 / 721158144 |
| SAVE源段 / copy calls | 24 / 1008 | 26 / 1092 |
| 恢复目的段 / copy calls | 66 / 2772 | 66 / 2772 |
| ZERO calls | 0 | 0 |
| fast / restore skips | 454 / 454 | 462 / 462 |
| 原consumer scheduled token | 8 | 9 |
| 原metrics抢占 | 0→1 | 0→1 |

B实际Engine253818；选择index21是本轮按已确认进展和严格后方/未scheduled/保护关系动态得出，**不是015315的index2/output552，也没有按固定索引或benchmark序号实现**。同selected rid真正完成SAVE→RESTORE_FULL→DROP serial123/完整覆盖ACK/host释放，runner六checks与原consumer9在原update后通过。A和B均VERIFY0，没有本轮字节回读，不能移植015315 VERIFY1的42层回读为本轮结果。动态R/copy/consumer不同属于策略行为，允许并保留；环境失配才是本轮不能算比率的原因。

两侧同PID profile_context_calls1、原int→父真list和三hook恢复均通过，A PID252228、B253818。B 02:22:03.037163Z exit0，post02:22:42.575452Z418源live无变/68MiB0/无GPU进程/9031双栈closed；A post02:13:19.255413Z同样通过。两轮测前及shutdown ERROR均空，forcekill WARN各按原件保留。

## 唯一验收与停止边界

本agent分别唯一执行冻结入口3f1dc204，不重跑旧suite或设备：

- `source/preemption-snapshot/020721-full-review.json` SHA `be286a95749b39cf6ed8089f7c2f27295d34a35f1fffb8eec4a3d2532068ced9`。
- `source/preemption-snapshot/021658-progress-review.json` SHA `90f3c896fdb8537e5cb317b823f1b7410b492acd5e1e5bbfbb830dddbd981c99`，引用本A报告，三项环境失配收益均null。
- 唯一执行回执020721-/021658-audit-execution.json；阶段比较 `progress-victim-first-pair-comparison.json` SHA `b346349c957f1341f6cedd2468c7815d13eb6498a3c981bbe1cd397f4be94661`，不计算其它raw百分比替代null。

包owner SHA：A `73ca1a3d3ecf93d81c155041eaa4db3932a58fa234278565676580fe66472a2f`，B `c6989051d9caa8e2dac548e88e85b155fab1d95c0bbacc32f4523eea97e46176`。registry112×16列/queue85、phase及本agent交接已收口，A更新为配对失配完成，B新增真实完成行，不覆盖原raw/JSON。

本轮既不确认正收益，也不凭失配断言策略无益；机制仍保留，未获得新accuracy/公平/默认资格。先前capacity/FULL两组小信号独立存在，不混成这个victim策略成绩。root明确首对结束，不追加盲复跑/第三run、不追容量，下一方向待root另定。用户最新暂不发布/PR，本agent不推送、不SSH/GPU、不改CURRENT或冻结资产，goal持续。
