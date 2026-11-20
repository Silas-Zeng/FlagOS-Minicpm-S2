# 20261029T234221231370Z-q32-causal-interior-component

- **尝试与改动**：Q32 历史块掩码精简。源码、环境及精确命令见下方原件。
- **怎么测**：Q2018/context12108/KV14126，实际encoded-I8 K/BF16 V格式的A/B组件门。
- **结果与限制**：step1048的A/B逐位不等，finite/readonly/guard通过；未计时，候选停止且不修救。保留源码和编译证据，约41MB失败张量留在原件库。
- **是否保留**：停止候选，不进入计时或服务。候选未改动团队main。

[原始证据](../../../experiments/bundles/q32-component-234221/) · [本批证据索引](../../../analysis/publication-storage-q32-profile-20261030/evidence-index.json) · [登记源](../../../experiments/registry.csv)
