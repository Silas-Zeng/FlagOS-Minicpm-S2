<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# C3重复视图清理

复用mixed Attention中的视图，减少重复slice/unbind；短输入信号与大输入、真实服务结果分别记录。

相关代码：[biv150_c3_view_reuse.py](../../patches/framework/candidates/biv150_c3_view_reuse.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T104449Z-c3-views-gate](../runs/bi-v150/20261022T104449Z-c3-views-gate.md)（登记#125）：wall增加0.3177%，event增加0.1112%；不外推服务吞吐或整模型accuracy **是否保留：** 未集成；失败或无收益记录保留。
- [20261022T105635Z-small-input-c3views-gate](../runs/bi-v150/20261022T105635Z-small-input-c3views-gate.md)（登记#129）：wall从0.460218219到0.432736688ms，耗时降低5.9714%；仅单层短形状信号，不外推整体吞吐或整模型accuracy **是否保留：** 保留作候选，仍待确认；不等于默认启用。
