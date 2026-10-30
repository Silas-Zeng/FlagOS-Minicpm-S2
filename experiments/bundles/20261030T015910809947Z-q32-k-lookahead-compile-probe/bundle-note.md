# 20261030T015910809947Z-q32-k-lookahead-compile-probe

- **尝试与改动**：Q32 K-only lookahead。
- **怎么测**：按原bundle中的固定命令与环境执行；终态/审阅边界见原件索引。
- **结果**：编译审阅在QK后、PV前定位到下一tile的页/K/scale加载，当前tile PV之后有完整vmcnt等待、下一轮才消费carry K，形成可能的重叠窗口；这只是机制窗口证据，未证明隐藏延迟或速度收益。VGPR135/shared57344均未上升，ASM SGPR spill计数98→88；仅writer与编译，无reader、数值或性能。
- **是否保留**：保留本轮证据；不超出review结论作资格、收益或基线判断。

[原件索引](../../../experiments/bundles/20261030T015910809947Z-q32-k-lookahead-compile-probe/bundle-index.json) · [恢复包分块](../../../experiments/bundles/20261030T015910809947Z-q32-k-lookahead-compile-probe/bundle-index.json) · [登记源](../../../experiments/registry.csv)
