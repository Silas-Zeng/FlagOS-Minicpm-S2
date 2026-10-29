<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T051506Z-prefill-base2-cpu-compile

- **尝试了什么：** 修复入口后尝试编译base2 normal与Q-hoisted两臂。
- **改了什么：** source reader把源码字符串作为Path.read_text路径，触发文件名过长。
- **怎么测：** CPU-only编译；normal B已有产物，Q-hoisted B未完成。 见[逐文件manifest](../../../experiments/bundles/20261029T051506Z-prefill-base2-cpu-compile/manifest.json)和[压缩包分块索引](../../../experiments/bundles/20261029T051506Z-prefill-base2-cpu-compile/raw.tar.gz.storage.json)。
- **结果怎样：** 工具读取路径错误而退出；无GPU数值或性能结论。
- **是否保留：** 保留source-reader失败，不归为kernel失败。
