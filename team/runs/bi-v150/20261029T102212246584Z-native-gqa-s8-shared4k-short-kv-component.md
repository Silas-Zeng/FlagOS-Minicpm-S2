<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T102212246584Z-native-gqa-s8-shared4k-short-kv-component

- **尝试了什么：** 比较N30/S8原shared8KiB与shared4k K/V同址复用候选。
- **改了什么：** 只变共享缓冲区生命周期与V写入/读取地址；QK、softmax、PV数学与reducer保持。
- **怎么测：** 同bundle包含102155 CPU build记录；组件分别对KV16K/4K执行数值、FP64、Graph、输入/RNG检查和ABBA。 原始记录见[manifest](../../../experiments/bundles/20261029T102212246584Z-native-gqa-s8-shared4k-short-kv-component/manifest.json)和[分块索引](../../../experiments/bundles/20261029T102212246584Z-native-gqa-s8-shared4k-short-kv-component/raw.tar.gz.storage.json)。
- **结果怎样：** 两档Event与wall均正向；这是局部组件信号。
- **是否保留：** 保留组件候选观察；不声称官方收益/模型资格，不修改生产代码。
