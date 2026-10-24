# 当前工作与接续入口

更新：2026-10-24（北京时间）。已恢复持续优化，当前主线为含队友 PR24 的 `1ad9a708`；已完成本实例移植短验和一次抢占观察，单次 warmed 恢复窗口 GPU 诊断 `20261024T113346Z-pr24-resume-native-context16k-long` 已启动，结束后补充结论。受测有收益的方法按用户授权提交并合并 PR。

- 本实例 native SO 9项数值/Graph检查通过；16K/128 ×32请求全成功，P在ready后命中、Q无回退，KV547600。见[移植摘要](experiments/framework/20261024T105037Z-pr24-main-context16k-control/summary.json)。
- 16K/1024 ×32请求全成功、1次抢占；准入时APC11536，随后3段重新提交，重叠旧CPU已提交前缀5446。M1441确有新调优，不能把CPU的6.265秒当GPU收益。见[诊断结论](analysis/pr24-kv-diagnostic.json)及[DB差异](analysis/pr24-resume-db-comparison.json)。
- 该观察driver退出0；owner因monitor sleep短暂未退出而退出1，后续复核其已退出并恢复原DB，原失败与[恢复凭据](experiments/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long-control/cleanup-recovery.json)均保留。
- 下一步仅采一次已调优条件下的恢复窗口，再决定是否迁移KV SAVE/FULL；观察结果不是优化收益。实验分支 `codex/pr24-kv-diagnostics-20261024`，原始记录由总表与方法页导航。

## 上阶段官方受测基线

组合：队友 main + PR15 computed H2D + PR21 计算顺序 + Q fragment lifetime。

- 框架 PR22（PR15+PR21 兼容组合）已合并。
- 框架 PR23（Q fragment）已合并。
- 对应阶段的 main merge commit：`1ea082f79db65a66f78fdd7b1d958335450fa9f4`。
- 实际受测运行时 commit：`4c57567d090bbb9aec1bbc2bef7847d3b4e5695a`。
- 运行时 tree：`dd0554f3895d7ddf0691926ecd860ee1d6b3cd6c`。
- 方法说明：[Q fragment](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/main/docs/07-prefill-q-fragment-biv150.md)；聚合证据：[qfragment-pr15-pr21-final.json](analysis/qfragment-pr15-pr21-final.json)。

## 上阶段性能与准确率

原官方 4K/16K 各 4 轮，跳过首轮并使用第 2–4 轮均值：

| 负载 | PR15+PR21 | +Q fragment | 变化 | 比赛初始基线 |
|---|---:|---:|---:|---:|
| 4K | 5118.99 tok/s | **5313.59 tok/s** | **+3.80%** | 1905.46（累计 +178.86%） |
| 16K | 3436.17 tok/s | **3764.67 tok/s** | **+9.56%** | 861.99（累计 +336.74%） |

- 官方 1536 请求全部成功，两档各 4 轮验证完整。
- Math500 Level 3：`100/105 = 95.24%`，达到 `>=100/105` 门。
- 105 请求成功，0 transport error，0 空最终答案；2 题达到输出上限（index 83、101）。

原始证据：

- [官方吞吐](experiments/official/20261024T061556Z-pr15-pr21-qfragment-official)
- [完整准确率](experiments/accuracy/20261024T071802Z-pr15-pr21-qfragment)

## Q fragment 实际选中

官方和准确率服务均出现 `BIV150_Q_FRAGMENT_SELECTED`，fallback 为 0。

- Q `ttg.local_load` 位于唯一 K 循环外。
- LLVM Q shared read 共 32 次，循环内 0 次。
- normal/candidate shared memory：`65536 / 32768` bytes。
- 方法默认由提交代码启用，不依赖环境变量或外部 IR artifact；不匹配时返回已编译 normal kernel。
- normalized clone 首次未满足旧 C2/源码行假设时保留为非性能失败；修复后短诊断先出现真实选中，再进入官方测试。详见[适配记录](analysis/qfragment-adaptation.json)。

## 上阶段结果边界

- 两次官方吞吐使用相同起始 DB 种子 `1907e03…`，但候选 KV 为 `521840`，PR15+PR21 旧基线为 `521936`。这是实际组合的保守绝对对照，不包装成严格等 KV 的单项因果拆分。
- 仅验证天数 BI-V150；沐曦曦云 C500 未验证，不能复制 BI-V150 成绩。
- 准确率为单次随机 105 题评测，不解释为精度提升或稳定等价证明。
- 不修改模型、精度、量化、投机采样、benchmark 或官方 serve 参数。
- CJJ 的 #17–#20 未合入。

## 上阶段设备与仓库（历史）

- BI-V150 实验结束：GPU `68 MiB / 0%`、9031 关闭、无模型/benchmark/Engine 进程。
- 标准 tuning DB 已恢复为 `207f1bdad2e980fcddf40b8367158026332bb9c9f6e3ab2dced1246cbb0d4378`。
- 框架 main 已包含 PR22、PR23；FlagGems 本阶段无算子库内代码改动。
- 实验记录通过 PR #2 批量同步；`experiments/registry.csv` 为唯一登记源，`scripts/build_team_view.py` 生成团队视图。

后续运行状态以上方当前接续入口为准。新方法沿用 `codex/` 分支和独立 PR，不重复已验证且未变的代码测试。
