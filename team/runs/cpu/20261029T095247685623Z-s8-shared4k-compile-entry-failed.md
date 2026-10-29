<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T095247685623Z-s8-shared4k-compile-entry-failed

- **尝试了什么：** 尝试运行shared4k候选的CoreX compile-only入口。
- **改了什么：** 未形成编译结果；shell脚本换行符导致解析失败。
- **怎么测：** 检查owner结果与原始shell日志；没有kernel launch、数值门或计时。 原始记录见[manifest](../../../experiments/bundles/20261029T095247685623Z-s8-shared4k-compile-entry-failed/manifest.json)和[分块索引](../../../experiments/bundles/20261029T095247685623Z-s8-shared4k-compile-entry-failed/raw.tar.gz.storage.json)。
- **结果怎样：** 入口工具失败，不代表候选源码编译/数值/性能失败。
- **是否保留：** 保留失败原件，后续LF修复后独立重试。
