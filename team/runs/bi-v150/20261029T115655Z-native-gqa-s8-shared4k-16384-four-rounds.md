<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T115655Z-native-gqa-s8-shared4k-16384-four-rounds

- **尝试了什么：** 筛选N30/S8 shared4k候选的官方16K吞吐表现。
- **改了什么：** PR105 N30/S8 producer接入shared4k实现；仅BF16、Q stride=2048命中，其余回退保持。
- **怎么测：** 沿用官方脚本/服务参数，16384输入、1024输出、并发64、每轮128请求；完成四轮，弃首轮比较PR105。；原件见[manifest](../../../experiments/bundles/20261029T115655Z-native-gqa-s8-shared4k-16384-four-rounds/manifest.json)和[压缩包分块索引](../../../experiments/bundles/20261029T115655Z-native-gqa-s8-shared4k-16384-four-rounds/raw.tar.gz.storage.json)。
- **结果怎样：** 暖均4908.913333 tok/s，对PR105 4832.66为观察+1.577875%；KV容量差48 tokens。
- **是否保留：** 保留为完整官方16K正向观察；不作严格因果、新基线或准确率资格，4K另行筛选。
