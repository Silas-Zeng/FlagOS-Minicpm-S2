<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T075911Z-native-gqa-s8-source-build

- **尝试了什么：** 为N30/S8组件准备实际source build和SO身份。
- **改了什么：** 构建固定source树并生成build receipt；限定build_only，未发起GPU workload。
- **怎么测：** 核查source files、build summary与SO SHA；原件manifest逐项SHA复核。 原始记录见[manifest](../../../experiments/bundles/20261029T075911Z-native-gqa-s8-source-build/manifest.json)和[分块索引](../../../experiments/bundles/20261029T075911Z-native-gqa-s8-source-build/raw.tar.gz.storage.json)。
- **结果怎样：** CPU build-only完成；产物身份可供后续组件参考，不含GPU验证。
- **是否保留：** 保留为构建/身份记录，不视为性能或生产资格。
