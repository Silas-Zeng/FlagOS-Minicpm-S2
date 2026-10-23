# 当前工作与 API 接续

更新：2026-10-24（北京时间）。本轮按用户要求收尾，**停止启动新任务，等待用户继续指示**。接续已有成果，不从头探索。团队入口：[实验总表](team/experiments.md)、[计算顺序方法](team/methods/compute-order.md)；历史过程：[上一版交接](archive/ai/CURRENT_WORK-through-20261023T1523Z.md)。

## 已完成及结果

当前组合：队友main `3283672b`（含prefill normalization）＋计算顺序两文件，commit `4fca58bad0c7e3ed73e59ed2c7749bb2511b6813`，tree `5c77e68caff6aa0c8b6c230adb78a2d4c293cca1`，完整446项。已建[Draft PR #21](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/21)，未合并；[补丁与精确来源](archive/ai/20261022-framework-kv/compute-order-main-profile/)、[分支回执](archive/ai/20261022-framework-kv/compute-order-pr/branch-receipt.json)。

原105题准确率 `142019`：**103/105（98.0952%）**，达到95%门；105请求成功、无空最终答案，index83一次达到原输出上限。**P分支零命中**，不能声称P分支完整准确率已验证。[摘要及原件](analysis/compute-order-current-main-accuracy.json)。

原官方 `20261023T144620Z-current-main-compute-order-official` 已于15:52 UTC完成，exit0；两case各4轮全部SUCCESS、1536请求成功。沿用原第2–4轮均值，没有重算或重复测试。

| 负载 | Total tok/s | TTFT ms | TPOT ms |
|---|---:|---:|---:|
| 4K / 输出1024 / c64 / 256请求 | 5116.68 | 4580.19 | 57.74 |
| 16K / 输出1024 / c64 / 128请求 | 3436.04 | 152082.85 | 130.38 |

官方实际P命中N62/M2048/outside59，normalization同时选择；只是路径覆盖，不是准确率证明。725原件逐项核、726导入，原tgz SHA `9fdc3e046a727adcf3eddd627d1182dd22156c62a625e16767c8ee7b04fd235a`。DB567/20986→569/21053如实保留。[官方摘要及原CSV](analysis/compute-order-current-main-official.json)、[封存导入回执](archive/ai/20261022-framework-kv/current-main-combined-official/)。

## 保留、限制与下一步

- **保留计算顺序Draft候选**。当前短pair表观+6.59%，但KV521840→521936，`gain=null`；官方单臂只有绝对成绩，不与旧组合或队友单轮归因比较。P完整准确率覆盖、稳定收益仍未确认。[原短对照](analysis/compute-order-current-main-pair.json)。旧423单pair+5.124857%和三题质量是历史证据，不能替代当前结果。
- Draft #15 computed H2D保留独立方法，未叠入当前446；100/105与历史小收益见[已有记录](analysis/pr15-computed-h2d-accuracy.json)。KV pitched-SAVE/linear-FULL等历史小收益、负结果沿总表保留，不累加收益。
- 队友[PR #20](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/20)处理残余混合Attention，与P作用路径有交集。已读head `cc6379f0`，当时仍Draft/服务验收中；**未拉入受测组合、未合测、未合并**。后续先核最新验收、互补/替代与来源绑定，再决定最短组合验证；不盲目叠加。队友#17–19已有负结果，不据微测直接集成。
- 一次metrics只证明累计preempt=1，不能量化重算。447同RID CPU诊断已准备互审，**未部署、未执行、无run ID**：[observer/owner](archive/ai/20261022-framework-kv/current-main-resume-cpu/)、[回收工具](archive/ai/20261022-framework-kv/current-main-resume-cpu-recovery/)。不自动排队；分stream Attention尚缺当前资源与净预算，当前不实现。

## 设备与检查

root为本实例唯一GPU owner。官方owner23938仅Z状态不占卡；server23952、Engine24116、benchmark24372均退出。15:55 UTC封存实查68MiB/0%、无设备进程、9031双栈关闭；没有后继实验。远端run：`/workspace/experiments/minicpm-s2/official/20261023T144620Z-current-main-compute-order-official`，control同名加`-control`。run的server/benchmark日志、control的`runner.log`及manifest保留。

检查：用现有专用密钥和严格host-key的SSH入口 `lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io -p 2224`，远端执行 `ps -o pid,ppid,stat,args -p 23938,23952,24116,24372`，读取run的`result.json`、`postflight-full.json`及control的`runner.log`。**不重跑封存器覆盖原件；以后启动前重查实时占用。**

## Git、同步与智能体

- 框架本地 `collaboration/FlagOS-S2-vllm-plugin-FL` 仍在原分支`codex/kv-save-restore`、HEAD `37661d2d`，工作树clean。新增`codex/biv150-compute-order`已推4fca58ba并建PR21，没有切换或覆盖原分支。FlagGems本地HEAD `6ddb4c4c`，本轮无算子改动。
- 实验表**206条/203run**，批量同步[实验PR #2](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/pull/2)，完成身份以`archive/github/20261023-current-main-official-pr2-update.json`最终回执为准；不直接写main、不合并PR。代码PR21回执：`archive/github/20261024-compute-order-pr.json`。
- 用户明确删除“现有仓库只读、只能发布到新仓库”旧限制；[AGENTS.md](AGENTS.md)已明确维护三个团队私有库，按方法PR及批量同步。一次旧规则自动审批拒绝后，经用户明确撤销、更新规则，同一push重新审批通过，没有绕过拒绝。比赛、秘密和单卡约束保留。
- 子智能体重要结论/待办已落盘：[框架](docs/agent-work/framework_innovation.md)、[硬件](docs/agent-work/hardware_innovation.md)、[回收摘要](docs/agent-work/team_view_final_check.md)、[发布](docs/agent-work/publication_batch.md)。本轮不再研究或上卡。
- 原封包本地保留`experiments/**/*.tgz`，已忽略防误传；GitHub保存逐项核验的展开证据。tmp/本地镜像保留，447可执行资产已另复制archive。最终代码/记录保存commit，未提交状态和忽略封包清单沿最终交接快照。

**用户指示继续后再开始**：核PR20最新验收和P兼容性；P准确率覆盖与可比收益仍待确认；447仅作预算诊断备选。未变的已有验证不重跑，BI-V150结论不外推C500。
