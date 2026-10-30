# 20261030T011120000584Z-q32-key-scale-component

- **尝试与改动**：Q32 K-scale每tile尺度融合。
- **怎么测**：固定合成ABI、Q2018/context12108/KV14126，原encoded writer与单Attention reader；五例（主形状、changed-Q、无历史、短、尾Q）数值/guard/只读与4组ABBA各50次。posthoc CPU输出检查单独记录，不更改原始summary。
- **结果**：四组ABBA Event A7.9743986/B8.0439349 ms，B慢0.872%，性能负向并停止、不重测。五例各臂选定FP64抽样通过；full-output helper报告AB非逐位却max-abs=0，CPU回读五份均见非零差且均在点式门内，全量AB数值门未闭合。不能称全数值通过，也不是已确认候选错误；原summary保持不变，附posthoc CPU脚本与JSON。
- **是否保留**：保留负向观察与数值门未闭合的证据边界；停止候选，不进官方或生产资格，不重测。

[原件索引](../../../experiments/bundles/20261030T011120000584Z-q32-key-scale-component/bundle-index.json) · [恢复包分块](../../../experiments/bundles/20261030T011120000584Z-q32-key-scale-component/bundle-index.json) · [登记源](../../../experiments/registry.csv)
