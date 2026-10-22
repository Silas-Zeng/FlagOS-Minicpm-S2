# 团队 GitHub 协作交接节点

本轮四项中文 Draft PR #1—#4 已实际创建，均未合并，代码main保持原基点。精确链接与合并材料见[方法协作安排](pr-collaboration-plan.md)。所有原件与子智能体记录完整保存；本轮实验仓库发布身份见[回执](github-publications/20261022-pr-maintenance.json)。

## 2026-10-22 本轮转入按方法协作

手头设备实验已全部结束；最后的两轮 Event 对照完成性通过但未见等待 CPU 下降，保留负结果，暂不新增实验。GitHub 三个专用仓库仍为私有，官方上游和原公开 fork 保持只读。新增代码按方法准备中文草稿 PR，默认入口和正式成绩仍以已经验收的 SQL+C3 基点为准。

当前主分支是此前一次性导入的组合代码，并不是多个 PR 分别合并后的历史。其组成与精确版本见[当前版本组成](current-version-composition.md)；新 PR 的范围、依赖、合并与验证安排见[方法协作安排](pr-collaboration-plan.md)。下方内容保留此前交付阶段的证据和历史状态。

## 当前交接状态（2026-10-22，北京时间）

用户已授权上传团队协作，现有原版与候选官方测量均已完成并独立验收，不再等待设备实验。三个仓库均为私有：本实验库按 BI-V150 / 沐曦－曦云 C500 分开整理分析与报告，`FlagOS-S2-vllm-plugin-FL` 和 `FlagGems` 是团队共用代码库，不要求按平台拆分。两个代码库完整源码已上传并核验，原公开 fork 保留、官方上游不修改。精确远端 commit、tree 和接入方式见 [GitHub 协作说明](github-collaboration.md)。两位协作者的用户名仍待提供，尚未发出邀请。

BI-V150 本次原版→候选的 4K 吞吐为 1905.46→3683.65 total tok/s，16K 为 861.9867→2729.0733；分档比值 1.9332× / 3.1660×。准确率 103/105。初始 DB 和真实 KV 存在差异，不能声称缓存完全匹配或合成比赛总分。中文报告和完整边界见 [技术报告](technical-report.md)。C500 尚无测量资料，不继承 BI-V150 的结果。

原版 225 项归档与 live 源码核验通过，已取回全 run/control；设备 68 MiB / 0%，9031 关闭且无 GPU 进程。runner 是已退出但 PID 1 尚未回收的 Z 状态；首次封存对 `/proc` 不存在的过严断言及后续实际状态核验都保留。离线工作包还包含 Git 忽略的数据库和历史材料。本轮材料交团队审阅与干净环境复现；用户随后已恢复持续优化，后续方案另建实验记录，不覆盖这一稳定基点。

## 早期交接准备快照（2026-10-21 12:58 UTC）

以下保留当时的准备过程，“在途”“未上传”仅指该时间点，当前状态以上节为准。

建议：原版完整官方对照结束、原始结果验收并写出两档结论后，就把当前候选交给团队审阅与独立复现。不必等所有探索结束。现在即可审阅候选源码；正式合并和比赛成绩声明仍需复现成立。

## 已能交给团队的内容

- 已验证候选：原保留 prefill/top-p，加 SQL 目标表反射、3D decode launch、mixed Attention 分流。完整补丁为 [sql-mixed-decode-full.patch](../patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch)，SHA256 `4aba147aa0bd3ec8dd1c12b6ae94bf39537a4cbad449e68e2fcdbfbdc0f8def6`，基于原始 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`。
- 独立包装审阅通过：一步应用与原两补丁叠加结果一致，212 份归档源码匹配；文件模式、MoE symlink 保持，逆向精确回到原始 Git tree。详见 [完整补丁说明](../analysis/2026-10-21-sql-mixed-full-package.md)。包装不是性能验证。
- 精确官方准确率：run `20261021T090505Z-sql-mixed-level3`，103/105，零请求错误、零截断。完整补丁重建出的候选源码与受测源码对应，不包含本轮未集成原型。
- 优化版完整官方吞吐：run `20261021T092944Z-sql-mixed-official`，两档各 4 轮、剔除首轮，4K 为 3683.65 total tok/s，16K 为 2729.07 total tok/s；8 条原始记录、2 条汇总及源文件已独立验收。这些目前是绝对结果，尚不构成总体提升幅度。
- 重大经验、失败、原型与子智能体工作入口：[CURRENT_WORK](../CURRENT_WORK.md)、[agent-work-index](agent-work-index.md)、[实验注册表](../experiments/registry.csv)。

## 本轮交接前剩余工作

1. 等唯一在途原版 `20261021T122607Z-original-baseline` 跑完官方两档各 4 轮。12:57 UTC 实查已完成 4K 两轮，开始 3/4；16K 尚未开始。不能将中途 CSV 当最终基线。
2. 验收 8 条原始记录和 2 条汇总、请求/token、源码与依赖、DB/KV 状态及服务清理；完整证据取回本地。只报告官方原 2–4 轮均值的两档比较，不发明总体计分公式。两轮 DB 初始状态不同须明示，不能宣称缓存完全匹配。只读本地入口已备好，见 [official-comparison](official-comparison.md)；唯一 CPU smoke 对真实未完成基线返回 pending、没有计算收益，完整成功分支仍待两份完整证据验收。
3. 在同一份复现说明中给出原版与候选的源码身份、环境、安装和原命令，以及已测结果/限制。团队从干净环境应用补丁独立复现，再决定合并。

## 团队分工与重大注意点

- 框架负责人：SQL 反射、mixed metadata/执行路径、完整吞吐与统计；算子负责人：prefill/top-p/decode launch 的精度和适用范围，互审最终代码。
- 当前一张 BI-V150 仍由主负责人独占；团队可并行审代码和准备脚本，实际设备实验串行安排。
- 原候选 runtime 会持久改写已安装 Attention，插件目录隔离不足以隔离依赖。原版必须维持原始 Attention SHA `bab2c0b9f9a7793ca411796b48ebb4734433160e7e99eabf46ddb7f1c30cb6e0`；原版测试期间禁止导入 retained/C3 平台模块。备份和恢复证据见 [dependency plan](../analysis/2026-10-21-original-baseline-dependency-plan.md)。
- bucket、hidden gather、growth V2、双 stream overlap、prefix-mask 均独立留档，尚未集成到交接候选；其中只有 prefix-mask 的小幅单层信号，不能写成整模型收益。
- 按 AGENTS.md，既有参考仓库只读；发布仅使用本实验新建专用仓库。大体积原始数据保留路径、校验和与可取回位置，凭据和私钥绝不入库。
