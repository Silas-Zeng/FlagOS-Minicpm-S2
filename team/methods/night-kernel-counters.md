<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 夜间单核硬件计数尝试

只对原baseline prefill/GQA单核尝试ixkn计数，复用旧worker，不是候选复测。Prefill wrapper -11，worker结果已写且有61440B报告，但离线导入报Unknown device name（空）；GQA因launch-skip=0不被工具接受而立即255，无结果或报告。两轮DB/source/native/所属进程组及设备清理通过，失败一次即跳过，不修工具或重跑。CLI未产生可用metric；原SQLite事件仅可有限匹配来源，计数含义未闭合，见页尾原值补充。本run全部timing禁作收益、官方成绩或新增组件资格。小原件已回收，夜间阶段空窗另补完整封存回执；旧小包index与原记录保持，未将工具失败改成完整可用profiler。

相关代码：[entry.py](../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/source/entry.py)；[profile-import.txt](../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/profile-import.txt)；[prefill-baseline.ixkn-rep](../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/prefill-baseline.ixkn-rep)；[worker.log](../../experiments/profiles/20261025T170652502004Z-gqa-one-kernel-counters/worker.log)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T170235660423Z-prefill-one-kernel-counters](../runs/bi-v150/20261025T170235660423Z-prefill-one-kernel-counters.md)（登记#282）：wrapper exit -11；worker写完results并有61440B ixkn-rep，离线导入rc255/Unknown device name（空），CLI指标不可用；SQLite原事件只作有限来源核对。 **是否保留：** 保留工具失败，停止本次计数，不修不重跑；全部timing禁止作收益、官方成绩或新增组件资格。
- [20261025T170652502004Z-gqa-one-kernel-counters](../runs/bi-v150/20261025T170652502004Z-gqa-one-kernel-counters.md)（登记#283）：ixkn立即exit255：launch-skip参数0无效；未生成results.json或报告，未进入采样。 **是否保留：** 记录工具参数拒绝后跳过，不修不重跑；不判候选数值或性能失败。


## 后续完整封存

在A/B结束后的GPU空窗已补封两轮完整原件，完整包留远端。独立回执：[Prefill完整封存](../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/full-seal-receipt.json)、[GQA完整封存](../../experiments/profiles/20261025T170652502004Z-gqa-one-kernel-counters/full-seal-receipt.json)。旧小包index、原日志与原登记未改；完整包SHA与全文件SHA在回执中，不能把补封解释为工具重跑或计数恢复。
## 2026-10-26 本地只读补充

Prefill报告虽无法由CLI导入，但SQLite保留1条kernel活动和57条EVENT，均以iterator/coorelationid=934关联；名称`kernel_biv150_prefill_normalized`、grid128×2×1、block512、VRF114/SRF104/shared32768与本run原current基线BM128/T64/w8、M2047/KV16384相符。[原值导出](../../analysis/20261025T170235-prefill-raw-events.json)保留全部事件、配置对照和报告SHA；原SQLite未修改。仅支持来源匹配，报告没有cubin/hash或动态参数，不能宣称二进制逐字绑定。

DEVICE_INFO、METRIC与METRIC_DATA为空且wrapper exit -11；已有材料缺计数域、聚合、单位和metric公式，事件数值仍待解释。原shared-store conflicts130752336/transactions126742528、LLC两core hit合计24899406/req24998649、total_cycles803635136/active_cycles776790603均不转换为冲突率、整轮命中率、占用率或收益；time8363934也保留原值。没有修数据库、重跑或新方案，原工具失败与所有timing禁作成绩的结论不变。此补充不改既有登记原文。
