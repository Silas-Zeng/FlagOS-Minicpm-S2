<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# RoPE与KV写入融合

保留实际526旋转表达式与Q/K输出，在同核追加KV写入；组件正信号保留。211606模型四语义正确，但跨submod图门误拒且源码目录新增.best_config，原source_unchanged=false/completed=false不改判，修复后须新服务门。

相关代码：[results.json](../../experiments/framework/20261024T203032Z-rope-kv-component/results.json)；[state.json](../../experiments/framework/20261024T203032Z-rope-kv-component/state.json)；[archive-receipt.json](../../experiments/framework/20261024T203032Z-rope-kv-component/archive-receipt.json)；[results.json](../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/results.json)；[state.json](../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/state.json)；[archive-receipt.json](../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/archive-receipt.json)；[state.json](../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/state.json)；[source-diff.json](../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/failed-posthoc/source-diff.json)；[0-computation_graph.py](../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/failed-posthoc/0-computation_graph.py)；[archive-receipt.json](../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261024T203032Z-rope-kv-component](../runs/bi-v150/20261024T203032Z-rope-kv-component.md)（登记#233）：configs=None导致记录器TypeError，无有效case；原失败保留，不作数值或性能负结果。 **是否保留：** 保留失败；仅修记录器后另开v2，不追溯改判。
- [20261024T203809Z-rope-kv-component-config-v2](../runs/bi-v150/20261024T203809Z-rope-kv-component-config-v2.md)（登记#234）：42层字节/guard/变输入Graph通过；M2048/32/64 Graph总wall约5.070→4.791、0.899→0.864、0.982→0.896ms，仅局部组件。 **是否保留：** 保留正信号供模型接线，模型准确率/端到端尚待。
- [20261024T211606Z-rope-kv-model-verify](../runs/bi-v150/20261024T211606Z-rope-kv-model-verify.md)（登记#238）：4/4语义正确，但图门跨submod误拒且新增.best_config；source_unchanged=false、completed=false，原失败保留。 **是否保留：** 保留失败与posthoc原件；cache位置和parser修复后另验，不能追溯恢复资格。
