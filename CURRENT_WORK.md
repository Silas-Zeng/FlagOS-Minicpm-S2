# 当前进展：官方四轮及 Attention 后继已收口

更新：2026-10-25 09:17 UTC。本批5轮已完成，257条登记／254个run；原始结果、失败和清理证据已回收，当前没有GPU任务或自动队列。

- **连续页寻址**：原官方两档各四轮、1536请求成功，4K／16K弃首轮均值5741.68／4050.10 tok/s。相对main526仅描述−0.30%／+0.12%；KV546432对547536，未确认净收益、不定基线、不启动105。此前组件和短模型正信号保留。[方法记录](team/methods/attention-affine-pages.md)
- **next-K预取**：首次组件数值检查通过，但真实编译路径在PV前等待预取，预期重叠未形成。未计时，停止本实现，定位器问题与CPU后核分别保存。[方法记录](team/methods/attention-next-k.md)
- **GQA恒等缩放**：S16／S4两组8项数值和Graph检查通过，组件耗时分别+2.31%／+1.06%。首次B32验证器空切片失败保留；v3仅修测试器、候选数学未变。两档未见收益，不进入模型／官方。[方法记录](team/methods/gqa-identity-rescale.md)
- **准确率边界**：main526完整105仍未确认；原main与选行候选同mixed长题失败、同题串行答对，根因未定，不为候选强改框架。selected-Q模型门未启动。
- **设备终态**：09:12:55 UTC实查68 MiB／0%、9031关闭，所属进程退出，标准DB恢复。[原始回执](experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/analysis/20261025T0912Z-affine-nextk-gqa-device-final.json)

接续先看[实验总表](team/experiments.md)与对应方法；本批没有确认可合并的新优化。用户澄清：首暖初筛已有正信号时完成该组，不因后续单轮回退提前停。后续从当前实际热点选择有可信机制的方向，不自动重开已关闭负候选。已有源码、命令与原件未变的验证不用为发布重复。

## 以下为历史交接

# 阶段已收尾，停止新增任务

用户要求完成当前任务和实验、维护GitHub后停止；本阶段已结束。设备68 MiB/0%、9031关闭、所属GPU任务全部终止，标准DB恢复；[最终设备回执](archive/ai/20261025-closeout/device-state.json)。

- 固定526性能对照基线仍为5758.72/4045.20 tok/s，本实例该版本完整105仍待，不借队友/历史准确率。
- 538 staging完整四轮1536成功：5724.16/4079.71，KV失配；保留长输入信号，无确认净收益，不定新基线/105。
- RoPE v2模型短门通过，但本次性能筛选4K暖均5744.28（约−0.25%）、16K首暖4008.32（约−0.91%），6完整轮1280成功后主动早停。非完整两档四轮；KV失配，原失败/停止状态保留，不新增优化PR。
- FFN527真实mixed语义失败；失败后新prefix图只读取回，原parser跨切分拒绝，不改原语义失败。o_proj/pure-prefill/S1派生原型未上卡。
- selected-Q组件首轮TP未初始化、v2 pinned NumPy构造失败；v3四case路径/全KV字节/guard/P完成，非bitexact，数值与FP32参考原件保留。没有模型/105/吞吐资格，不自动继续。
- 框架与FlagGems本批没有可合并的新受益实现，不制造PR；实验结果与候选差分通过本实验PR保留。

现245条登记/242个run。[五份候选的可恢复源码差分与状态](archive/candidates/20261025-final-rows/README.md)已归档，未验证部分不能直接合并或套用旧准确率。不要自动重开旧队列。下文为历史记录。

# 当前工作与接续入口

## 2026-10-25 阶段收尾

- 用户要求完成当前实验、维护GitHub后停止；不再新增研究方向。
- 538完整四轮1536成功，官方均值5724.16/4079.71；KV失配，不设新基线，不追加105。
- RoPE v2真实模型门通过；后继官方由主线程收尾，本批不提前写其结果。
- FFN527真实mixed出现语义失败，已停止性能路径；衍生o_proj/S1原型保留为未验证，不因组件结果获得模型资格。
- 本批新增三条登记，共241条/238个run。设备与最后收尾状态见根CURRENT_WORK.md；下文保留历史。

## 2026-10-25 当前接续

- 526性能对照基线仍为161030：main0bf9/tree8671、SO14f、KV547536、DBfb035；官方两档各四轮、1536/0，第2–4轮5758.72/4045.20 tok/s，本实例该版本完整105仍待。
- [535 KV＋H2D](team/methods/pr25-kv-current.md)完整官方193100：4K/16K各四轮、1536成功，第2–4轮5703.70/4060.24 total tok/s，TTFT3635.20/123213.90ms，28条完整FULL链、VERIFY0。全部8轮原件保留。
- 20:29:16 UTC清理、source/native未变和DB恢复成功；实际KV546432对基线547536，比较仅actual_kv失配、gain_calculated=false、差值null。不声称单项或稳定收益；完整105尚未通过，不更换accepted baseline。
- 538的204402两轮筛选已回收：4K5544.36/5615.02、16K3845.32/4078.31，768成功；暖轮对526 R2仅观察−2.38%/＋0.82%，KV546528≠547536、非因果。source/native与DB恢复通过，后续官方运行不纳入本批，也不更换基线。
- 末层211402 logger-v2四shape逐bit/变输入Graph通过；M2048→S32/64的Graph总wall约2.386→0.170/2.397→0.183ms，只是组件、不含后继dense回填和新编译入口。保留进入模型验证；204020日志失败原件保留。
- RoPE模型211606四语义正确，但跨submod图门误拒且source目录新增.best_config，原source_unchanged=false/completed=false/exit1保留；DB恢复、native未变。后续修复需新服务门，CPU回放不追溯恢复资格。此前RoPE组件与首次记录失败均保留。
- 本批仅新增上述三轮，现238条登记/235个run；原235条登记逐字前缀保持。维护现有PR5，不合并main，不为发布重复测试；当前设备状态由根CURRENT_WORK.md统一记录。

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
