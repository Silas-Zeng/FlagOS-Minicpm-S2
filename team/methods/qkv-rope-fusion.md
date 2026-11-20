<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# QKV GEMM与RoPE融合

layer0真实权重＋合成激活，融合QKV GEMM输出和RoPE，不含KV writer。M2030/2048的14项逐位/FP64/Graph/side stream通过，Graph慢12.4198%/12.8168%，停止。原组件基于installed mm，未绑定生产opaque/F.linear身份，不能当生产linear的直接对照。单层未复现42层交织；原RoPE heuristic重新编译，不宣称服务原机器码，亦无官方资格。

相关代码：[result.json](../../experiments/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component/result.json)；[source](../../experiments/framework/20261026T064944259294Z-biv150-qkv-rope-fusion-component/source)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T064944259294Z-biv150-qkv-rope-fusion-component](../runs/bi-v150/20261026T064944259294Z-biv150-qkv-rope-fusion-component.md)（登记#315）：layer0真实QKV GEMM＋原native RoPE combo对照新融合输出，M2030/2048共14项Q/K/V逐位、独立FP64、换值Graph及side stream通过，RNG不变。Graph Event均值分别0.384947→0.432756ms、0.385697→0.4351 **是否保留：** 停止，不进官方；无生产adapter或新基线。
