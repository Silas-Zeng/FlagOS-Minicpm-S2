# 20261030T005910507361Z-q32-key-scale-compile-probe

- **尝试与改动**：Q32 K-scale每tile尺度融合。
- **怎么测**：按原bundle中的固定命令与环境执行；终态/审阅边界见原件索引。
- **结果**：TTGIR循环内score乘法由3次降至2次，ASM SGPR spill计数98→99；runtime regs135/shared57344，runtime spills0、VGPR spills0、ScratchSize0。仅编译探针，无attention reader数值或性能，不是收益或生产资格。
- **是否保留**：保留本轮证据；不超出review结论作资格、收益或基线判断。

[原件索引](../../../experiments/bundles/20261030T005910507361Z-q32-key-scale-compile-probe/bundle-index.json) · [恢复包分块](../../../experiments/bundles/20261030T005910507361Z-q32-key-scale-compile-probe/bundle-index.json) · [登记源](../../../experiments/registry.csv)
