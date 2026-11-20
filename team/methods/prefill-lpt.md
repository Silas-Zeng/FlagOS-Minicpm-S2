<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill序列内CTA调序

保留stride/Q-hoist及每query的K顺序，只反转序列内CTA枚举。完整Graph Q2048/KV2048省12.2180%，Q2048/KV4096省5.7144%，长Q2047/KV16384慢3.57%。纯causal原FP64门两臂均false、输出逐位相同，保留原失败诊断；middle原FP64硬门通过。独立原官方4K暖均5722.4833观察+1.1617%，16K首暖4111.36观察−0.19663%后停，六轮1280 SUCCESS。私有LPT Q-hoist实际selected通过；KV548432对548336，保留混合结果候选，不能称稳定整体收益或整体负。无105/合并，main6971不变。

相关代码：[results.json](../../experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component/results.json)；[source](../../experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component/source)；[lpt-posthoc-activation.json](../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds-control/lpt-posthoc-activation.json)；[raw_runs_20261026_151843.csv](../../experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds/benchmark_results/raw_runs_20261026_151843.csv)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T055057881154Z-prefill-lpt-causal-component](../runs/bi-v150/20261026T055057881154Z-prefill-lpt-causal-component.md)（登记#305）：Q2048/KV2048原臂与候选输出有限、guard正常，但都被旧long-only FP64 max_abs≤5e-4拒绝：两臂同max_abs0.00352174、relative_l20.00095805。保存输出CPU后核整份逐位一致/max_diff0；不据此认定候选新增数值错，未计时。 **是否保留：** 原臂/候选逐位一致；旧FP64拒绝不改判，后继逐位组件单列。
- [20261026T055124182279Z-prefill-lpt-long-component](../runs/bi-v150/20261026T055124182279Z-prefill-lpt-long-component.md)（登记#306）：当前stride/Q-hoist上仅反转序列内query块，Q2047/KV16384初始及换值跨臂逐位、独立FP64、writer/Graph/输入RNG均过。完整Attention Event 8.168149→8.460097ms，慢3.57%，wall同向。长上下文无净益，不推进该范围；短c **是否保留：** 长上下文不进模型；短causal单独完成有界验证。
- [20261026T061252978123Z-prefill-lpt-bitwise-causal-component](../runs/bi-v150/20261026T061252978123Z-prefill-lpt-bitwise-causal-component.md)（登记#309）：Q2048/KV2048仅CTA reversal，初始/换值跨臂逐位及自臂换值Graph通过。直接JIT ABBA Event0.660719→0.582717ms省11.8056%，wall0.783708→0.805652ms慢2.8000%，不以此认定Graph或整模收益。旧long-onl **是否保留：** 保留逐位依据；直接JIT不代替完整Graph或整模，FP64诊断false不改判。
- [20261026T062007042651Z-prefill-lpt-graph-causal-component](../runs/bi-v150/20261026T062007042651Z-prefill-lpt-graph-causal-component.md)（登记#310）：Q2048/KV2048完整Attention Graph replay ABBA Event0.663944→0.582823ms省12.2180%，wall0.667164→0.585344ms省12.2639%；初始/换值跨臂及自臂Graph逐位。旧long-only FP64 max_abs **是否保留：** 保留早期chunk候选；无官方/105新资格。
- [20261026T063949247282Z-prefill-lpt-graph-middle-component](../runs/bi-v150/20261026T063949247282Z-prefill-lpt-graph-middle-component.md)（登记#311）：Q2048/KV4096、context2048对应4K第二chunk，完整Attention Graph Event1.755975→1.655632ms省5.7144%，wall1.759074→1.658530ms省5.7157%。初始/换值跨臂逐位、自臂Graph及原FP64硬门通过；DB/ **是否保留：** 保留已测第二chunk范围；不推广long或任意形状。
- [20261026T071618Z-main6971-lpt-early-four-rounds](../runs/bi-v150/20261026T071618Z-main6971-lpt-early-four-rounds.md)（登记#316）：LPT早期chunk原官方4K四轮4863.05/5694.95/5694.17/5778.33 tok/s，弃首轮5722.4833，对main6971的5656.77观察+1.1617%；16K冷3757.10、首暖4111.36，对应4119.46观察−0.19663%后停止。六轮1280 S **是否保留：** 保留混合结果候选；停止后续测试，无105/合并或新基线，不称整体负或稳定收益。
