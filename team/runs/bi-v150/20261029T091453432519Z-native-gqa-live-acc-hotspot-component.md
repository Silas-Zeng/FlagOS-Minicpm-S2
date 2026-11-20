<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T091453432519Z-native-gqa-live-acc-hotspot-component

- **尝试了什么：** 复核N32/S4 live-acc producer的热点组件代价。
- **改了什么：** 保持原macro1对照与live-acc候选数学和reducer。
- **怎么测：** 固定KV16K，检查数值/FP64抽样/Graph及side-effect，再做暖组件ABBA。 原始记录见[manifest](../../../experiments/bundles/20261029T091453432519Z-native-gqa-live-acc-hotspot-component/manifest.json)和[分块索引](../../../experiments/bundles/20261029T091453432519Z-native-gqa-live-acc-hotspot-component/raw.tar.gz.storage.json)。
- **结果怎样：** Event慢0.0135%，wall差极小且方向不一致；候选按Event负信号停止。
- **是否保留：** 保留负观察，不扩展到官方或模型测试。
