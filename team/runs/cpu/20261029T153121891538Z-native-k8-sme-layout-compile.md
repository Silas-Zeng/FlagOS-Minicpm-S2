<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T153121891538Z-native-k8-sme-layout-compile

- **尝试了什么：** 验证目标工具链能否编译隔离SME布局探针。
- **改了什么：** 新增probe-only CU测试入口；不改生产kernel。
- **怎么测：** BI-V150 CoreX编译；保存build命令、SO、IR、ASM及环境/源码身份。
- **结果怎样：** 编译退出0，实际SO身份与GPU运行状态一致；无吞吐测量。
- **是否保留：** 保留为布局探针的编译证据，不赋予模型或生产资格。

原件：[manifest](../../../experiments/bundles/20261029T153121891538Z-native-k8-sme-layout-compile/manifest.json)；[恢复包分块索引](../../../experiments/bundles/20261029T153121891538Z-native-k8-sme-layout-compile/raw.tar.gz.storage.json)。
