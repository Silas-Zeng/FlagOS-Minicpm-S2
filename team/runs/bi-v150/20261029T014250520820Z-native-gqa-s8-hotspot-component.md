# 20261029T014250520820Z-native-gqa-s8-hotspot-component

平台：天数 BI-V150。本页只记录组件筛查，不代表完整模型或官方成绩。

## 尝试、测量与结果

- **尝试**：真实生产路径单层 attention A/B 组件。
- **改动**：真实N30/S8组件，数值门通过；ABBA Event 1.029299→0.766297ms（快25.5515%），wall 1.032342→0.768814ms（快25.5272%），单次组件正向信号，等待端到端确认。
- **怎么测**：同一输入与ABI，四段 ABBA；原始恢复包 SHA 分块保存在 bundle。正确性门为单 shape/抽样范围。
- **是否保留**：保留组件正向信号与原始证据；须按团队规定完成端到端复现后再判断是否更新基线。

原件：[bundle](../../../experiments/bundles/20261029T014250520820Z-native-gqa-s8-hotspot-component)；恢复源：`archive/native-gqa-s8-20261029/batch-014250-component-positive`。
