<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA KV读取缓存策略

仅将实际GQA内核4处K/V load标为.cg，原reducer与数学不变。N33/B40/S16与B32/S4各8组数值/换值Graph边界通过（含原非有限行为保持），实际ASM各64处cg，组件Event分别省2.6666%/1.3662%。通用生产候选原官方4K仅完成冷/首暖两轮，4722.73/4944.66 tok/s；对参考同轮4713.78/5751.88，首暖观察−14.03%，主动停止。512请求成功、第三轮中断、16K未测，不是完整官方成绩。KV547648对547536；独立DB后分析共同key配置无变仍有新增/缺少key与形状差异，不判内核因果，不定基线或PR。补充4K/B64/S2原8组数值/Graph通过，Event省1.2912%、wall省1.4224%。三个局部形状均正，不支持短输入局部负的猜想，不做长短gating。当前不能合并或定新基线，待当期原main control解释组件与官方的差异，不将.cg永久淘汰。

相关代码：[kernel.diff](../../experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/source/kernel.diff)；[worker.py](../../experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/source/worker.py)；[early-stop-request.json](../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds-control/early-stop-request.json)；[posthoc-db-comparison.json](../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds-control/analysis/posthoc-db-comparison.json)；[raw_runs_20261025_001229.csv](../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/benchmark_results/raw_runs_20261025_001229.csv)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T130020159833Z-gqa-kv-cg-hotspot-component](../runs/bi-v150/20261025T130020159833Z-gqa-kv-cg-hotspot-component.md)（登记#266）：N33/B40/S16：8组数值/Graph边界通过，Event1.277376→1.243314ms，省2.6666%；wall省2.7239%。 **是否保留：** 保留16K组件正信号；官方后继首暖负、待同期control，不将局部结果外推端到端。
- [20261025T130258500889Z-gqa-kv-cg-b32-component](../runs/bi-v150/20261025T130258500889Z-gqa-kv-cg-b32-component.md)（登记#267）：B32/S4：8组数值/Graph边界通过，Event1.029731→1.015663ms，省1.3662%；wall省1.4070%。 **是否保留：** 保留第二形状的局部正信号，不外推官方吞吐收益。
- [20261025T132239Z-main0915-gqa-kv-cg-four-rounds](../runs/bi-v150/20261025T132239Z-main0915-gqa-kv-cg-four-rounds.md)（登记#271）：4K冷/首暖4722.73/4944.66 tok/s，首暖对同轮5751.88为−14.03%；512成功，第三轮主动中断、16K未测。 **是否保留：** 保存全部已测及停止原件；KV/DB条件差异，不判内核因果。等待当期原main control解释局部/官方差异，当前不能合并或定新基线。
- [20261025T135551248816Z-gqa-kv-cg-b64-4k-component](../runs/bi-v150/20261025T135551248816Z-gqa-kv-cg-b64-4k-component.md)（登记#273）：4K/B64/S2：原8组数值/Graph通过，Event0.528390→0.521568ms省1.2912%，wall省1.4224%。 **是否保留：** 保留第三个局部正信号；不支持短输入局部负猜想，不做长短gating，待当期main control解释官方负结果。
