<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# RoPE与KV写入融合

保留实际526旋转表达式与Q/K输出，在同一核追加KV写入；独立组件正信号不等于模型收益，需显式副作用/依赖及模型验证。

相关代码：[results.json](../../experiments/framework/20261024T203032Z-rope-kv-component/results.json)；[state.json](../../experiments/framework/20261024T203032Z-rope-kv-component/state.json)；[archive-receipt.json](../../experiments/framework/20261024T203032Z-rope-kv-component/archive-receipt.json)；[results.json](../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/results.json)；[state.json](../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/state.json)；[archive-receipt.json](../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261024T203032Z-rope-kv-component](../runs/bi-v150/20261024T203032Z-rope-kv-component.md)（登记#233）：configs=None导致记录器TypeError，无有效case；原失败保留，不作数值或性能负结果。 **是否保留：** 保留失败；仅修记录器后另开v2，不追溯改判。
- [20261024T203809Z-rope-kv-component-config-v2](../runs/bi-v150/20261024T203809Z-rope-kv-component-config-v2.md)（登记#234）：42层字节/guard/变输入Graph通过；M2048/32/64 Graph总wall约5.070→4.791、0.899→0.864、0.982→0.896ms，仅局部组件。 **是否保留：** 保留正信号供模型接线，模型准确率/端到端尚待。
