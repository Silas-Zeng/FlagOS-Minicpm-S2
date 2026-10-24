<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# PR24 组合基线与 KV 抢占诊断

复用队友已合并的 INT8 gate/up、PR15/PR21 与 Q fragment 组合；本实例 SO 的9项检查通过，短服务32请求全成功。长输出观察覆盖1次抢占，重复提交与旧CPU已提交前缀重叠5446 tokens；M1441冷调优影响CPU计时，尚不能推算GPU收益。原收尾失败及DB恢复证据保留，下一步仅采一次已调优的恢复窗口。

相关代码：[pr24-kv-diagnostic.json](../../analysis/pr24-kv-diagnostic.json)；[pr24-resume-db-comparison.json](../../analysis/pr24-resume-db-comparison.json)；[summary.json](../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/summary.json)；[native-build-manifest.json](../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/native-build-manifest.json)；[operator-check.json](../../experiments/framework/20261024T105037Z-pr24-main-context16k-control/operator-check.json)。

相关方法PR：[INT8 gate/up 组合 #24](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/24)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261024T105037Z-pr24-main-context16k](../runs/bi-v150/20261024T105037Z-pr24-main-context16k.md)（登记#210）：结束exit0、源未变、GPU68MiB/0%、DB已恢复；32成功0失败，total tok/s=5121.780601，仅单臂不报性能收益 **是否保留：** 保留作本实例后续基线；组合已由PR24合并，短验不计性能收益或完整准确率。
- [20261024T110545Z-current-main-pr24-resume-cpu-context16k-long](../runs/bi-v150/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long.md)（登记#211）：32成功0失败，真实抢占1次 **是否保留：** 保留抢占证据；KV SAVE/FULL仍为候选，GPU开销待一次已调优窗口确认。
