<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 有限窗口增长准入

真实服务消除本轮抢占，但共同DB对照仍有KV容量失配；默认关闭保留研究证据，不宣称确定收益。

两轮原 bc51 smoke 仅作启动显存诊断：共同 observer 下，finite 的非 Torch 内存多 4 MiB，差异在 before_profile 已存在；KV 为 baseline 521936、finite 521840，与旧性能对照方向相反。四端 DB 均为 532 表、19839 行且三项 SHA 一致；文本及 32 个 token ID 相同，但未覆盖 mixed Q/GQA 命中，不算准确率或性能收益。停止追查启动差异，旧性能对照仍因 KV 容量失配而不能归因。

相关代码：[finite-growth-common-db-service-pair.json](../../analysis/finite-growth-common-db-service-pair.json)；[finite-growth-warm-service-pair.json](../../analysis/finite-growth-warm-service-pair.json)；[finite-growth-service-pair.json](../../analysis/finite-growth-service-pair.json)；[current-kv-memory-smokes.json](../../analysis/current-kv-memory-smokes.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T193302Z-finite-growth-baseline-context16k-long](../runs/bi-v150/20261022T193302Z-finite-growth-baseline-context16k-long.md)（登记#164）：32成功0失败；后继cold与warm候选KV521936且DB起点/终点不同，旧pair收益均null **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T194020Z-finite-growth-candidate-context16k-long](../runs/bi-v150/20261022T194020Z-finite-growth-candidate-context16k-long.md)（登记#165）：32成功0失败 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T194634Z-finite-growth-candidate-context16k-long](../runs/bi-v150/20261022T194634Z-finite-growth-candidate-context16k-long.md)（登记#166）：TPS+0.9894%但KV/DB双失配，可比收益null **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261022T195213Z-finite-growth-baseline-context16k-long](../runs/bi-v150/20261022T195213Z-finite-growth-baseline-context16k-long.md)（登记#167）：TPS+1.000545%不能归因，收益null **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T201344Z-current-kv-memory-baseline-smoke](../runs/bi-v150/20261022T201344Z-current-kv-memory-baseline-smoke.md)（登记#168）：原 bc51 smoke 启动显存诊断，非性能轮 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T201518Z-current-kv-memory-finite-smoke](../runs/bi-v150/20261022T201518Z-current-kv-memory-finite-smoke.md)（登记#169）：原 bc51 smoke 启动显存诊断，非性能轮；文本及32个token ID相同，未覆盖mixed Q/GQA命中，不算accuracy/收益 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
