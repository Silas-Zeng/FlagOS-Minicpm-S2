# FlagOS 第二季 MiniCPM5-2B 双平台协作

四项独立中文 Draft PR 已创建：[CPU metadata #1](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/1)、[async token #2](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/2)、[KV连续页 #3](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/3)、[KV二维SAVE #4](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/4)。均未合并；两个CPU方法的import冲突已有双向解决补丁，详见协作安排。

本仓库是团队的实验记录与交接总入口，覆盖 **天数 BI-V150** 和 **沐曦－曦云 C500**。本实验库按平台分别维护环境、分析、验证结果和中文报告；框架和算子代码在另外两个团队共用代码库中协作。

| 平台 | 负责人 | 当前证据与进度 | 入口 |
|---|---|---|---|
| 天数 BI-V150 | 本轮主智能体及对应团队成员 | SQL+C3 准确率 103/105；原版与候选官方两档均已完成并验收 | [BI-V150](platforms/iluvatar-bi-v150/README.md) |
| 沐曦－曦云 C500 | 另一位队友 | 等待队友提交本平台的环境、代码版本和验证结果 | [C500](platforms/metax-c500/README.md) |

截至本次整理，仓库既有 `experiments/`、`analysis/` 中的设备实测数据均来自 BI-V150，历史路径保留。C500 后续资料放入自己的平台目录，并在实验记录中填写平台标识。跨平台数值分别报告；团队总分仅按主办方明确的公式计算。

## 三个协作仓库

- [FlagOS-S2-Minicpm-throughput](https://github.com/Silas-Zeng/FlagOS-S2-Minicpm-throughput)：本仓库，保存实验记录、补丁、结果、中文报告和交接文档，已为私有。
- [FlagOS-S2-vllm-plugin-FL](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL)：团队共用的框架代码库，独立私有副本，完整候选已上传并核验 410 项 Git 文件与模式。
- [FlagGems](https://github.com/Silas-Zeng/FlagGems)：固定 `v5.3.5` 的团队共用算子库，私有，已上传并核验 4,769 项 Git 文件与模式。

两个代码库共用，不要求按平台拆分目录或分支。修改提交到我们自己的私有协作副本，官方上游只读；原公开 [vllm-plugin-FL fork](https://github.com/Silas-Zeng/vllm-plugin-FL) 按用户选择保留。两位协作者的邀请待用户名确认。每个平台的实测证据在本实验库分别记录，不能互相替代。

## 接续工作

切换 API 或加入协作时，先读 [CURRENT_WORK.md](CURRENT_WORK.md)、[协作规范](AGENTS.md) 和 [子智能体交接索引](docs/agent-work-index.md)。2026-10-22 本轮手头设备实验已结束，现转入 GitHub 协作整理，暂不新增实验。已验证小收益和负结果全部保留，代码按方法拆分草稿 PR，合并前核对各自验证范围和组合边界。

当前代码库主分支曾一次性导入完整 SQL+C3 候选，包含下方列出的多项优化；这不代表此前已通过多个 PR 分别合并。新增方法的 PR 与历史组合版本分开记录，主分支中的旧方法不重复提交。

- 最近的 KV 二维复制门保留局部成本改善；真实42层 SAVE 与原 FULL 恢复均通过完整字节检查，尚不作为新官方吞吐或准确率结果。
- 两轮 Event 对比均通过完成性检查，但 typed blocking 和直接 Corex blocking 都未降低等待线程 CPU，按负结果结束，不作为生产优化加入代码 PR。
- 框架草稿 PR 的范围、依赖与合并步骤统一记录于 [方法与协作安排](docs/pr-collaboration-plan.md)。

- [团队交接](docs/team-github-handoff.md)
- [BI-V150 技术报告](docs/technical-report.md)
- [候选安装与复现](docs/candidate-usage.md)
- [比赛规则核实](docs/official-verification.md)
- [离线恢复说明](docs/offline-recovery.md)

## BI-V150 当前冻结候选

在官方插件基点 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0` 上一次应用 [完整 SQL+C3 补丁](patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch)。SHA256 为 `4aba147aa0bd3ec8dd1c12b6ae94bf39537a4cbad449e68e2fcdbfbdc0f8def6`。它包括 SQLite 目标表反射、3D decode launch、mixed Attention 分流，以及已保留的 prefill 与确定性 top-p 实现。

已通过官方 Level 3 准确率 **103/105（98.0952%）**，请求与评估全部成功。按原官方脚本每档四轮、去掉首轮，完整对照如下：

| 档位 | 原版 total tokens/s | 候选 total tokens/s | 本次吞吐比值 |
|---|---:|---:|---:|
| 4K / 1024 output | 1905.46 | 3683.65 | 1.9332×（+93.32%） |
| 16K / 1024 output | 861.99 | 2729.07 | 3.1660×（+216.60%） |

两组初始调优数据库不同；原版 KV 为 521840 tokens，候选为 521936 tokens。以上是本次官方协议下的分档描述性比较，不能称为缓存完全匹配的稳定因果增益，也不是比赛总分。完整限制与原件见 [中文技术报告](docs/technical-report.md) 和 [比较结果](analysis/2026-10-21-official-final-comparison.json)。全部成绩仅适用于 BI-V150。

旧补丁、失败和未集成原型均保留。单层计时和安装标记不能代替端到端性能与准确率；提交候选的实际启用代码必须与报告对应。

## 资料结构与比赛约束

- `platforms/`：按硬件平台组织入口和队友新增材料。
- `docs/`：中文规则、环境、方法、报告与交接文档。
- `scripts/`：本地整理及远端实验脚本。
- `experiments/`：已有 BI-V150 原始实验与注册表。
- `analysis/`：已有 BI-V150 瓶颈分析、资料研究与负结果。
- `patches/`：冻结候选及历史增量。

仅使用 MiniCPM5-2B、比赛指定框架基点和 FlagGems `v5.3.5`，保持官方服务参数和评测脚本，不通过参数开启现有量化或推测解码，不为性能合并新框架分支。原始源码、日志、CSV、命令和许可证保留原文；本项目维护的说明使用自然中文，专有名词保持原名。

大体积 SQLite、trace、完整工作 ZIP 和 Git 恢复 bundle 独立保存，不能仅靠 GitHub 的文本记录替代。任何设备操作前都要实时确认该平台的负责人、进程和显存状态。
