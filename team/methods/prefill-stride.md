<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill stride常量特化

仅11项stride改constexpr并保留int64寻址，原normalized/Q-hoist浮点表达式、tile和页序不变。组件SGPR spill30→6/mul103→30，Event省0.5151%、wall慢0.5676%，数值/FP64/Graph及alternate17项通过。旧main0915的603/tree1127346e原官方4K/16K各四轮与实际激活全部通过，1536 SUCCESS；弃首轮5726.63/4052.78 tok/s、TTFT3637.47/124103.35ms，相对旧5758.72/4045.20观察−0.56%/+0.19%。KV547648对547536，非严格因果，只保留长输入小信号；不确认净收益、不合并、不授105资格或新比赛基线，不能混入新main34942/PR51。单序列组件页表行stride仅身份覆盖。

相关代码：[kernel.diff](../../experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/source/kernel.diff)；[alternate_stride.py](../../experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/source/alternate_stride.py)；[results.json](../../experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/results.json)；[raw_runs_20261026_011033.csv](../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds/benchmark_results/raw_runs_20261026_011033.csv)；[prefill-activation.json](../../experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds-control/prefill-activation.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T161135828367Z-prefill-stride-constexpr-component](../runs/bi-v150/20261025T161135828367Z-prefill-stride-constexpr-component.md)（登记#281）：旧数值/FP64/Graph与alternate17项通过，跨臂初始/换值逐位；Event8.371886→8.328763ms省0.5151%，wall慢0.5676%。 **是否保留：** 保留小GPU候选，生产官方入口准备中；模型收益未确认，不授105资格。
- [20261025T170831Z-main0915-prefill-stride-four-rounds](../runs/bi-v150/20261025T170831Z-main0915-prefill-stride-four-rounds.md)（登记#284）：原官方两档各4轮、1536成功，实际激活闭合；弃首轮5726.63/4052.78 tok/s，TTFT3637.47/124103.35ms。 **是否保留：** 相对旧完整参考观察−0.56%/+0.19%，KV不同不判因果；保留小信号，不合并、不升基线、不继承105资格。
