<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T154519134404Z-native-k8-sme-lookahead-compile

- **尝试了什么：** 检查K lookahead SME候选与原S2/S4配置能否在编译ASM中形成预期发射顺序。
- **改了什么：** 仅有隔离base/candidate源码；未接入生产kernel。
- **怎么测：** 两臂CoreX standalone compile-only，独审比较LLVM/ASM及编译资源；没有linked SO或GPU执行。
- **结果怎样：** S2/S4 next-K SME在当前PV前发射；PV后及loop header存在g2scnt wait。VGPR 85→70、SGPR 70→72、shared 8192B、scratch 0。
- **是否保留：** 仅保留CPU compile/ASM顺序观察；不能证明实际重叠、Attention正确性、吞吐收益或生产资格。

原件：[manifest](../../../experiments/bundles/20261029T154519134404Z-native-k8-sme-lookahead-compile/manifest.json)；[恢复包分块索引](../../../experiments/bundles/20261029T154519134404Z-native-k8-sme-lookahead-compile/raw.tar.gz.storage.json)。
