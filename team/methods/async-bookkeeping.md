<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 异步输出 CPU 批量记账

将有效单 token 异步输出的逐行 CPU 数组更新合并，保留请求历史、事件与回退；服务对照的 KV 失配单列。

相关代码：[biv150_async_bookkeeping.py](../../archive/ai/20261022-framework-kv/async-bookkeeping/biv150_async_bookkeeping.py)；[compare_service_pair.py](../../archive/ai/20261022-framework-kv/async-bookkeeping/compare_service_pair.py)；[async-bookkeeping-service-pair.json](../../analysis/async-bookkeeping-service-pair.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T180643Z-async-bookkeeping-service-candidate-decode4k](../runs/bi-v150/20261022T180643Z-async-bookkeeping-service-candidate-decode4k.md)（登记#156）：吞吐6936.431443对6932.365590tok/s，表观+0.058650%、wall缩短0.058616%、TTFT−0.115824%、TPOT+0.012425%略慢；候选KV521936与基线521840不同，不能作因果性能结论；保留机制候选和失配结果，非稳定收益，无模型准确率结论 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261022T181134Z-async-bookkeeping-service-baseline-decode4k](../runs/bi-v150/20261022T181134Z-async-bookkeeping-service-baseline-decode4k.md)（登记#157）：吞吐+0.058650%不认作收益；基线KV521840与候选521936不同，不能形成严格性能配对；非稳定或官方性能结论 **是否保留：** 保留作对照基线；KV失配，不据此判断候选收益。
