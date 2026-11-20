# 20261030T010749147245Z-q32-tile128-compile-probe

- **尝试与改动**：Q32 TILE128。
- **怎么测**：固定合成Q32 ABI，单次encoded writer后分别warmup编译A/B；BM256/BQ32/w16/stage1/grid(64,2)相同，仅TILE_SIZE A64/B128。实际effective SME分别记录。
- **结果**：固定合成ABI编译成功；B TILE128相对A TILE64的VGPR 135→164、shared 57,344→81,920 B、ASM SGPR spill计数98→128。runtime spill、ASM VGPR spill与ScratchSize均为0；有效SME均3。仅writer和编译，无Attention reader/数值/性能测试；保留待数值与组件门，不由资源数据单独宣判。
- **是否保留**：保留编译与资源记录，进入同几何数值/组件门；当前不宣称性能收益、官方成绩或生产资格。

[原件索引](../../../experiments/bundles/20261030T010749147245Z-q32-tile128-compile-probe/bundle-index.json) · [恢复包分块](../../../experiments/bundles/20261030T010749147245Z-q32-tile128-compile-probe/bundle-index.json) · [登记源](../../../experiments/registry.csv)
