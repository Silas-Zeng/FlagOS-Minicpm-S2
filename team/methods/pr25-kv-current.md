<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# PR25 与缓存修复后的 KV 保存恢复

以7596cc0为共同基点，比较原调度与单victim KV SAVE/FULL，保留官方服务参数。VERIFY1字节门通过，关闭回读后的两轮对照同KV546432、同初始DB：4K为+0.103%/+0.644%但无FULL覆盖，16K为+4.728%/−0.493%。筛选未见明显退化，尚未确认稳定收益；两侧调优增长不同，不换算为耗时。保留候选，按用户要求完成官方四轮及最终组合准确率后再下结论、确定新基线；不把本轮结果归给后续main集成。

相关代码：[pr25-kv-current-pair.json](../../analysis/pr25-kv-current-pair.json)；[result.json](../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/result.json)；[archive-receipt.json](../../experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds-control/archive-receipt.json)；[source-manifest.json](../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/source-manifest.json)；[coverage.json](../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/coverage.json)；[semantic-validation.json](../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/model-path/semantic-validation.json)；[archive-receipt.json](../../experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/archive-receipt.json)；[result.json](../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds/result.json)；[state.json](../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/state.json)；[archive-receipt.json](../../experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/archive-receipt.json)。

相关方法PR：[激活量化缓存 #25](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/25)；[native编译缓存身份 #35](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/35)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261024T142819Z-pr25-cache-main-fullsize-two-rounds](../runs/bi-v150/20261024T142819Z-pr25-cache-main-fullsize-two-rounds.md)（登记#219）：4K两轮5396.58/5730.67、16K两轮3565.12/3992.53 total tok/s；768请求全成功，KV546432。仅本组筛选基线，非官方四轮分数或优化收益。 **是否保留：** 保留两档全部原轮作本组筛选基线；不丢首轮、不以第二轮变快归因优化，不自动定为新官方基线。
- [20261024T145945Z-pr25-cache-kv-verify1-context16k-long](../runs/bi-v150/20261024T145945Z-pr25-cache-kv-verify1-context16k-long.md)（登记#220）：32/0；R16960、每方向729415680字节一致，SAVE504/FULL2688。另同服务4/4语义正确、实际34层native图；VERIFY1不计性能或完整准确率。 **是否保留：** 保留KV字节、真实模型路径和4题语义门；允许进入关闭VERIFY回读的性能对照，完整组合准确率另验。
- [20261024T151255Z-pr25-cache-kv-fullsize-two-rounds](../runs/bi-v150/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds.md)（登记#221）：候选768/0；4K5402.15/5767.57（+0.103%/+0.644%，无FULL不可归因），16K3733.69/3972.85（+4.728%/−0.493%）。未确认稳定收益，待官方四轮。 **是否保留：** 候选保留待确认；两轮未见明显退化，但16K正负并存。按用户要求跑满官方四轮并完成最终组合准确率后再下结论、确定新基线。
