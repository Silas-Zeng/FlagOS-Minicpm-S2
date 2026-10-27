<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# CoreX Q32四页搬运编译探针

原checker搜索NVVM屏障而实际CoreX使用bi.sl.barrier，passed=false原样保留；sidecar仅接受同步与共享生命周期静态顺序。无GPU执行、坐标映射、数值或性能资格。

相关代码：[summary.json](../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/summary.json)；[raw-evidence.json](../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/raw-evidence.json)；[compile-backend-barrier-review.json](../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/compile-backend-barrier-review.json)；[review-compile-160904.py](../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/review-compile-160904.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T160904Z-native-q32-transfer-fragments](../runs/bi-v150/20261027T160904Z-native-q32-transfer-fragments.md)（登记#383）：CPU实编32SME/64MMA、64KiB；原checker=false，静态sidecar仅接受CoreX同步顺序。 **是否保留：** 保留编译可行性；无GPU、数值或性能资格。
