<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# BQ16 chunk 形状对齐

复用现有 C2/C3 与原算子，比较七段恢复链的 chunk 形状；局部正信号保留，未实现调度器或接入服务。

相关代码：[validate_bq16_chunk_chain.py](../../archive/ai/20261022-framework-kv/bq16-chunk-alignment/validate_bq16_chunk_chain.py)；[result-review.json](../../archive/ai/20261022-framework-kv/bq16-chunk-alignment/result-review.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T181739Z-bq16-chunk-chain-gate](../runs/bi-v150/20261022T181739Z-bq16-chunk-chain-gate.md)（登记#158）：wall60.169030→60.023055ms（缩短0.242608%），event60.029037→59.888794ms（缩短0.233626%），4窗cgroup throttle均0；decode起始KV16384为构造值，不外推端到端、准确率、C500或稳定统计收益 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
