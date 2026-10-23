<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# KV 二维 FULL 恢复

保留原页序、私有页资格和完成事件，合并H2D提交；独立单层字节门与真实42层事务分开记录，调用数下降不当作性能收益。

相关代码：[README.md](../../archive/ai/20261022-framework-kv/q-gqa-kv-restore-pitch/README.md)；[kv-pitched-restore-method.json](../../analysis/kv-pitched-restore-method.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T222047Z-kv-pitched-restore-gate](../runs/bi-v150/20261022T222047Z-kv-pitched-restore-gate.md)（登记#178）：RNG **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T222222Z-q-gqa-kv-restore-pitched-verify1-context16k-long](../runs/bi-v150/20261022T222222Z-q-gqa-kv-restore-pitched-verify1-context16k-long.md)（登记#179）：32成功0失败，R16704/1044页 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T223056Z-q-gqa-kv-restore-pitched-verify0-baseline-context16k-long](../runs/bi-v150/20261022T223056Z-q-gqa-kv-restore-pitched-verify0-baseline-context16k-long.md)（登记#180）：32成功0失败，完整来源/原参数/DB544四端/真实FULL事务及consumer/无回读/清理均通过 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long](../runs/bi-v150/20261022T223540Z-q-gqa-kv-restore-pitched-verify0-candidate-context16k-long.md)（登记#181）：32成功0失败，完整来源/原参数/DB544四端/真实FULL事务及consumer/无回读/清理均通过 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
