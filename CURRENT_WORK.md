# 当前工作与接续入口

## 2026-10-25 当前接续

- 526性能对照基线仍为161030：main0bf9/tree8671、SO14f、KV547536、DBfb035；官方两档各四轮、1536/0，第2–4轮5758.72/4045.20 tok/s，本实例该版本完整105仍待。
- [535 KV＋H2D](team/methods/pr25-kv-current.md)完整官方193100：4K/16K各四轮、1536成功，第2–4轮5703.70/4060.24 total tok/s，TTFT3635.20/123213.90ms，28条完整FULL链、VERIFY0。全部8轮原件保留。
- 20:29:16 UTC清理、source/native未变和DB恢复成功；实际KV546432对基线547536，比较仅actual_kv失配、gain_calculated=false、差值null。不声称单项或稳定收益；完整105尚未通过，不更换accepted baseline。
- 538 staging：203135服务VERIFY1/4题语义/34native新图通过，32请求、每向729415680字节、临时释放、DB恢复通过；非性能/105，后继筛选未纳入本批。
- RoPE首次203032记录器故障无case；203809修复后42层三个形状字节/Graph通过并有局部改善，模型验证待。末层204020因执行日志挂载守卫失败，无数值或性能结论；v2另验。
- 前序184509字节/语义验证、185439两轮筛选与原owner异常/posthoc、192645独立staging primitive均保留；primitive不包含在535官方组合内。后继设备安排由主智能体记录，下一轮未加入本批。
- 本批新增538 VERIFY1、RoPE两轮组件和末层首次日志失败四条，现235条登记/232个run；旧AOT资格撤回及历史准确率均保留。维护现有PR5，不合并main，不为发布重复测试。

以下为此前状态，以上述条目及原始run证据为准。

更新：2026-10-24。**PR25＋默认缓存身份修复已完成重启语义验证，完整性能尚待当前基线结果。** [方法记录](team/methods/native-cache-identity.md)与[框架 PR35](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/35)已关联；受测源码 `7596cc0`，PR head `35039443` 仅增加中文说明。

- `135749` 的 49 项组件门通过，但检查器误拒带 `<think>` 的正确加法响应，原 exit 1 和失败原件保留。首启运行图是在重启前首次补存，时间与来源限制保留。
- `141536` 复用上述组件证据，默认缓存重启后 4/4 语义请求正确（含 4908-token prefill），实际复用同一 AOT 与 34 层 native 图。源码/SO 未变，DB 恢复；这不是官方性能或完整准确率，也不把前序 PR24 的 100/105 自动转给本版本。
- 主智能体已运行 `142819` 当前版本完整规模两轮基线，尚无完成结果；本表暂不登记进行中任务，后续设备安排由主智能体维护。

## PR24 隔离缓存完整准确率（前序独立版本）

**PR24 同源码隔离编译缓存后，本实例真实 native 路径与完整准确率通过：100/105（95.2381%）。** 这仅适用于新 run `131603`；105037 至 124000 六轮的旧 AOT 失配资格仍撤回，不能追溯恢复为有效性能基线。详见[方法汇总](team/methods/pr24-main.md)。

- [准确率复核](experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/accuracy-review.json)：105 评审成功、0 请求错误、0 空最终答案；index 83/99/101 达到输出上限，index 101 无可提取答案，全部仍计入 105 分母。官方预测、评审、配置与报告原件均已保留；单次评测不解释为精度提升。
- [新运行图](experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/active-graph/computation_graph.py) SHA `e4ff3193…a33` 含 layer 4–37 共 34 个 native 调用，[图检查](experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/active-graph-typed-assignment-check.json)已核；源码仍为 `1ad9a708`、native SO 未变。本轮使用[隔离缓存设置](experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/environment-overrides.json)，官方 serve/评测参数不变。
- 本轮 driver/owner exit 0、DB 恢复 `207f1b…`、source/native 未变；[状态](experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/state.json)及[完整原包凭据](experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/archive-receipt.json)保留。此准确率运行不报吞吐或性能收益，结束后态不代表当前设备空闲。
- 本轮源码与后续 PR25＋缓存修复版本分别记录；后续重启语义结果见顶部，不重复本轮同源码准确率。

## 旧 AOT 图失配：历史六轮资格仍撤回

- 114500服务直接加载旧 `f7af72be36`/AOT `7a51652d…d1c`，与PR24前日志相同。[当前缓存图](experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/loaded-computation-graph.py) SHA `ab75722cd9edd5cbd33a2bb72d3f17f090eb2796ec86386d777a852f8e9cd69c` 有42层旧gate linear、native调用0；前三个M2048恢复步骤也各有168 mm和42独立SiLU。原scope仅核类方法/SO/34层计数，不能证明编译图启用native。
- 原standalone 9项数值/Graph检查通过事实保留；105037的32请求成功不等于答案正确，不能复用队友完整准确率证明本实例。110545的CPU重复提交和113346的wrapper误拒绝失败也保留。
- 114500的168次Attention共1018.292405ms仅为失配运行可见活动，**不是有效PR24模型净预算**；M457冷调优及KV差异仍成立。原[分析](analysis/pr24-resume-native-v2-114500.json)与[汇总](analysis/pr24-kv-diagnostic.json)保留历史，模型资格和下一步结论以本修正为准。
- 122225 VERIFY1仍保留R16960、每方向729415680字节一致、恢复消费者到达等[KV字节证据](experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/coverage.json)；消费者到达不证明答案正确，也不证明有效PR24组合的完整模型正确性。
- 队友PR24/25验收已显式使用 `VLLM_DISABLE_COMPILE_CACHE=1` 与独立 `TORCHINDUCTOR_CACHE_DIR`；本站漏带该既有条件。正式serve参数不改，修复须验证实际编译图与权重绑定，不能只看安装标记。
- 124000完整规模筛选因缓存失配停止：4K两轮2915.46/2941.09 tok/s、各256请求成功；16K未完成、候选未启动，不计收益。13:00:52 UTC停止driver104652，13:01:33完成该轮清理、DB恢复，source/native未变；[停止记录](experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/early-stop-request.json)、[两轮原值与退出结果](experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/result.json)、[完整原包凭据](experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/archive-receipt.json)已归档。该后态不是当前设备空闲证明；缓存身份修复及新验证由root维护。

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
