<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA KV读取缓存策略

实际GQA内核4处K/V load改.cg，三个组件形状Event省2.6666%/1.3662%/1.2912%。旧官方首暖4944.66混有Q-hoist和compute-order失活，不能判.cg本体无收益；原main当期首暖5761.99，两轮部分对照保留。后继修正三处关联身份，实际确认Q-fragment install+selected和compute-order selected，4K冷/首暖5073.26/5362.19 tok/s、512成功。首暖相对历史5751.88及当期5761.99观察−6.7750%/−6.9386%，按规则主动停止，第三轮中断、16K/105不跑。KV547648对547536仍不同，非严格因果；本轮没有模型净收益，不合并/定基线，也不回改旧混杂结果。

相关代码：[stack-activation.json](../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds-control/stack-activation.json)；[biv150_q_fragment_service.py](../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds-control/plugin-source/vllm_fl/patches/biv150_q_fragment_service.py)；[biv150_compute_order.py](../../experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds-control/plugin-source/vllm_fl/patches/biv150_compute_order.py)；[server.log](../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds/server.log)；[server.log](../../experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds/server.log)；[kernel.diff](../../experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/source/kernel.diff)；[worker.py](../../experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/source/worker.py)；[early-stop-request.json](../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds-control/early-stop-request.json)；[posthoc-db-comparison.json](../../experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds-control/analysis/posthoc-db-comparison.json)；[raw_runs_20261025_001229.csv](../../experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/benchmark_results/raw_runs_20261025_001229.csv)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T130020159833Z-gqa-kv-cg-hotspot-component](../runs/bi-v150/20261025T130020159833Z-gqa-kv-cg-hotspot-component.md)（登记#266）：N33/B40/S16：8组数值/Graph边界通过，Event1.277376→1.243314ms，省2.6666%；wall省2.7239%。 **是否保留：** 保留16K组件正信号；旧官方对照关闭Q-hoist/compute-order，存在混杂，.cg本体整模收益待修正集成后验证。
- [20261025T130258500889Z-gqa-kv-cg-b32-component](../runs/bi-v150/20261025T130258500889Z-gqa-kv-cg-b32-component.md)（登记#267）：B32/S4：8组数值/Graph边界通过，Event1.029731→1.015663ms，省1.3662%；wall省1.4070%。 **是否保留：** 保留第二形状的局部正信号，不外推官方吞吐收益。
- [20261025T132239Z-main0915-gqa-kv-cg-four-rounds](../runs/bi-v150/20261025T132239Z-main0915-gqa-kv-cg-four-rounds.md)（登记#271）：4K冷/首暖4722.73/4944.66 tok/s，首暖对同轮5751.88为−14.03%；512成功，第三轮主动中断、16K未测。 **是否保留：** 保存全部已测及停止原件；旧候选Q-hoist/compute-order未启用而原main已启用，属优化组合不完整的混杂比较，不能判.cg本体无收益；修正集成后另作对照。
- [20261025T135551248816Z-gqa-kv-cg-b64-4k-component](../runs/bi-v150/20261025T135551248816Z-gqa-kv-cg-b64-4k-component.md)（登记#273）：4K/B64/S2：原8组数值/Graph通过，Event0.528390→0.521568ms省1.2912%，wall省1.4224%。 **是否保留：** 保留第三个局部正信号，不做长短gating；旧官方因Q-hoist/compute-order失活存在混杂，修正集成后再对照。
- [20261025T140749Z-team-main0915-current-official-four-rounds](../runs/bi-v150/20261025T140749Z-team-main0915-current-official-four-rounds.md)（登记#274）：原main4K冷/首暖5404.31/5761.99 tok/s、512成功；因已有完整基线主动停止，仅两轮，16K未测。 **是否保留：** 保留当期部分对照，不覆盖旧完整基线；本轮两项原有优化启用，与旧.cg关闭状态不同，修正后才能判断.cg本体整模收益。
- [20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds](../runs/bi-v150/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds.md)（登记#280）：Q-fragment与compute-order均实际选中；4K冷/首暖5073.26/5362.19 tok/s，512成功，首暖对历史/当期观察−6.7750%/−6.9386%。 **是否保留：** 按首暖负可停策略收尾，第三轮中断、16K/105不跑；KV不同不判严格因果，无模型净收益或新基线。
