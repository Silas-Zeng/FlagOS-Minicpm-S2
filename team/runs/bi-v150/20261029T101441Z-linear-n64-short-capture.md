<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T101441Z-linear-n64-short-capture

- **尝试了什么：** 用有界capture检查该profile窗口是否观察到目标N64 linear调用。
- **改了什么：** 没有改变kernel、模型或评测参数；采集driver异常退出。
- **怎么测：** 保留final/owner日志、profile与DB状态；本轮未得到目标launch证据。 原始记录见[manifest](../../../experiments/bundles/20261029T101441Z-linear-n64-short-capture/manifest.json)和[分块索引](../../../experiments/bundles/20261029T101441Z-linear-n64-short-capture/raw.tar.gz.storage.json)。
- **结果怎样：** 本次采集未观察到可用目标调用；不是全局不存在该调用的证明。
- **是否保留：** 保留无观察诊断；不转为性能或实现结论。
