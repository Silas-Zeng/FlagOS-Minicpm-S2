# 20261030T012148540966Z-q32-tile128-component

- **尝试与改动**：Q32 TILE128。
- **怎么测**：固定合成Q32 ABI，主形状Q2018/context12108/KV14126，另含changed-Q、无历史、短与尾形状；按原reference、逐点容差、guard/只读检查及4组ABBA各50次测单reader。
- **结果**：五个合成ABI case 的A/B逐点门、FP64抽样、guard/readonly/changed-Q及同臂稳定检查均通过。四组ABBA Event A7.9793690/B8.4068933 ms，B慢5.358%；停止TILE128候选，不进官方/生产资格，不更新基线。
- **是否保留**：数值门通过但组件性能为负，停止候选；保留编译资源成本与本轮原件，不进服务/官方，不更新基线。

[原件索引](../../../experiments/bundles/20261030T012148540966Z-q32-tile128-component/bundle-index.json) · [恢复包分块](../../../experiments/bundles/20261030T012148540966Z-q32-tile128-component/bundle-index.json) · [登记源](../../../experiments/registry.csv)
