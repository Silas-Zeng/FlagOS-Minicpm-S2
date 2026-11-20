<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# S2同CTA归约

首次编译失败；停止当前实现，无数值或性能结论。

相关代码：[archive-receipt.json](../../experiments/framework/20261027T043321686931Z-gqa-s2-incta-hotspot-component/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T043321686931Z-gqa-s2-incta-hotspot-component](../runs/bi-v150/20261027T043321686931Z-gqa-s2-incta-hotspot-component.md)（登记#359）：S2两段同CTA/w2并在核内归约，拟省全局partial读写和一次启动；保持原page16、KV布局与逐段数学。实际CoreX在首个candidate的TritonGPUAccelerateMatmul阶段编译失败；checks/timings均空，未取得数值或性能结论。停止当前实现，不改编译器、 **是否保留：** 停止当前实现，不进生产。
