<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T061308Z-native-gqa-s8-native14f-math500

- **尝试了什么：** 按原batch8与服务参数完成Math_500 Level3原105准确率评估。
- **改了什么：** 819-file PR105 overlay启用S8库；自然负载无N30/S8 selected/captured，不称105题覆盖该分支。
- **怎么测：** 评审105份输出/stop状态并核报告、预测、评审文件SHA；逐项核对原件manifest。 见[逐文件manifest](../../../experiments/bundles/20261029T061308Z-native-gqa-s8-native14f-math500/manifest.json)和[压缩包分块索引](../../../experiments/bundles/20261029T061308Z-native-gqa-s8-native14f-math500/raw.tar.gz.storage.json)。
- **结果怎样：** 101/105（96.1905%）达到至少100正确；无传输错误、截断或空答案；S8为not_exercised。
- **是否保留：** 保留准确率门通过；不作S8分支覆盖、性能或新基线结论。
