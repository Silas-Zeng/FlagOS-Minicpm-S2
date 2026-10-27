<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# CoreX Q32四页搬运与M16映射诊断

160904原checker失败与CoreX sidecar静态接受分列；164809两次launch固定映射对独立FP64逐位通过。尚无softmax、Graph、完整Attention、性能或模型准确率资格。

相关代码：[summary.json](../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/summary.json)；[raw-evidence.json](../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/raw-evidence.json)；[compile-backend-barrier-review.json](../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/compile-backend-barrier-review.json)；[review-compile-160904.py](../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/review-compile-160904.py)；[summary.json](../../experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/summary.json)；[raw-evidence.json](../../experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/raw-evidence.json)；[manifest.json](../../experiments/bundles/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/manifest.json)；[raw.tar.gz.storage.json](../../experiments/bundles/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/raw.tar.gz.storage.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T160904Z-native-q32-transfer-fragments](../runs/bi-v150/20261027T160904Z-native-q32-transfer-fragments.md)（登记#383）：CPU实编32SME/64MMA、64KiB；原checker=false，静态sidecar仅接受CoreX同步顺序。 **是否保留：** 保留编译可行性；无GPU、数值或性能资格。
- [20261027T164809092948Z-native-q32-m16-mapping-diagnostic](../runs/bi-v150/20261027T164809092948Z-native-q32-m16-mapping-diagnostic.md)（登记#386）：两次launch固定映射，换值QK16384/PV32768值对CPU FP64 cast FP32逐位通过。 **是否保留：** 保留M16映射依据；非完整Attention或性能资格。
