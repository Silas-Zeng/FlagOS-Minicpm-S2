<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# NativeK8 SME布局与组件实验

此前完整页K-stage字节布局探针16案/96项检查通过；lookahead独立compile/ASM顺序门通过。此次新增A/B最终SO pair-build与producer+原reducer组件试验。A/B SO符号隔离、20参数ABI一致。四组组件case逐位数值、全长度、Graph变Q、输入只读和redzone均通过，Event分别减少2.0675%、2.7325%、2.2473%、2.2759%；但4K Q stride2560 wall反向变慢2.1025%。组件信号不等于稳定收益、模型服务吞吐、准确率或生产资格。

详见[SO构建短记](../runs/cpu/20261029T155955570211Z-native-k8-sme-pair-build.md)和[组件短记](../runs/bi-v150/20261029T161341635355Z-native-k8-sme-component.md)，原始ABBA样本及复核在对应bundle。
