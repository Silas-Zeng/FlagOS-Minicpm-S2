<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# PR24 组合基线与 KV 抢占诊断

本实例 SO 的9项检查通过，短服务32请求全成功。CPU观察确认抢占后的重复提交；修正探针后捕获完整GPU窗口，目标Attention恰168次（4×42）、约1.018秒。P在本轮自然decode前缀下无需重排；KV容量变化、M457冷调优及原owner失败/DB恢复证据均保留。这里只得到局部计算预算，尚无端到端收益；保留KV SAVE/FULL，下一步做一次新组合VERIFY1，暂不重复profile。

相关代码：[pr24-kv-diagnostic.json](../../analysis/pr24-kv-diagnostic.json)；[pr24-resume-native-v2-114500.json](../../analysis/pr24-resume-native-v2-114500.json)；[pr24-resume-native-failure.json](../../analysis/pr24-resume-native-failure.json)；[pr24-resume-db-comparison.json](../../analysis/pr24-resume-db-comparison.json)；[summary.json](../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/summary.json)；[native-build-manifest.json](../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/native-build-manifest.json)；[operator-check.json](../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/operator-check.json)。

相关方法PR：[INT8 gate/up 组合 #24](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/24)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261024T105037Z-pr24-main-context16k](../runs/bi-v150/20261024T105037Z-pr24-main-context16k.md)（登记#210）：结束exit0、源未变、GPU68MiB/0%、DB已恢复；32成功0失败，total tok/s=5121.780601，仅单臂不报性能收益 **是否保留：** 保留作本实例后续基线；组合已由PR24合并，短验不计性能收益或完整准确率。
- [20261024T110545Z-current-main-pr24-resume-cpu-context16k-long](../runs/bi-v150/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long.md)（登记#211）：32成功0失败，真实抢占1次 **是否保留：** 保留抢占证据；后续GPU窗口结果见同方法记录，不把CPU返回计时当收益。
- [20261024T113346Z-pr24-resume-native-context16k-long](../runs/bi-v150/20261024T113346Z-pr24-resume-native-context16k-long.md)（登记#212）：DB由8acaab58种子恢复207f1b，source/native未变，结束时GPU68MiB/0%且9031关闭 **是否保留：** 未集成；失败或无收益记录保留。
- [20261024T114500Z-pr24-resume-native-v2-context16k-long](../runs/bi-v150/20261024T114500Z-pr24-resume-native-v2-context16k-long.md)（登记#213）：32成功0失败；warmed种子仍有M457冷调优，窗口含同批decode，不报吞吐收益或完整可省预算 **是否保留：** 保留局部GPU预算，进入KV SAVE/FULL最短VERIFY1；尚未确认端到端收益。
