# 当前工作与 API 接续

## 已完成

- 用户已明确要求按依赖合并并复用既有验证。框架十项 PR 已按 #5→#6→#7→#8→#9→#10→#1→#2→#3→#4 合并；#11 仅更新中文 README。当前 main：`87ed53719126208eaa9ba1cab698b14a5693eb5d`。官方上游和原公开 fork 未改，旧快照与本地实验版本保留。
- #1/#2 的 runner 冲突使用已验证组合 `6f918ae6…`，保留两 helper、回退及 SQL→C2→C3。代码合并提交 0f2b9255 的全部 425 文件与预期组件组合相同，未重复测试。精确提交、双亲冲突解决及最终身份见[合并回执](archive/github/20261022-framework-merge.json)。后续代码与文档维护均通过 PR，不直接写 main。
- CPU组合070004/070452短测完成，两轮64成功/0失败、同KV521936/同DB，吞吐单轮+0.6986%、平均TTFT−0.1250%；保留待确认，未补整模型准确率。两CPU PR已附中文结果。关停EngineDeadError和一次DB快照误比均已留原件，不能写成日志无异常。
- 新一轮已收尾：085923 hot-key 门输出/KV/RNG正确但未命中，100149诊断确认默认 HookChain 对象被误当作非空 hook 拒绝；均 exit1、没有性能结论。100830 CPU组合短测64/0、38.867665s、6955.2931 tok/s，10:10:29Z exit0；随后用户要求直接合并，未再跑反序基线，不能据此形成新配对收益。三轮原件和校验包均已回收至本地 experiments/framework/，待下一实验记录批次发布。
- 本轮设备后态已核为68MiB/0%、9031双闭、无GPU进程；现在无本任务设备作业。下一次启动仍需实时查空闲。

## 团队入口

实验记录库现名为 `Silas-Zeng/FlagOS-Minicpm-S2`（GitHub ID 1427279927），原名 `FlagOS-S2-Minicpm-throughput` 的链接仍重定向。2026-10-22 本轮首次发布在名称校验处停止、未写入；适配现名后重新发布，保持三个协作库分工。

[实验总表](team/experiments.md) → [按方法与平台查阅](team/README.md) → 每轮短记与原始证据。registry是唯一登记源，python scripts/build_team_view.py生成团队视图。README只负责导航及当前有效结果，详细历史从[归档入口](archive/README.md)查阅。

团队整理已发布为实验库提交 `7362fee812b786bb38a757a3b644ca21c33d4b68`，21810 项与来源 tree 完全一致；回执为 `tmp/publish-team-rebuild-final-20261022.json`。最新合并状态与协作规则通过单独的记录库维护 PR 同步，不创建重复仓库。

## 当前并行工作与下一步

- root已完成框架 PR 合并，收尾本地证据和本次维护说明，不重复上卡验证。
- 待后续设备队列（均未上卡的新版本）：`tmp/hot-key-v2/README.md`（a67d3add policy / 1f402c6d gate，只复用 key/cache，原 hook/launch 尾保持）；`tmp/input-prep-timing/README.md`（真实输入准备等待成本诊断，不能把诊断 TPS 当收益）；`tmp/next-c3-views/README.md`（ba085577 policy / e5eef652 gate，独立去重复 view，不叠 hot-key）。CPU 合同及定向互审已留各目录；不将其混入刚合并的十项 PR。
- 子智能体已收口保存接续信息；新方法按适用输入大小判断，有依据就用对应最短负载实测，小收益保留，未变的验证复用。
- 单卡实验仍由root唯一负责，始终串行。代码版本/命令/环境/原始结果自动保存，结论、失败原因、下一步只写几句话；阶段结束批量报告/PR，设备运行时CPU准备下一项。
- 所有维护说明与PR保持自然中文，英文专有名词、命令与原证据原样保留；BI-V150与C500证据分别报告。未确认准确率的组合不冒称最终提交资格。

[完整旧交接原文](archive/ai/CURRENT_WORK-before-team-rebuild-20261022.md)保留，旧文中的相对路径以项目根目录为基准；它是历史，当前安排以本页为准。
