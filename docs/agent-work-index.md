# 子智能体工作与 API 接续索引

建立时间：2026-10-21 18:06（10:06 UTC）。用户明确要求子智能体所有工作留痕，供下一 API 使用。

先读根目录 [AGENTS.md](../AGENTS.md) 和 [CURRENT_WORK.md](../CURRENT_WORK.md)，再读本索引及对应子任务交接。代码、补丁和原始实验记录是证据；进度文件中的猜想不能当已验证结果。子任务的当前状态以各自文件的最后更新时间为准。

## 当前团队

**最新阶段（2026-10-22 01:53，北京时间）：** 用户已恢复持续优化，重点硬件/输入特征驱动的调度、KV 等框架创新，小收益也需最短上卡实测并保留。稳定阶段已上传、归档；新一轮正在执行。framework 负责真实 C3 覆盖缺口、CPU metadata 复用及保持采样行的 Attention 内部索引；hardware 负责固定 tile CTA 分组的边界失败诊断、已有 prefix-mask 小收益及互审；systems 负责实际 EngineCore/KV 回收机会诊断和独立证据审计。root 是唯一 GPU owner，已完成覆盖诊断、CTA 失败门、metadata 正确性门和 async 短服务，当前设备以 `CURRENT_WORK.md` 顶端及真实状态为准。新阶段结论不得倒填为旧候选的验证结果。

本阶段入口：[C3 与 metadata](../analysis/2026-10-22-c3-coverage-and-metadata.md)、[CTA 分组](../analysis/2026-10-22-mm-cta-group.md)、[调度与 KV](../analysis/2026-10-22-scheduler-kv-innovation.md)。下方“冻结/收尾/不重启”仅描述历史阶段，由本段最新授权覆盖。

**最终收尾（2026-10-22，北京时间）：** 原版官方已完整结束并验收，已无 GPU 活跃实验。framework 完成冻结候选的私有源码副本、中文报告与复现说明；hardware 完成中文分析、FlagGems 私有副本及两个代码库的离线 bundle 恢复验证；systems 完成中文实验规范、原版完整终审及分档比较，并更新现有注册表/队列。两个私有代码库已上传并核验，root 负责实验库、PDF 和离线工作包交付。下表与后续时间线保留原任务范围，不表示继续新增探索。各子任务的完整过程、最终来源版本与负结果仍见各自交接文件末尾。

| 子任务 / 角色 | 已下发工作 | 持久交接入口 | 产物与权限 |
|---|---|---|---|
| `/root/framework_innovation` / 框架实现 | 独立实现 mixed 尾块 token bucket 候选，保持真实 Attention 长度和采样行数；精确源码 guard | [framework_innovation](agent-work/framework_innovation.md) | 拟写 `patches/framework/biv150_mixed_token_bucket.py` 和实现说明；仅本地 CPU，不改冻结候选/运行器，不上 GPU |
| `/root/hardware_innovation` / 硬件与独立审阅 | 查询一手资料及本地源码，最多两项新大收益路线；审阅 bucket 实现 | [hardware_innovation](agent-work/hardware_innovation.md) | `analysis/2026-10-21-innovation-hardware.md`，精确挂点、反证及最短设备验证；仅本地 CPU/公开资料 |
| `/root/systems_innovation` / 系统、规则与实验记录 | 调度/容量/重计算等合规创新，独立审计原始结果 | [systems_innovation](agent-work/systems_innovation.md) | `analysis/2026-10-21-innovation-systems.md`；拥有 framework-experiments、registry、queue 的本轮记录更新；仅本地 CPU/公开资料 |

主负责人 `/root` 是唯一 GPU owner。设备实时归属以根 `CURRENT_WORK.md` 顶端和实际进程/显存为准；索引不复制易过期PID。任何子任务不得启动服务、benchmark、profiler 或 GPU gate。

2026-10-21 13:16Z 继续：同三位子任务已重新启用。framework 在冻结 SQL+C3 基础上核查尚未覆盖的 host/cache 重复工作；hardware 据实际 MM 源与旧真实 prefill trace准备固定 tile 的 CTA grouping 最短候选，必须交叉审阅，尚未设备验证或服务集成；systems 审团队复现入口和技术报告。原版完整官方基线仍由 root 独占设备，13:24Z 已完成 4K 四轮、进入 16K 第一轮。新发现、重复路线的纠正及原型均继续写入对应持久 handoff。

**13:30Z 用户冻结后，三位子任务均已完成收尾并停止探索。** framework 的 C3 coverage 审计和诊断设计保存在 `analysis/2026-10-21-framework-research-closeout.md`，没有新诊断脚本或实现；hardware 的 MM grouping 仅留下证据、实际源码和设计文档 `analysis/2026-10-21-mlp-cta-grouping-evidence.md`，经 framework 独立只读审阅，未执行 CPU bijection/GPU 门、未写 runtime。systems 已完成复现入口/报告审阅，等待 root 取回当前官方基线后做已有终审。恢复时不要重启这些探索；只完成在途基线、证据验收、报告和交接归档。

## 继承的团队与探索

- [上一组子智能体成果与未完成事项](agent-work/previous-team.md)：旧三位 owner 的报告、实现、审阅、验证与否定方向入口。
- [本轮派发、失败与恢复](agent-work/20261021T1006Z-dispatch.md)：模型容量失败和三个新任务的工作范围。
- [全项目框架实验记录](../analysis/2026-10-21-framework-experiments.md)、[实验注册表](../experiments/registry.csv)、[队列](../experiments/queue.md)。这些记录由新 systems owner 接续维护。
- 更早的环境、基线和算子探索见 [measurement-log](measurement-log.md)、[Attention/top-p](../analysis/2026-10-21-attention-top-p-candidates.md) 和 [analysis 索引](../analysis/README.md)。

## 每份子任务交接必须包含

1. 任务、owner、已授权范围及最后记录时间。
2. 实际读取的本地源文件/版本/位置，以及公开资料的直接 URL。
3. 中间发现、假设、反证、放弃路线及原因，区分已测与未测。
4. 已改文件、源码身份/哈希、安装方法；不能把 base revision 冒充候选完整身份。
5. 实际验证命令、run ID、原始结果路径、失败与结论。没有验证就明确写未验证。
6. 当前卡点、未解决风险、下一条可执行操作，以及由谁持有设备。
7. 最终回复与审阅结论也保存到文件；不能仅保留在子智能体聊天里。

切换 API 时不需要保留运行中的智能体进程。新会话可依据这些文件重新分派；重新启动设备工作前必须核实当前真实占用。大文件中的 `snapshot.sqlite` 被 Git 忽略但本地可能存在，使用 `Test-Path`/`pathlib` 检查，不能仅凭默认 `rg --files` 判定缺失。
