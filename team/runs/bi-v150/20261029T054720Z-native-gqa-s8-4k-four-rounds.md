<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T054720Z-native-gqa-s8-4k-four-rounds

- **尝试了什么：** 检验N30/S8生产接入在官方4K下的端到端影响。
- **改了什么：** PR105 producer新增N30/S8 producer；仅BF16且Q stride=2048命中，其余fallback。
- **怎么测：** 原官方4K四轮，每轮256请求；首暖筛选正向后完成四轮。 见[逐文件manifest](../../../experiments/bundles/20261029T054720Z-native-gqa-s8-4k-four-rounds/manifest.json)和[压缩包分块索引](../../../experiments/bundles/20261029T054720Z-native-gqa-s8-4k-four-rounds/raw.tar.gz.storage.json)。
- **结果怎样：** 暖均6594.42 tok/s，对PR105 6627.816667低0.5039%；KV差48，不能严格归因或更新基线。
- **是否保留：** 保留完整负向观察，与16K正向并列；不更新基线。
