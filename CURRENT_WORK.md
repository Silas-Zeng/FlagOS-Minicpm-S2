# 当前工作与 API 接续

## 已完成

- GitHub 框架 main 已恢复比赛原始源码13eb9be，恢复提交77bc2488；旧SQL+C3导入快照保存在codex/archive/sql-c3-imported-20261022，未强制改历史。本地完整实验版本保留。
- 原有改动已拆PR：#5诊断支持→#6 prefill→#7 top-p→#8 SQL→#9 3D decode→#10 mixed。CPU #1/#2依赖#10，原受测head不变；KV #3/#4独立指向main。十项均Draft、未合并。精确回执见[GitHub归档](archive/github/20261022-framework-rebuild.json)。
- CPU组合070004/070452短测完成，两轮64成功/0失败、同KV521936/同DB，吞吐单轮+0.6986%、平均TTFT−0.1250%；保留待确认，未补整模型准确率。两CPU PR已附中文结果。关停EngineDeadError和一次DB快照误比均已留原件，不能写成日志无异常。
- 设备最后后态07:07:32Z为68MiB/0%、9031双闭、无GPU进程；现在没有本任务新GPU作业。下一次启动仍需实时查空闲。

## 团队入口

实验记录库现名为 `Silas-Zeng/FlagOS-Minicpm-S2`（GitHub ID 1427279927），原名 `FlagOS-S2-Minicpm-throughput` 的链接仍重定向。2026-10-22 本轮首次发布在名称校验处停止、未写入；适配现名后重新发布，保持三个协作库分工。

[实验总表](team/experiments.md) → [按方法与平台查阅](team/README.md) → 每轮短记与原始证据。registry是唯一登记源，python scripts/build_team_view.py生成团队视图。README只负责导航及当前有效结果，详细历史从[归档入口](archive/README.md)查阅。

本地团队整理已保存；用户已要求清理过时、冲突的规则并继续合理维护。AGENTS.md 已统一为：官方上游及参考 fork 只读，三个实验专用私有库正常协作；代码改动按方法 PR 呈现，记录库阶段末批量更新，不创建重复仓库。本阶段发布状态文件为 `tmp/publish-team-rebuild-final-20261022.json`。只有 `published_commit` 存在、`verified_tree/entries` 与来源一致且进程退出 0，才算发布完成；计划或中间状态不代表成功。

## 当前并行工作与下一步

- root收尾摘要显示修正后批量发布团队视图，不再逐份改写旧报告。
- framework与hardware正在CPU侧准备严格guard的Attention热launch复用候选，先核实际Corex JIT/CompiledKernel/stream/hooks/globals语义，再最小复用已有两形状正确性和ABBA门。尚未部署或上卡，收益未知；get_corex_sme并非热命中重复成本。
- systems维护自动团队视图，已验source/DB等结论复用，不重跑旧套件。
- 单卡实验仍由root唯一负责，始终串行。代码版本/命令/环境/原始结果自动保存，结论、失败原因、下一步只写几句话；阶段结束批量报告/PR，设备运行时CPU准备下一项。
- 所有维护说明与PR保持自然中文，英文专有名词、命令与原证据原样保留；BI-V150与C500证据分别报告。未确认准确率的组合不冒称最终提交资格。

[完整旧交接原文](archive/ai/CURRENT_WORK-before-team-rebuild-20261022.md)保留，旧文中的相对路径以项目根目录为基准；它是历史，当前安排以本页为准。
