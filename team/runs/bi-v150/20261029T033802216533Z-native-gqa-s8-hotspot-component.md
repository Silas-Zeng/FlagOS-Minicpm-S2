<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T033802216533Z-native-gqa-s8-hotspot-component

- **尝试了什么：** 真实N30/S8容量资格组件；九类对照、逐位/FP64抽样与Graph等门通过。ABBA Event 1.0282070041→0.7649875879ms，省25.59985%；仅组件结果，不代表模型吞吐。
- **改了什么：** 把 C++ 容量从硬编码 30720 改为与正值池相等；CUDA 容量逻辑保持不变。
- **怎么测：** BI-V150 N30/S8 容量资格组件，九类对照、逐位/FP64抽样及 Graph 检查通过，ABBA Event 1.0282070041→0.7649875879 ms。 完整压缩原件按恢复包保存，见 [SHA逐文件清单](../../../experiments/bundles/20261029T033802216533Z-native-gqa-s8-hotspot-component/manifest.json) 与 [压缩包分块索引](../../../experiments/bundles/20261029T033802216533Z-native-gqa-s8-hotspot-component/raw.tar.gz.storage.json)。
- **结果怎样：** Event 1.0282070041→0.7649875879 ms，省25.59985%；这是组件数据，不能当模型吞吐收益。
- **是否保留：** 保留原件和结论；不据此新增基线。
