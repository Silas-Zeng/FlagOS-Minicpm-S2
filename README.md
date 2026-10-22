# FlagOS 第二季 MiniCPM5-2B 双平台实验

团队主要看：**尝试了什么、改了什么、怎么测、结果怎样、是否保留。**

- **[实验总表](team/experiments.md)**：唯一登记视图，包含成功、失败与待确认项。
- **[按方法查阅](team/README.md)**：同一方法的实验集中展示，每轮短记链接代码、命令和原始结果。
- 硬件入口：[天数 BI-V150](team/platforms/bi-v150.md) · [沐曦－曦云 C500](team/platforms/c500.md)。

## 三个仓库各管什么

| 仓库 | 团队查看内容 |
|---|---|
| [vllm-plugin-FL](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL) | 比赛原始框架＋按方法拆分的PR；main已恢复原始源码，未合并优化不属于main |
| [FlagGems](https://github.com/Silas-Zeng/FlagGems) | 比赛指定算子代码＋实际发生的算子改动PR；目前没有新增库内算子实现 |
| 本实验库 | 实验总表、方法记录、每轮短记和原始证据；按硬件区分 |

框架PR的顺序和依赖见[协作安排](docs/pr-collaboration-plan.md)。PR正文链接方法记录，所有维护说明使用自然中文，英文专有名词和代码标识保留。

## 当前结果

| 方法 / 版本 | 结果与处理 |
|---|---|
| BI-V150历史SQL+C3完整组合 | 官方准确率103/105，完整两档吞吐已留档；这些结果只属于该历史组合，DB/KV对照限制见[原报告](docs/technical-report.md)。当前以方法PR重新呈现，尚未合入新main |
| [CPU metadata＋async token](team/methods/cpu-combination.md) | 两轮64/0、同KV与DB，单轮吞吐+0.6986%、平均TTFT−0.1250%；保留待确认，未做新整模型准确率 |
| [KV复制](team/methods/kv-pitched.md) | 字节正确性和局部成本信号已记录，尚无稳定端到端收益；工具保留Draft |
| 沐曦－曦云C500 | 由该平台队友补充环境与实测，不能套用BI-V150结果 |

原始日志与环境文件保留在experiments/，从短记进入即可；不需要先读审计过程。早期未证实、放弃或失败的方法仍在总表中。

[当前工作](CURRENT_WORK.md) · [协作规范](AGENTS.md) · [AI交接、详细清单与历史过程归档](archive/README.md)

每轮复用启动器自动留原件，简写结论与下一步；完整技术报告和GitHub更新在阶段结束批量处理。
