# 子智能体工作与 API 接续索引

**最新阶段（2026-10-22 05:08，北京时间）：** 本批GPU全结束。204159已通过真实私有页排序/42层回读；205219基线与205819不回读候选都32/0，但候选KV少96且DB新增1表3行，不能报可归因收益。framework已独立核全部源/DB/真实恢复/后态，hardware复算实际1043页66段并排除没有证据的profile归因，systems维护注册表/失败边界。capacity67e4独立实现、唯一CPU合同及a79b/0ae隔离包装均已互审，尚未上卡；旧0e/worker/事务不改。三agent收口后暂时停写供root一致发布/完整ZIP，持续优化目标仍有效，后继先读[本阶段交接](../analysis/2026-10-22-kv-framework-milestone.md)与CURRENT顶端。

**当前阶段（2026-10-22 04:50，北京时间）：** 204159真实私有页排序门已完成；framework独立验收source416、DB三SHA、完整恢复/回读/消费者与空闲后态，hardware独立复算66段和每阶段2772调用，systems保存注册表和后继容量早退方案。当前0e2115仍为唯一受测实现，227.55秒属于VERIFY1诊断。framework准备关闭额外回读的原参数短服务配对包装，hardware互审；root串行上卡。后继容量必要条件早退、省ZERO完整覆盖恢复都仅为研究，不能混成已测收益。原件与三角色过程均保存在本地；远端发布/离线包覆盖边界读CURRENT顶端。

建立时间：2026-10-21 18:06（10:06 UTC）。用户明确要求子智能体所有工作留痕，供下一 API 使用。

先读根目录 [AGENTS.md](../AGENTS.md) 和 [CURRENT_WORK.md](../CURRENT_WORK.md)，再读本索引及对应子任务交接。代码、补丁和原始实验记录是证据；进度文件中的猜想不能当已验证结果。子任务的当前状态以各自文件的最后更新时间为准。

## 当前团队

**当前阶段（2026-10-22 04:27，北京时间）：** 200957真实SAVE已完成685.125MiB，但副本随后被丢弃，没有恢复；全原件与独立验收已发布实验库76e94。systems据负例最小修正暂态保留，framework/hardware完成互审；root唯一GPU执行202526新诊断，精确PID/版本与后态读CURRENT顶端。framework继续只读审[碎片前缀选择设计](../analysis/2026-10-22-kv-fragment-aware-prefix-plan.md)，systems核实际准入容量，hardware的预算/碎片审计与一手资料已落盘。后继设计不混入当前受测版本，两个代码仓库仍只改本地。

**当前阶段（2026-10-22 03:56，北京时间）：** 持续优化已恢复，旧阶段归档锁已解除。root串行完成195012真实KV/executor最短smoke，framework独立验收通过，设备已空闲。实际为42层独立normal KV、UniProcExecutor、AsyncScheduler/queue2，完整证据见[运行时布局观察](../analysis/2026-10-22-kv-runtime-descriptor.md)。framework现实现独立worker保存/清零/恢复模块，systems实现单victim事务和调度/V2 resume适配，hardware独立审接口及硬件预算；三者仅CPU，后续唯一GPU门仍由root负责。两个共享代码库先本地更改，实验记录库继续发布；既有小收益、负结果不删除。

**最新完成状态（2026-10-22 03:26，北京时间）：** 本批所有设备作业已完成且空闲后态通过；三位 agent 的实现、复核、负结果与下一操作都已落盘，并暂停写入供统一归档。mapped 首轮121.79秒/复核117.03秒并列保留，KV容量差与稳定性限制不省略；prefix 首次服务负结果保留；KV修正版四case byte/event门通过，但生产恢复协议尚未实现。原件及审计已提交本地 `98f208fd6f37e4f1f654b3a492174f65e430512e`，tree `e88738bfc30ff12848e366f0b9e5904934ed2139`，10,431项；远端发布和离线包最终身份见 CURRENT 顶端及发布回执。

快速读 [阶段记录](../analysis/2026-10-22-framework-milestone.md)，再读 [下一框架优先项](../analysis/2026-10-22-next-framework-priority.md)。恢复时先核实际设备状态，下一切口为运行时 KV 布局/executor 证据与安全抢占恢复协议；用户持续探索授权有效，本批暂停写入仅为一致归档，不是用户取消探索。

**最新阶段（2026-10-22 03:14，北京时间）：** root 按单卡串行完成 mapped 正确性/单层计时、真实服务及 prefix 真实服务；两项首次服务均为负信号，原件保留，未集成。mapped 原代码一次复核在途，KV 页复制门因归档 `copy.py` 遮蔽标准库在加载阶段失败，最小重命名已完成双人互审，等待串行重试。当前 PID 读 CURRENT 顶端。framework 继续实际输入/16SM 下的下一调度与执行方向分析；hardware 独立审 prefix 和 KV 包装；systems 维护 KV 实现、记录及独立实验审计。已有 d756 本地检查点/bundle，最新工作尚未全部同步 GitHub；不能把29ad远端或旧ZIP称为本轮全量。

新增入口：[mapped 与真实覆盖](../analysis/2026-10-22-c3-coverage-and-metadata.md)、[prefix 服务](../analysis/2026-10-22-visible-prefix-service.md)、[KV 页复制门](../analysis/2026-10-22-kv-page-copy-gate.md)、[调度/KV 状态机研究](../analysis/2026-10-22-scheduler-kv-innovation.md)。

**最新阶段（2026-10-22 02:38，北京时间）：** 已完成阶段本地759f/远端29ad完整tree相同，私有实验库7445项核验通过。root继续独占GPU，已完成gate-up真实服务、mapped首门编译失败留档，当前实际作业读CURRENT顶端。framework定位mapped派生内核的实际编译入口；hardware审CTA真实编译证据及准备prefix-mask独立入口；systems独立审服务pair，并推进抢占KV保存/恢复的真实源码与成本门。所有失败、假设和未集成代码保留；不能用单层正信号替代服务收益/accuracy。

本阶段新增入口：[gate-up服务](../analysis/2026-10-22-mm-cta-group-service.md)、[小框架短测](../analysis/2026-10-22-small-framework-comparison.md)、[新阶段GitHub回执](github-research-publication-20261022.json)。下方状态为历史，不是仍在运行的作业。

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
