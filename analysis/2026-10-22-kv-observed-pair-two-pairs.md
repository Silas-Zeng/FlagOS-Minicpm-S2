# 共同启动观察器 capacity/FULL：两组分层记录

2026-10-22；仅天数 BI-V150。两组共同观察器VERIFY0对照均已完整验收，分别保留约+0.1988%与+0.0603%的FULL吞吐小正差，第二组TTFT略升亦保留。只记录两个容量层级内的各自比率，不跨层混均值、不称稳定收益。本项已按预先计划结束性能重复，不追容量、不改参数、不挑最好值。

## 组一：KV521840，已结束

| 字段 | A1 capacity 222731 | B1 FULL 223613 |
|---|---:|---:|
| 成功/失败 | 32/0 | 32/0 |
| 输入/输出 token | 524288/32768 | 524288/32768 |
| duration 秒 | 218.81890873378143 | 218.3848344660364 |
| 总 token/s | 2545.7397773504263 | 2550.799836270839 |
| mean TTFT 毫秒 | 62472.47070692538 | 62338.00159151724 |
| KV token 容量 | 521840 | 521840 |
| 实际 R / 页数 | 16688 / 1043 | 16688 / 1043 |
| SAVE 字节 / copy calls | 717717504 / 966 | 717717504 / 966 |
| 目的连续段 / 恢复 calls | 66 / 2772 | 66 / 2772 |
| fast rejects / 原消费者 token | 462 / 16 | 462 / 16 |

组内 FULL TPS +0.19876575624233617%，duration −0.1983714617063148%（少0.434074267745018秒），TTFT −0.21524539350935568%。两侧 DB 四端、启动非时间内存项、实际 SAVE/RESTORE 页数组均匹配；保留小正差，不称稳定效果或独立 ZERO 阶段耗时。详细边界及原件身份见 [首组报告](2026-10-22-kv-observed-pair-first-result.md) 与 `source/kv-memory-observer/observed-pair-first-comparison.json`。

## 组二：KV521936，唯一必要复核已结束

| 字段 | A2 capacity 224411 | B2 FULL 225501 |
|---|---:|---:|
| 运行状态 | 完整 c0 实审通过 | 完整 c0 实审通过 |
| 成功/失败 | 32/0 | 32/0 |
| 输入/输出 token | 524288/32768 | 524288/32768 |
| duration 秒 | 218.84790462488309 | 218.7160065015778 |
| 总 token/s | 2545.402483769829 | 2546.937505444904 |
| mean TTFT 毫秒 | 62497.66085240117 | 62627.150716711185 |
| KV token 容量 | 521936 | 521936 |
| 实际 R / 页数 | 16704 / 1044 | 16704 / 1044 |
| SAVE 字节 / copy calls | 718405632 / 1008 | 718405632 / 1008 |
| 目的连续段 / 恢复 calls | 66 / 2772 | 66 / 2772 |
| fast rejects / 原消费者 token | 454 / 8 | 454 / 8 |
| DB before=after | 519表19340行，三SHA相同 | 519表19340行，三SHA相同 |

组内 FULL TPS **+0.06030565636920837%**（ratio1.000603056563692），duration **−0.0602693105658747%**、少 **0.13189812330529094秒**，TTFT **+0.20719153732142725%**。吞吐小正差与 TTFT 负向变化都保留，不能只挑吞吐或将其称为稳定效果。

A2 报告 `source/kv-memory-observer/224411-capacity-review.json`，SHA `e52a572e7ccbb577acf882934bf8ef06f42a0fe8f01d13efc0cb17442a2a5d45`；B2报告 `source/kv-memory-observer/225501-full-review.json`，SHA `62b07a8cabef0cf5d9259abb433e83e55ccfb553b121de4e4e0df7ae62af9b2f`。本agent分别唯一执行冻结c0，B2实际exit0；本次另外只读两原raw核字段/哈希和token÷duration算术，未重复完整入口或套件。

本组记录条件全部匹配：418源/共同6a-init39fb、原bc51/SERVER/contextlong/seed721201、VERIFY0、packages/installed、CPU6/物理32GiB、DB四端三SHA、KV与启动非时间内存分项相同。A2/B2各自同PID profile1/父真list/三hook恢复；B2实际PID238635。两侧 nonTorchIncrease1000341504B、available22447777996.8B、原int22447777996、KV521936。首组分别1004535808B、22443583692.8B、KV521840，容量与恢复几何层级不同，**不合并四轮绝对 TPS/均值，不把 A2 当 A1 的 matched 漂移样本**。

本组实际R/页/字节/源24段1008copy/目的66段2772copy/fast454/consumer8相同。B2实际SAVE→RESTORE_FULL→DROP serial123，0ZERO/zero_stageFalse/完整覆盖与绑定ACK、runner六checks/原输出8token消费者与host释放均通过；VERIFY0没有本轮回读。23:00:06.869321Z exit0，23:01:06.003547Z post418源无变/68MiB0/双栈9031closed无GPU进程。B2测前与shutdown ERROR均空，forcekill WARN原样保留，不泛称发生ERROR。包owner SHA `472555b4eee2a0d7f1cfd144fa2b56fbe57b6d2caefd161b85b910f3df2e856a`。

## 两组已按预定收口，保留小信号及边界

两组分别得到 FULL TPS约 **+0.1988%** 与 **+0.0603%** 的小正差；TTFT第一组−0.2152%、第二组+0.2072%，方向不同。只保留各组实测，不给跨容量总体均值/比赛总分，不从整体差反推独立ZERO耗时。顺序样本仅两组，共同observer有CPU/日志扰动，记录起点相等也不证明所有编译cache/主机干扰完全一样；**尚不能声明稳定因果收益**。先前VERIFY1门独立存在，不移植为本轮回读，新accuracy/官方复现/默认集成资格未新增。

全部比较及原raw引用可复算于 `source/kv-memory-observer/observed-pair-two-pairs-comparison.json`，SHA `c7f7ffa9f419a91dfe04831c65df438054081941ff59117152b5c54b3f8d20cb`。唯一B2执行回执 `225501-audit-execution.json`记录实际命令/exit0/依赖A2报告/validator pin；原审计JSON与原件未改。registry108数据×16列/queue82均LF，既有A2更新为已配对、新增实际B2完成行，其它未涉及的registry行逐byte保持。

在B2结果出现前已限定仅这一组必要复核，**本项性能重复现已结束**，不追加启动样本、不改参数凑容量、不取最好值。后继victim只观察任务属于独立源码/新run，不将其混入本pair。root独占SSH/GPU；本agent仅CPU，未改CURRENT/根资产/冻结运行模块。

冻结入口 SHA `c0c80dcf81b2fc0727f06b43d166a61ad042916ee300511243c2aae42cb14c00`，B2唯一实际命令：

```powershell
python -X utf8 scripts/review_kv_observed_pair_run.py full 20261021T225501Z-kv-observed-pair-full-context16k-long --capacity-review analysis/source/kv-memory-observer/224411-capacity-review.json --output analysis/source/kv-memory-observer/225501-full-review.json
```

首组固定检查点已由root发布为远端 `111910c84ecbeb7e54c1505289cf1d1aca154136`、tree `37b8951fa6b84154aed9ca70ae8f786cbb31a59e`、16922项全核；不宣称该发布含新A2/B2完成原件或本后续总结。
