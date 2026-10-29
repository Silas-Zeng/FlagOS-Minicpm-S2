<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# NativeK8 SME K页布局与lookahead编译探针

本探针核实将完整16-slot K页经两条 `__ivcorex_sme_load_16x1b64_colxfb8` 搬运后，shared stage 的2048字节图像是否与原 `issue_k_i8` 路径一致。目标是确认SME搬运的布局行为，便于后续单独评估；它没有接入attention或生产代码。

CPU编译使用实际BI-V150 CoreX工具链，保存source、build命令、实际SO、IR和ASM；GPU试验固定4种输入模式（zero、−127、+127、固定seed随机）、page 0/3、head 0/1，共16案。CPU reference、A/B逐字节相等、输入不变及两侧输出guard共96项检查均通过。原件和身份字段见[编译run](../runs/cpu/20261029T153121891538Z-native-k8-sme-layout-compile.md)与[布局run](../runs/bi-v150/20261029T153349258627Z-native-k8-sme-layout.md)。

第三条CPU run记录lookahead候选与base两臂standalone compile-only成功。独审确认S2/S4中next-K SME发射在当前PV前，g2scnt wait在PV后且loop header再次等待；VGPR 85→70、SGPR 70→72、shared 8192B、scratch 0。只通过CPU编译/指令顺序门，不证明实际重叠、Attention数值或性能。详见[第三条CPU短记](../runs/cpu/20261029T154519134404Z-native-k8-sme-lookahead-compile.md)和[独立复核](../../../experiments/bundles/20261029T154519134404Z-native-k8-sme-lookahead-compile/source/assembly-review.json)。

结论仅适用于探测的完整页与字节搬运stage；不覆盖partial page、完整attention数学、模型数值/准确率、吞吐或生产资格。源码依据main `899ce77470b0b539aebc108fd122f668c2d5894d`；probe源码、lookahead两臂与复核文件列于本地payload。
