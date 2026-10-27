# 原生同步 GQA：完整 producer＋原 reducer 组件

固定本次N64/S2、真实长度全部4096，最大cache容量16384只用于ragged/尾页边界；不是官方16K（其常见N32/S4），不是官方成绩或模型资格。A来自实际backend自然捕获的原GQA＋原reducer，直接重放kernel hash须与本次生产捕获相同；B为新原生C++同步SME/page16 producer，归约仍逐字原实现。原writer只在setup一次，两臂不改writer；计时不包含writer，不称writer全链。

单页v3的布局、FP32/BF16 P/underflow/Graph/stream资格复用；本轮仍硬核完整历史、tail/empty与归约。沿用原8case/独立FP64/Graph换值/输入只读/RNG/同流ABBA；新增所有有限partial/max/sum跨臂逐位，以及未用tail K/V槽注入NaN后仍保持原masked语义。任何错误停止，容差不变。只有全部正确性过后才唯一完整Graph ABBA（A/B/B/A，每窗16call），每次包含完整producer＋同一个原reducer；不扫形状或wait variant。

源CU SHA `8aa05659…bf7f`，与12:31:55实际CPU编译输入逐字一致，`COREX_NATIVE_GQA_V_OVERLAP=0`。实际CPU probe为8KiB/private0/SGPR62/VGPR76/spill0，32MMA/16SME/4wait/8exp/4sumFMA含full/tail静态重复；这些字段明确标 `candidate_cpu_probe`，不是反汇编实际Torch extension。extension另存实际ninja命令与.so SHA，显式同目标/宏/标准/O3及variant0，附带Torch兼容flag如实保留；数值/计时以执行臂为准，不为资源口径重编阻塞设备。

```bash
python3 entry.py --compile-dir /workspace/experiments/minicpm-s2/cpu-probes/20261027T123155Z-corex-native-gqa-loop
```

原owner的设备/9031预检、锁、DB恢复、源码/native检查与自有进程清理复用单页v3，finally AST未变。默认冻结main56/807源码仅作不变GQA控制，PR84没有改该核；不把旧模型或head资格迁移。`worker.py.diff`仅呈本轮相对旧producer＋reducer组件的接线差分。没有生产补丁、后继队列或GPU启动。

Segments保模板能力，当前bridge/launcher只启N64/S2；N32/S4须后续独立组件。8KiB wait移动只留同源可选编译设计，当前显式0，不继承收益或数值资格。
