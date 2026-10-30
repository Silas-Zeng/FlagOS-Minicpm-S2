# 20261030T002901364769Z-q32-head4-component

- **尝试与改动**：Q32 GQA head4 CTA拆分。
- **怎么测**：四个组件case检查A/B逐位一致、finite、guard、输入只读及changed-Q；主形状Q2018/context12108/KV14126，4组ABBA、每臂每组50次，测完整producer+reducer组件Event和host block。
- **结果**：四例逐位与guard/readonly门通过；Q2018/KV14126组件A/B Event为7.983063/10.274864 ms，B慢28.7083%，停止，不进入服务/官方测量。 实际use_sme=3；仅合成ABI组件结果，不是服务负载资格。
- **是否保留**：保留负结果，停止该CTA拆分候选。

[本轮原件索引](../../../experiments/bundles/20261030T002901364769Z-q32-head4-component/bundle-index.json) · [恢复包分块](../../../experiments/bundles/20261030T002901364769Z-q32-head4-component/bundle-index.json) · [登记源](../../../experiments/registry.csv)
