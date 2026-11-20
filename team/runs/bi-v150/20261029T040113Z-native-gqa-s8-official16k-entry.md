<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T040113Z-native-gqa-s8-official16k-entry

- **尝试了什么：** 官方16K入口在启动前接线失败，benchmark未开始；无模型数值和性能结果。
- **改了什么：** 失败原因是 receipt SHA 嵌套字段的读取路径写错；入口取值失败后在 benchmark 前退出。
- **怎么测：** BI-V150 官方16K启动前 receipt identity 检查；因 SHA 字段路径错误退出，无请求或吞吐计时。 完整压缩原件按恢复包保存，见 [SHA逐文件清单](../../../experiments/bundles/20261029T040113Z-native-gqa-s8-official16k-entry/manifest.json) 与 [压缩包分块索引](../../../experiments/bundles/20261029T040113Z-native-gqa-s8-official16k-entry/raw.tar.gz.storage.json)。
- **结果怎样：** receipt SHA 嵌套字段路径读取错误，benchmark未启动；不属于模型数值或性能结果。
- **是否保留：** 保留原件和结论；不据此新增基线。
