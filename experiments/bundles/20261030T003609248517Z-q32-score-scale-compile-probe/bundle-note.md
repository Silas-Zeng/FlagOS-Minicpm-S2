# 20261030T003609248517Z-q32-score-scale-compile-probe

- **尝试与改动**：Q32 score-scale循环外提。
- **怎么测**：两臂使用共同BM256/grid-y2/w16 writer ABI，仅编译并检查TTGIR/ASM资源；worker启动一次writer以取得真实tensor参数，未启动Attention reader。
- **结果**：TTGIR循环内score乘法3→2；ASM SGPR spill计数98→110，资源差异未闭合。无reader数值/性能测量，暂缓，不作收益或生产资格结论。 Triton runtime spills=0、VGPR spill=0、ScratchSize=0，但SGPR计数差异未解释。
- **是否保留**：暂缓；需先解释资源差异并补数值门，当前不进入生产或收益判断。

[本轮原件索引](../../../experiments/bundles/20261030T003609248517Z-q32-score-scale-compile-probe/bundle-index.json) · [恢复包分块](../../../experiments/bundles/20261030T003609248517Z-q32-score-scale-compile-probe/bundle-index.json) · [登记源](../../../experiments/registry.csv)
