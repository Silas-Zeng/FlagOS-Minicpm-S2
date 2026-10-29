<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T051320Z-prefill-base2-cpu-compile

- **尝试了什么：** 尝试启动base2 CPU编译检查。
- **改了什么：** 入口引用的run_compile.py路径不存在。
- **怎么测：** CPU owner入口和launcher原日志；未运行编译或设备代码。 见[逐文件manifest](../../../experiments/bundles/20261029T051320Z-prefill-base2-cpu-compile/manifest.json)和[压缩包分块索引](../../../experiments/bundles/20261029T051320Z-prefill-base2-cpu-compile/raw.tar.gz.storage.json)。
- **结果怎样：** 启动前报文件不存在；无数值或性能测量。
- **是否保留：** 保留入口路径失败原件，不判候选正确性/性能。
