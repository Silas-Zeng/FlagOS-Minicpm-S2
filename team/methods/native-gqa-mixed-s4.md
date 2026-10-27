<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 原生BF16 GQA：mixed S4覆盖扩展

原c75db仅覆盖B64/S2与B32/S4，真实mixed prefix61原回落Triton。B61/B60完整mixed组件Event省8.8533%/25.5143%、B63位型通过；仅helper/CPP扩32–63且排40，CU/chooser/S2不动。原官方4K两轮首暖6168.07对A6301.93观察−2.1241%后主动停，KV548432对548336不同，不能严格归因。候选不合并，停止16K/105，不定新基线；正确性门通过与性能筛选负分列。

相关代码：[summary.json](../../experiments/framework/20261027T181731151743Z-corex-native-gqa-mixed61-component/summary.json)；[raw-evidence.json](../../experiments/framework/20261027T181731151743Z-corex-native-gqa-mixed61-component/raw-evidence.json)；[manifest.json](../../experiments/bundles/20261027T181731151743Z-corex-native-gqa-mixed61-component/manifest.json)；[raw.tar.xz.storage.json](../../experiments/bundles/20261027T181731151743Z-corex-native-gqa-mixed61-component/raw.tar.xz.storage.json)；[summary.json](../../experiments/cpu-probes/20261027T182749Z-native-gqa-mixed-s4-production-build/summary.json)；[raw-evidence.json](../../experiments/cpu-probes/20261027T182749Z-native-gqa-mixed-s4-production-build/raw-evidence.json)；[manifest.json](../../experiments/bundles/20261027T182749Z-native-gqa-mixed-s4-production-build/manifest.json)；[raw.tar.gz.storage.json](../../experiments/bundles/20261027T182749Z-native-gqa-mixed-s4-production-build/raw.tar.gz.storage.json)；[summary.json](../../experiments/framework/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/summary.json)；[raw-evidence.json](../../experiments/framework/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/raw-evidence.json)；[manifest.json](../../experiments/bundles/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/manifest.json)；[raw.tar.gz.storage.json](../../experiments/bundles/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/raw.tar.gz.storage.json)；[summary.json](../../experiments/official/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/summary.json)；[raw-evidence.json](../../experiments/official/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/raw-evidence.json)；[manifest.json](../../experiments/bundles/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/manifest.json)；[raw.tar.gz.storage.json](../../experiments/bundles/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/raw.tar.gz.storage.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T181731151743Z-corex-native-gqa-mixed61-component](../runs/bi-v150/20261027T181731151743Z-corex-native-gqa-mixed61-component.md)（登记#395）：回放真实step125的61decode＋1987prefill CPU几何，随机QKV；私有B61桥直接链接同f720 S4导出，CU不重编。 **是否保留：** 保留候选；等待独立模型／官方验证。
- [20261027T182749Z-native-gqa-mixed-s4-production-build](../runs/bi-v150/20261027T182749Z-native-gqa-mixed-s4-production-build.md)（登记#396）：f6b4候选仅Python／CPP两文件扩原已选S4的32≤B≤63并排40，原CU a8b1／S2／chooser／macro0不变。 **是否保留：** 保留编译／身份依据；不授数值或性能。
- [20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component](../runs/bi-v150/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component.md)（登记#397）：只加载新b9bff11d SO：A旧Runtime guard自然回Triton，B实际新生产_Runtime；真实step123 B60＋1988／step129 B63＋1985。 **是否保留：** 保留候选；等待独立模型／官方验证。
- [20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds](../runs/bi-v150/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds.md)（登记#398）：原官方4K两轮512成功；首暖6168.07对6301.93观察−2.1241%，按预设主动停止。 **是否保留：** 候选不合并；停止16K/105，不更新基线。
