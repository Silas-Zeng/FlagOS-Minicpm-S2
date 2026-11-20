<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 采样转换与首遍统计融合

v2统计逐位门失败，停止；无性能计时，原件已完整回收。

相关代码：[archive-receipt.json](../../experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component/archive-receipt.json)；[ssh-readback-summary.json](../../experiments/framework/20261027T031858174112Z-sampler-preprocess-stats-component/ssh-readback-summary.json)；[archive-receipt.json](../../experiments/framework/20261027T031858174112Z-sampler-preprocess-stats-component/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T030446321226Z-sampler-preprocess-stats-component](../runs/bi-v150/20261027T030446321226Z-sampler-preprocess-stats-component.md)（登记#357）：首包f3e99d0a在候选执行前失败：入口PYTHONPATH只包含assets，导入安装旧vllm_fl，缺biv150_runtime，ImportError。cases/timings均空，尚无数值或性能结论，也不是生产框架报错。保留原包和26原件；下一包仅绑定main241765源码路径及复 **是否保留：** 保留原启动失败，只修入口源码路径后单独重试；无收益或数值结论。
- [20261027T031858174112Z-sampler-preprocess-stats-component](../runs/bi-v150/20261027T031858174112Z-sampler-preprocess-stats-component.md)（登记#358）：采样融合v2真实head首组scaled/filtered/IDs/RNG相同，但stats_bitwise=false，按预定门停止；无计时，后续换值/Graph/性能未运行。不能称原main预测错误，也不接受为等价候选。DB恢复、source/native不变；36份原始文件已完整回收并逐SHA **是否保留：** 停止当前实现，无性能或官方资格。
