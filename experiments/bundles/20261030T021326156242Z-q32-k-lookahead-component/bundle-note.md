# 20261030T021326156242Z-q32-k-lookahead-component

- **尝试与改动**：Q32 K-only lookahead。
- **怎么测**：按原bundle中的固定命令与环境执行；终态/审阅边界见原件索引。
- **结果**：五个case（含changed-Q）全输出A/B逐位一致，CPU FP64抽样、guard、只读输入/缓存/表及重复稳定性通过。四组ABBA Event A8.031193/B8.537401 ms，B慢6.303%；四组分别慢7.0392%、7.0048%、6.8048%、4.4104%。停止此版，不进服务或官方测试，不升级基线。
- **是否保留**：保留本轮证据；不超出review结论作资格、收益或基线判断。

[原件索引](../../../experiments/bundles/20261030T021326156242Z-q32-k-lookahead-component/bundle-index.json) · [恢复包分块](../../../experiments/bundles/20261030T021326156242Z-q32-k-lookahead-component/bundle-index.json) · [登记源](../../../experiments/registry.csv)
