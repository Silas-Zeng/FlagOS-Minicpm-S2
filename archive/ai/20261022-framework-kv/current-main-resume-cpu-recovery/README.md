# 447 CPU诊断收尾

**2026-10-23收口：用户要求完成当前工作后切换API，447诊断未执行，不再启动；没有实际run ID。以下仅为已准备资产，不能作为新任务授权。** `RUN=None`不伪造时间；若以后重新明确授权，先核实际部署资产和实际run ID再锁定。

仅准备，未执行封存、导入或设备命令。`preparation.json`、两份 `.diff` 保存原候选收尾器的精确逆回及syntax结果。root取得实际run ID后可仅锁两脚本的 `RUN`；当前只接受合法UTC及 `-current-main-resume-cpu-context16k-long` 后缀。

`seal_resume_cpu.py <runID>` 保留原exit0/1终态，核固定446 Git map加observer两delta后的完整447/tree cd500、已锁owner800a的live/control source_maps，原Attention/DB/端口/进程清理不变。新增 `owner-process-group.json` 只读 `/proc/*/stat`，记录runner预期PGID/SID；存在活跃成员或扫描不完整就拒封包，不发信号。封存失败输出保留，不能盲目重跑覆盖。

`resume-cpu-events.json` 独立保留FINAL、抢占、APC及实际execute原字段，缺覆盖或FINAL不阻保存原件；不据CPU提交证明GPU完成、可省重算时间或性能。失败时负载结果可为空，原server/runner日志保留。

本地导入：`python import_resume_cpu.py <runID> <实际tgz字节数> <实际SHA256> <实际seal条目数>`。447/框架目录与long结果路径已适配；复用唯一已审symlink材料化、全seal集合和已有异字节拒覆盖规则，原tgz不改。原件可含负结果，不写注册表或性能结论。

冻结交付仅两入口：sealer `9f3e42eb03e551bef62ef6634b9052666fd68cab7f516181ff6656e2bef9d880`；importer `500e9e52f9e2a241eeb5b513ed37860a60b986cad05744ec5a8b6dd2015fc6cf`。初版importer的展示性benchmark JSON解析遇半写文件会中断receipt，最终仅增加 `parse_error` 保留失败数据，不放松任何seal门；`.initial`是未执行草稿，不能部署。已完成syntax与精确逆回，无原件/旧套件/设备执行。

硬件负责人已只读核sealer新增源码闭包、PGID/SID stat字段及不杀进程的失败闭合，无当前阻断；无FINAL或缺事件仍按未覆盖封存，`causal_chain_reviewed=False`。不由CPU issued/return字段推定GPU已完成前缀或实际重算秒数。

硬件负责人最终实读并核importer500e9e52：新增parse_error仅影响展示，不改全包/全seal/路径/唯一link/拒覆盖门，也不将半写负结果当成功；与sealer9f3合并静态封口无阻断。两个入口均未执行，447本轮不运行；本子任务停止。
