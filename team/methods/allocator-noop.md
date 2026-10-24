<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# KV 分配器无状态快返

普通decode不新增页或完整块哈希时返回原空分配结果；保留新页、哈希、恢复与非RUNNING原路径，CPU片段和服务配对分别记录。

相关代码：[README.md](../../archive/ai/20261022-framework-kv/next-kv-noop-allocate/README.md)；[allocator-noop-service-pair.json](../../analysis/allocator-noop-service-pair.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T225044Z-allocator-noop-baseline-decode4k](../runs/bi-v150/20261022T225044Z-allocator-noop-baseline-decode4k.md)（登记#182）：64成功0失败，原参数/DB544四端/完整422→423源码/实际QGQA/新快返及清理等30项通过，唯一same_KV失败：521936→521840，gain=null **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T230741Z-allocator-noop-candidate-decode4k](../runs/bi-v150/20261022T230741Z-allocator-noop-candidate-decode4k.md)（登记#183）：64成功0失败，原参数/DB544四端/完整422→423源码/实际QGQA/新快返及清理等30项通过，唯一same_KV失败：521936→521840，gain=null **是否保留：** 待确认；通过某项检查不自动等于优化保留。
