# 20261030T024939570521Z-q32-affine-pages-component

- **尝试与改动**：Q32 连续页仿射寻址。
- **怎么测**：固定Q32 encoded-I8/BF16-V组件，5个数值case及四组ABBA；原始结果、数值/计时审阅和恢复包见登记的证据路径。
- **结果**：5个case全输出逐位一致，选定CPU FP64、guard、只读与changed-Q检查通过。四组ABBA Event均值A7.989743/B7.876383 ms，省1.418813%，四组方向一致。仅理想连续页合成布局，未计descriptor构建/H2D且无真实覆盖率与生命周期验证；保留条件候选，不接服务、不更新基线。
- **是否保留**：保留为条件候选；下一步先核真实连续页覆盖率和descriptor构建/传输成本，再决定是否服务接入。

[原件索引](../../../experiments/bundles/20261030T024939570521Z-q32-affine-pages-component/bundle-index.json) · [恢复包分块](../../../experiments/bundles/20261030T024939570521Z-q32-affine-pages-component/bundle-index.json) · [登记源](../../../experiments/registry.csv)
