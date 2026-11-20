<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T071002153051Z-native-gqa-s8-short-kv-component

- **尝试了什么：** 测量N30/S8 native producer在KV16K与KV4K下的局部短KV组件时延。
- **改了什么：** 同一N30/S8 producer与固定Q stride；不增加长度分流。
- **怎么测：** 两个固定shape分别做Triton/native/native/Triton ABBA，每臂32 calls；检查数值、Graph、stream、guard及RNG。 见[原件manifest](../../../experiments/bundles/20261029T071002153051Z-native-gqa-s8-short-kv-component/manifest.json)与[压缩包分块索引](../../../experiments/bundles/20261029T071002153051Z-native-gqa-s8-short-kv-component/raw.tar.gz.storage.json)。
- **结果怎样：** KV16K与KV4K的Event和wall均下降；这是组件结果，不是官方吞吐或准确率。
- **是否保留：** 保留两个长度的局部正信号；等待生产/官方证据决定适用范围。
