# 当前工作与 API 接续

更新：2026-10-23 07:09 UTC。root 是唯一 SSH/GPU owner；接续已有成果，不重新开始。团队只看[实验总表](team/experiments.md)和[方法汇总](team/README.md)，细节沿原件链接。历史过程已移入[AI归档](archive/ai/CURRENT_WORK-through-20261023T060425Z.md)。

## 当前任务

- 唯一在途GPU：`framework/20261023T070816Z-compute-order-answer-baseline`，原bc51派生owner9b645 PID7283；source仍原422 `code/q-gqa-kv-swap-20261022T213134Z`。辅助答案门保原SERVER、锁、smoke、环境/监控/清理，只替换一次load为固定32×16K输入/128输出的答案客户端。不要另启服务、benchmark、profiler。
- 固定请求由CPU实际tokenizer生成一次，两臂共用 `/workspace/experiments/minicpm-s2/diagnostic-inputs/compute-order-answer-20261023T065931Z/requests.jsonl`，SHA b35be1461b5af29ffe90f6300e0084ca5de015549ed00fcbdd960e07eaf4e497。无request seed，temp1/top_p.95，保原随机采样。先baseline；其答案/长度若不过，停止candidate，记门无判别力。
- 辅助门作者framework_innovation、窄审team_view_final_check，冻结运行文件及root emitter见 `archive/ai/20261022-framework-kv/compute-order-answer-gate/`，工作稿在同名tmp。只证明同窗真实选路集成＋答案可用，答案可能早于FIRST_SELECTED，不声称每条答案来自P、全q1逆映射、逐层数值或官方准确率。
- accepted-fill 064838/065325已全部收尾并导入，设备已释放。31门仅KV容量521840→521936失配，DB四端558/20651三hash相同；表观吞吐−0.235046%，gain=null，当前不集成，不追加大测或代码PR。完整负结果见[分析](analysis/accepted-fill-service-pair.json)，资产在 `archive/ai/20261022-framework-kv/accepted-fill/` 及 `accepted-fill-owner/`。

## 最新结论与 GitHub

- **计算序短测**：054306→060425两侧32/0，104.312939462→99.536272152s、5065.373507102→5308.456792453 total tok/s。表观+4.7989%，但KV521936→521840，31门仅same_KV失败、gain=null。Engine2350实际N17/M2048/Dprefix1/outside14，保留候选不默认集成；[分析](analysis/compute-order-service-pair.json)。
- **061500完整准确率已回收**：101/105（96.19%）、105请求成功、2个max_tokens（23、83），通过原95%门。没有COMPUTE_ORDER_FIRST_SELECTED，不能证明新排列路径正确，也不与原422的103/105作精度升降统计；[简短摘要](analysis/compute-order-accuracy.json)。原35d/6e045/SERVER未变，723原件已核导入，设备/端口清理；DB554/20517→558/20651。
- **实验PR #2已更新**：[PR链接](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/pull/2)，head545b157d、tree55944568、本地来源65a0118，已包含188条登记/185run；[发布回执](archive/github/20261023-framework-batch-pr2-update.json)。本地现191条/188run，正在将061500准确率、accepted-fill负结果和PR15链接一起批量补传。PR #3是队友算子记录，不改；main未写。
- **代码PR #15已建Draft**：[computed H2D](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/15)，只改一个runner文件，head638c4ac0，基于当前main9a43eb1。引用既有+0.619291%可比单pair及214819方法门；只静态迁移，没有为上传重测。没有本方法新完整准确率/C500验证，按正文边界审阅后再合并，不触碰队友#14。
- 当前原422组合的完整准确率是103/105；官方231746为1536成功，4K总4957.95、16K总3669.74 tok/s，仅绝对值。002156 GPU轨迹显示下一graph已提前提交，不支持继续把当前热点当CPU未及时提交。其余正负方法见总表，不重复旧测试。

## 接续约定

1. 框架、调度、KV与硬件适配是主线；新增算子由队友负责。每项先判断可省的真实开销，复用轨迹，必要时做最短有判别力的验证。
2. 每轮保存版本、命令、环境及原始结果；registry一行写改动、测法、结果、限制。对照完成批量更新实验PR，完整准确率/官方大测当天同步。代码按方法PR，源码未变不为上传重测。
3. 三个私有协作库按[AGENTS.md](AGENTS.md)维护；官方上游/参考库只读。现有PR用普通追加提交，不force、不覆盖队友、不直接写main。
4. `scripts/build_team_view.py`只在登记/方法链接变化后批量运行。新原件传输exit0、封包及逐文件核对后再分析；已核过且不变的门复用结论。
5. SSH入口仍为 `lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io -p 2224`，使用现有专用密钥和严格host-key检查；不要记录凭据。

当前固定比赛约束：MiniCPM5-2B、原官方benchmark与SERVER参数、不改量化/推测超参数、不升级框架。SQL只缩小SQLAlchemy反射，官网规则复核和原件在 `archive/rules/20261023-sql-compliance/`；不能外推为任意修改调优配置的许可。
