# 20261029T233910926379Z-q32-causal-interior-component

- **尝试与改动**：Q32 历史块掩码精简。源码、环境及精确命令见下方原件。
- **怎么测**：真实调度形状的组件入口；helper SHA抄写错误导致编译前退出。
- **结果与限制**：入口helper SHA与冻结身份不匹配，benchmark/编译前停止，无性能样本；保留失败记录。
- **是否保留**：保留入口失败证据；此轮未执行候选内核。

[原始证据](../../../experiments/bundles/q32-entry-233910/) · [本批证据索引](../../../analysis/publication-storage-q32-profile-20261030/evidence-index.json) · [登记源](../../../experiments/registry.csv)
