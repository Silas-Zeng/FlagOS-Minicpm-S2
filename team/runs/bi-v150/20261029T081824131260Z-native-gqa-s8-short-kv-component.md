<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T081824131260Z-native-gqa-s8-short-kv-component

- **尝试了什么：** 测量N30/S8 native producer在KV16K与KV4K的组件路径。
- **改了什么：** 固定N30/S8实现，分别测试两档KV长度，没有新增长度分流。
- **怎么测：** ABBA组件计时及完整输出、partial、FP64抽样、Graph、side/input/RNG检查。 原始记录见[manifest](../../../experiments/bundles/20261029T081824131260Z-native-gqa-s8-short-kv-component/manifest.json)和[分块索引](../../../experiments/bundles/20261029T081824131260Z-native-gqa-s8-short-kv-component/raw.tar.gz.storage.json)。
- **结果怎样：** 两档组件Event均有明显下降；本结果不等同端到端官方吞吐。
- **是否保留：** 保留局部正信号；不授生产、官方或完整S8准确率资格。
