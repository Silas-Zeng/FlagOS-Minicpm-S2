# FlagOS 第二季 MiniCPM5-2B 双平台实验

团队主要看：**尝试了什么、改了什么、怎么测、结果怎样、是否保留。**

- **[实验总表](team/experiments.md)**：唯一登记视图，包含成功、失败与待确认项。
- **[按方法查阅](team/README.md)**：同一方法的实验集中展示，每轮短记链接代码、命令和原始结果。
- 硬件入口：[天数 BI-V150](team/platforms/bi-v150.md) · [沐曦－曦云 C500](team/platforms/c500.md)。

## 三个仓库各管什么

| 仓库 | 团队查看内容 |
|---|---|
| [vllm-plugin-FL](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL) | 比赛原始框架＋按方法拆分的 PR；十项方法已按依赖合并，后续代码和维护继续通过 PR |
| [FlagGems](https://github.com/Silas-Zeng/FlagGems) | 比赛指定算子代码＋实际发生的算子改动PR；目前没有新增库内算子实现 |
| 本实验库 | 实验总表、方法记录、每轮短记和原始证据；按硬件区分 |

框架PR的顺序和依赖见[协作安排](docs/pr-collaboration-plan.md)。PR正文链接方法记录，所有维护说明使用自然中文，英文专有名词和代码标识保留。

## 当前结果

| 方法 / 版本 | 结果与处理 |
|---|---|
| BI-V150历史SQL+C3完整组合 | 官方准确率103/105，完整两档吞吐已留档；这些结果只属于该历史组合，DB/KV对照限制见[原报告](docs/technical-report.md)。对应方法已合并，不能把历史准确率自动赋予新增 CPU 组合 |
| [CPU metadata＋async token](team/methods/cpu-combination.md) | 两轮64/0、同KV与DB，单轮吞吐+0.6986%、平均TTFT−0.1250%，性能信号保留待确认；完整Math500 Level 3准确率102/105（97.1429%），通过 |
| [Q fragment循环外保留](team/methods/q-fragment-hoist.md) | 单轮可比短服务吞吐+1.7113%、TTFT+1.3185%、TPOT−5.3841%；Math500 Level 3为101/105（96.1905%），1题到输出上限，通过95%门。保留候选交接，尚不报稳定或完整官方性能收益 |
| [C3重复视图清理](team/methods/c3-views.md) | 短输入单层耗时降低5.97%；真实服务仅表观+0.0177%且KV容量失配，未确认端到端收益，保留局部候选 |
| [输入准备等待](team/methods/input-prep.md) | 4K短负载与16K长输出的部分累计中，等待占预处理均低于0.1%；暂不优先改造此处同步。诊断不计吞吐收益 |
| [KV复制](team/methods/kv-pitched.md) | 字节正确性和局部成本信号已记录，尚无稳定端到端收益；工具已合并，仍需显式调用，未启用 KV offload |
| 沐曦－曦云C500 | 由该平台队友补充环境与实测，不能套用BI-V150结果 |

当前主线是 **KV管理、请求调度、批处理与硬件及现有算子的配合**；算子优化由队友负责。已有[GPU热点](team/methods/gpu-hotspots.md)轨迹继续作为依据；必要时补最短诊断，先量清实际重算或浪费，再决定改动。CPU小收益作为并行补充。

最新8轮已留存：V-late及其cache偏好组合均无收益；末层尾段裁剪未过严格数值门，暂停。两个长基线因DB/KV条件不同不能配对比较。后继候选先根据实际硬件和开销判断收益，再决定是否上卡，详见实验总表。

原始日志与环境文件保留在experiments/，从短记进入即可；不需要先读审计过程。早期未证实、放弃或失败的方法仍在总表中。

[当前工作](CURRENT_WORK.md) · [协作规范](AGENTS.md) · [AI交接、详细清单与历史过程归档](archive/README.md)

每轮复用启动器自动留原件，简写结论与下一步；完整技术报告和GitHub更新在阶段结束批量处理。
