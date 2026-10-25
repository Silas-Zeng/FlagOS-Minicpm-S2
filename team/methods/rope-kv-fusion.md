<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# RoPE与KV写入融合

保持526的RoPE旋转数学与Q/K输出，在同一核追加完整KV写入。生产v2外置autotune元数据，四语义及实际42融合/0旧KV/34native图通过；性能筛选6完整轮未见净正信号，按用户要求早停并封存，不更新基线或追加105。组件正信号、首轮记录/模型失败和全部原始测量分别保留。

相关代码：[results.json](../../experiments/framework/20261024T203032Z-rope-kv-component/results.json)；[state.json](../../experiments/framework/20261024T203032Z-rope-kv-component/state.json)；[archive-receipt.json](../../experiments/framework/20261024T203032Z-rope-kv-component/archive-receipt.json)；[results.json](../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/results.json)；[state.json](../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/state.json)；[archive-receipt.json](../../experiments/framework/20261024T203809Z-rope-kv-component-config-v2/archive-receipt.json)；[state.json](../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/state.json)；[source-diff.json](../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/failed-posthoc/source-diff.json)；[0-computation_graph.py](../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/failed-posthoc/0-computation_graph.py)；[archive-receipt.json](../../experiments/framework/20261024T211606Z-rope-kv-model-verify-control/archive-receipt.json)；[state.json](../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2-control/state.json)；[archive-receipt.json](../../experiments/framework/20261024T223155Z-rope-kv-model-verify-v2-control/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261024T203032Z-rope-kv-component](../runs/bi-v150/20261024T203032Z-rope-kv-component.md)（登记#233）：configs=None导致记录器TypeError，无有效case；原失败保留，不作数值或性能负结果。 **是否保留：** 保留失败；仅修记录器后另开v2，不追溯改判。
- [20261024T203809Z-rope-kv-component-config-v2](../runs/bi-v150/20261024T203809Z-rope-kv-component-config-v2.md)（登记#234）：42层字节/guard/变输入Graph通过；M2048/32/64 Graph总wall约5.070→4.791、0.899→0.864、0.982→0.896ms，仅局部组件。 **是否保留：** 保留正信号供模型接线，模型准确率/端到端尚待。
- [20261024T211606Z-rope-kv-model-verify](../runs/bi-v150/20261024T211606Z-rope-kv-model-verify.md)（登记#238）：4/4语义正确，但图门跨submod误拒且新增.best_config；source_unchanged=false、completed=false，原失败保留。 **是否保留：** 保留失败与posthoc原件；cache位置和parser修复后另验，不能追溯恢复资格。
- [20261024T223155Z-rope-kv-model-verify-v2](../runs/bi-v150/20261024T223155Z-rope-kv-model-verify-v2.md)（登记#240）：RoPE生产v2/tree4e2f52ce四题语义正确（含4908-token prefill），实际42层融合、0旧KV writer、同fusion Q/K/dep与34层native图/FP/AOT通过。22:33:41 UTC源/native未变、DB恢复和清理成功；修复为外置autotun **是否保留：** 保留本轮原件与边界；收尾不重复测试，后继仅按实际资格继续。
- [20261025T005629Z-main0bf9-rope-rope-official-four-rounds](../runs/bi-v150/20261025T005629Z-main0bf9-rope-rope-official-four-rounds.md)（登记#243）：RoPE528原官方参数完成4K四轮5183.64/5678.16/5777.01/5777.66，暖均5744.28 tok/s，对526暖均约−0.25%；16K已完成3439.95/4008.32，首暖对对应4045.32约−0.91%。1280个完整请求成功，后续不完整轮不计入。01:37: **是否保留：** 原始证据和失败保留；是否进入模型/合并以本轮结论为准，不自动续测。
