<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill当前chunk直读K/V

保留writer与原浮点顺序，历史KV走paged、当前chunk读post-RoPE BF16 K/V。长场景逐位/FP64/Graph与实际来源证明通过，但Event慢30.1099%，停止；causal未测，不叠LPT或进入模型。

相关代码：[results.json](../../experiments/framework/20261026T062915011626Z-prefill-fresh-kv-long-component/results.json)；[source](../../experiments/framework/20261026T062915011626Z-prefill-fresh-kv-long-component/source)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T062915011626Z-prefill-fresh-kv-long-component](../runs/bi-v150/20261026T062915011626Z-prefill-fresh-kv-long-component.md)（登记#314）：历史KV读paged cache、当前chunk直读post-RoPE BF16 K/V，保留writer、绝对T64/K顺序与softmax。Q2047/KV16384初始/换值跨臂逐位、FP64/Graph通过；修改raw来源而cache不变时仅fresh臂变化，证明新来源实际使用。Event8 **是否保留：** 停止，不叠LPT或接模型；causal未测。
