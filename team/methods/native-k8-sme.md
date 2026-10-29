<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# NativeK8 SME布局与lookahead组件探针

完整页K-stage字节布局探针通过；lookahead两臂standalone compile/ASM顺序门通过。新增producer+原reducer组件4-case结果逐位数值/Graph/input门全通过，Event改善2.07–2.73%，但4K Q stride2560 wall反向慢2.10%。均为组件/编译证据，不代表attention完整正确性、官方吞吐、模型准确率或生产资格。 本批新增一次A臂CRLF入口失败（benchmark未启动）及A/B官方4K四轮筛选。A暖均6779.836667、B暖均6796.443333 tok/s，观察+0.244941987%；末两轮均值B反低0.1422675%。共同冻结DB起步，但末态私有3_6 DB为1bf0…/53fe…（585表21832行/581表22030行），KV为34277/34271页；不作严格因果或稳定收益结论，不更新基线。无模型准确率。

相关代码：[experiment-note.md](../../analysis/publication-k8-sme-20261029/experiment-note.md)；[native_k8_sme_A.cu](../../experiments/bundles/20261029T155955570211Z-native-k8-sme-pair-build/source/native_k8_sme_A.cu)；[native_k8_sme_B.cu](../../experiments/bundles/20261029T155955570211Z-native-k8-sme-pair-build/source/native_k8_sme_B.cu)；[worker.py](../../experiments/bundles/20261029T161341635355Z-native-k8-sme-component/source/worker.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261029T153349258627Z-native-k8-sme-layout](../runs/bi-v150/20261029T153349258627Z-native-k8-sme-layout.md)（登记#511）：16个布局案例/96项检查全部通过：isolated 2048B K head stage图像A/B逐字节相同，CPU reference、输入不变、guard通过 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261029T161341635355Z-native-k8-sme-component](../runs/bi-v150/20261029T161341635355Z-native-k8-sme-component.md)（登记#514）：4组数值/Graph边界通过；Event四项减少2.07–2.73%，4K Q stride2560 wall反向慢2.10%。 **是否保留：** 保留为局部producer+原reducer组件候选信号；不作稳定模型/官方吞吐、准确率或新基线资格。
- [20261029T165859246696Z-native-k8-sme-dispatcher-boundary](../runs/bi-v150/20261029T165859246696Z-native-k8-sme-dispatcher-boundary.md)（登记#516）：bitwise、original reducer、side-stream、changed-Q Graph bitwise、Q/storage/lengths/table只读与guards **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261029T174727581180Z-native-k8-sme-a-4096-four-rounds](../runs/bi-v150/20261029T174727581180Z-native-k8-sme-a-4096-four-rounds.md)（登记#517）：A臂main899官方4K服务启动未ready，benchmark未发出（0行）；根因为Windows git archive产生CRLF、源码依赖SHA不符。无模型数值/准确率/吞吐结论。 **是否保留：** 保留启动失败；使用逐Git blob SHA核验的原始字节包另run重试，A/B结果待回收复核。
- [20261029T175900061663Z-native-k8-sme-a-4096-four-rounds](../runs/bi-v150/20261029T175900061663Z-native-k8-sme-a-4096-four-rounds.md)（登记#518）：A臂main899 NativeK8 SME官方4K四轮均完成，原始吞吐5579.18/6400.98/6970.94/6967.59 tok/s；按官方弃首轮口径暖均6779.84 tok/s。所选A库已加载，目标64×2路由被观察到；私有3_6调优DB由207f1bd…变为1bf06dd…，KV **是否保留：** 保留A臂官方4K筛选记录；B臂对照仍在运行，当前不判断收益、准确率或基线资格。
- [20261029T175900061663Z-native-k8-sme-b-4096-four-rounds](../runs/bi-v150/20261029T175900061663Z-native-k8-sme-b-4096-four-rounds.md)（登记#519）：B臂main899 NativeK8 SME官方4K四轮均完成，原始吞吐5653.86/6470.63/7003.28/6915.42 tok/s；按官方弃首轮口径暖均6796.443333 tok/s。相对A臂6779.836667 tok/s观察为+0.244941987%；但最后两轮均值较A低 **是否保留：** A/B暖均仅观察到+0.244941987%，末两轮均值反向；末态私有DB已分叉且KV页差6，不能作严格内核因果结论。保留筛选观察，不宣布稳定收益或更新基线。

## CPU

- [20261029T153121891538Z-native-k8-sme-layout-compile](../runs/cpu/20261029T153121891538Z-native-k8-sme-layout-compile.md)（登记#510）：BI-V150 CoreX compile-only通过 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261029T154519134404Z-native-k8-sme-lookahead-compile](../runs/cpu/20261029T154519134404Z-native-k8-sme-lookahead-compile.md)（登记#512）：两臂standalone compile-only通过 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261029T155955570211Z-native-k8-sme-pair-build](../runs/cpu/20261029T155955570211Z-native-k8-sme-pair-build.md)（登记#513）：隔离A/B SO构建成功；符号、动态依赖和20参数ABI核对通过。无GPU执行。 **是否保留：** 保留为组件入口构建身份；不把compile结果写成数值或性能结论。
- [20261029T164536162881Z-native-k8-sme-dispatcher-build](../runs/cpu/20261029T164536162881Z-native-k8-sme-dispatcher-build.md)（登记#515）：A/B dispatcher SO均编译成功 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
