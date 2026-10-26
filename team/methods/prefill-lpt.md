<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill序列内CTA调序

保留stride/Q-hoist及每query的K顺序，只反转序列内CTA枚举。完整Graph Q2048/KV2048省12.2180%，Q2048/KV4096省5.7144%，长Q2047/KV16384慢3.57%。纯causal原FP64门两臂均false、输出逐位相同，保留原失败诊断；middle原FP64硬门通过。只保留已测早期chunk候选。07:16启动独立原官方，双Manager安装成功尚未取得实际选择资格，无整模结论；main6971基线不变。

相关代码：[results.json](../../experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component/results.json)；[source](../../experiments/framework/20261026T062007042651Z-prefill-lpt-graph-causal-component/source)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T055057881154Z-prefill-lpt-causal-component](../runs/bi-v150/20261026T055057881154Z-prefill-lpt-causal-component.md)（登记#305）：Q2048/KV2048原臂与候选输出有限、guard正常，但都被旧long-only FP64 max_abs≤5e-4拒绝：两臂同max_abs0.00352174、relative_l20.00095805。保存输出CPU后核整份逐位一致/max_diff0；不据此认定候选新增数值错，未计时。 **是否保留：** 原臂/候选逐位一致；旧FP64拒绝不改判，后继逐位组件单列。
- [20261026T055124182279Z-prefill-lpt-long-component](../runs/bi-v150/20261026T055124182279Z-prefill-lpt-long-component.md)（登记#306）：当前stride/Q-hoist上仅反转序列内query块，Q2047/KV16384初始及换值跨臂逐位、独立FP64、writer/Graph/输入RNG均过。完整Attention Event 8.168149→8.460097ms，慢3.57%，wall同向。长上下文无净益，不推进该范围；短c **是否保留：** 长上下文不进模型；短causal单独完成有界验证。
- [20261026T061252978123Z-prefill-lpt-bitwise-causal-component](../runs/bi-v150/20261026T061252978123Z-prefill-lpt-bitwise-causal-component.md)（登记#309）：Q2048/KV2048仅CTA reversal，初始/换值跨臂逐位及自臂换值Graph通过。直接JIT ABBA Event0.660719→0.582717ms省11.8056%，wall0.783708→0.805652ms慢2.8000%，不以此认定Graph或整模收益。旧long-onl **是否保留：** 保留逐位依据；直接JIT不代替完整Graph或整模，FP64诊断false不改判。
- [20261026T062007042651Z-prefill-lpt-graph-causal-component](../runs/bi-v150/20261026T062007042651Z-prefill-lpt-graph-causal-component.md)（登记#310）：Q2048/KV2048完整Attention Graph replay ABBA Event0.663944→0.582823ms省12.2180%，wall0.667164→0.585344ms省12.2639%；初始/换值跨臂及自臂Graph逐位。旧long-only FP64 max_abs **是否保留：** 保留早期chunk候选；无官方/105新资格。
- [20261026T063949247282Z-prefill-lpt-graph-middle-component](../runs/bi-v150/20261026T063949247282Z-prefill-lpt-graph-middle-component.md)（登记#311）：Q2048/KV4096、context2048对应4K第二chunk，完整Attention Graph Event1.755975→1.655632ms省5.7144%，wall1.759074→1.658530ms省5.7157%。初始/换值跨臂逐位、自臂Graph及原FP64硬门通过；DB/ **是否保留：** 保留已测第二chunk范围；不推广long或任意形状。
