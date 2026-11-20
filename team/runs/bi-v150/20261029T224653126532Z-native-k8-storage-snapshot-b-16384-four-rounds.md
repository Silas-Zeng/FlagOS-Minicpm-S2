# 20261029T224653126532Z-native-k8-storage-snapshot-b-16384-four-rounds

- **尝试与改动**：Storage 元数据单次调用复用。源码、环境及精确命令见下方原件。
- **怎么测**：官方16K/1024、并发64、128请求，共4轮；与205801 A比较。
- **结果与限制**：四轮3923.23/4555.17/4551.99/4550.26，弃首轮均值4552.473333 tok/s；相对同起始DB的A 4548.78观察+0.0812%。KV页相同，末态调优DB不同；仅小幅观察，不宣称稳定因果收益，不升级基线。
- **是否保留**：保留小幅观察，不升级基线；完整准确率未测。

[原始证据](../../../experiments/bundles/storage-B-224653/) · [本批证据索引](../../../analysis/publication-storage-q32-profile-20261030/evidence-index.json) · [登记源](../../../experiments/registry.csv)
