<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# main6971 Graph真实热点诊断

保持生产源码，复用PR62诊断工具；Graph采样可用，fresh native FX证明缺项保留。图内插桩时间只用于排序，不作正常耗时或官方成绩。

相关代码：[posthoc.json](../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/actual/posthoc.json)；[summary.md](../../experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/posthoc-20261027/summary.md)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T083941Z-main6971-production-hotspot-4k](../runs/bi-v150/20261026T083941Z-main6971-production-hotspot-4k.md)（登记#318）：诊断adapter把Git mode120000符号链接解引用，源码身份检查在CPU阶段拒绝；未启动collector/服务/GPU。修为校验linktarget字节后另run执行，原失败保留。 **是否保留：** 保留入口失败；v2单独登记，不当模型错误或性能负。
- [20261026T084521Z-main6971-production-hotspot-4k](../runs/bi-v150/20261026T084521Z-main6971-production-hotspot-4k.md)（登记#319）：4K诊断256/256成功；Graph四samples、334bindings，API/数值/别名检查通过，实际prefill栈有效。无日志指向fresh FX，posthoc仍diagnostic_incomplete；正常退出、共享DB未变。不是官方吞吐/105。 **是否保留：** 保留可用Graph诊断，native FX缺口明示；分析实际热点，不把插桩时间当正常占比。
