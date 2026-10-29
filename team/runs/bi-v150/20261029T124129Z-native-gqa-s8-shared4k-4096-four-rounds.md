<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T124129Z-native-gqa-s8-shared4k-4096-four-rounds

- **尝试了什么：** 按官方首暖筛选规则评估shared4k S8候选4K负载。
- **改了什么：** 运行同一shared4k S8接入；保持官方服务及评测参数，未改变候选实现。
- **怎么测：** 官方4K输入4096、输出1024、并发64、512请求；记录两轮，在第二轮按负向筛选规则停止。；原件见[manifest](../../../experiments/bundles/20261029T124129Z-native-gqa-s8-shared4k-4096-four-rounds/manifest.json)和[压缩包分块索引](../../../experiments/bundles/20261029T124129Z-native-gqa-s8-shared4k-4096-four-rounds/raw.tar.gz.storage.json)。
- **结果怎样：** 第二轮6204.95 tok/s，对PR105 6441.35低3.670038%；512请求成功，KV差48 tokens。
- **是否保留：** 保留两轮负向筛选结果；不扩为四轮、不称框架错误，不建立基线或准确率资格。
