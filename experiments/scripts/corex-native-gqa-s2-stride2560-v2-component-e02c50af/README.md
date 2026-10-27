# 真实Q stride2560的独立S2增量

原6f975完整组件已正确且正向，但Q连续2048不能直接继承到真实生产QKV切片。此包不改CU、FP、原始Q数值、flags或门，只把Q放到20heads backing的前16heads，额外4heads为保护区；bridge严格只接受(2560,128,1)。输入变化通过同一原生产ABI捕获和全部原门，唯一N64/S2/KV4096完整producer＋原reducer ABBA。三个新增diff与CPU地址证明见stride2560-*；原6f975包保持。

# 原生同步 GQA：完整 producer＋原 reducer 组件

固定本次N64/S2、真实长度全部4096，最大cache容量16384只用于ragged/尾页边界；不是官方16K（其常见N32/S4），不是官方成绩或模型资格。A来自实际backend自然捕获的原GQA＋原reducer，直接重放kernel hash须与本次生产捕获相同；B为新原生C++同步SME/page16 producer，归约仍逐字原实现。原writer只在setup一次，两臂不改writer；计时不包含writer，不称writer全链。

单页v3的布局、FP32/BF16 P/underflow/Graph/stream资格复用；本轮仍硬核完整历史、tail/empty与归约。沿用原8case/独立FP64/Graph换值/输入只读/RNG/同流ABBA；新增所有有限partial/max/sum跨臂逐位，以及未用tail K/V槽注入NaN后仍保持原masked语义。任何错误停止，容差不变。只有全部正确性过后才唯一完整Graph ABBA（A/B/B/A，每窗16call），每次包含完整producer＋同一个原reducer；不扫形状或wait variant。

源CU SHA `8aa05659…bf7f`，与12:31:55实际CPU编译输入逐字一致，`COREX_NATIVE_GQA_V_OVERLAP=0`。实际CPU probe为8KiB/private0/SGPR62/VGPR76/spill0，32MMA/16SME/4wait/8exp/4sumFMA含full/tail静态重复；这些字段明确标 `candidate_cpu_probe`，不是反汇编实际Torch extension。extension另存实际ninja命令与.so SHA，显式同目标/宏/标准/O3及variant0，附带Torch兼容flag如实保留；数值/计时以执行臂为准，不为资源口径重编阻塞设备。

```bash
python3 entry.py --compile-dir /workspace/experiments/minicpm-s2/cpu-probes/20261027T123155Z-corex-native-gqa-loop
```

原owner的设备/9031预检、锁、DB恢复、源码/native检查与自有进程清理复用单页v3，finally AST未变。默认冻结main56/807源码仅作不变GQA控制，PR84没有改该核；不把旧模型或head资格迁移。`worker.py.diff`仅呈本轮相对旧producer＋reducer组件的接线差分。没有生产补丁、后继队列或GPU启动。

Segments保模板能力，当前bridge/launcher只启N64/S2；N32/S4须后续独立组件。8KiB wait移动只留同源可选编译设计，当前显式0，不继承收益或数值资格。

## v2 仅修输入夹具

独立诊断132510未调用GQA：实际FlagGems zero_在Qstride2560上忽略stride，B32/B64误改额外512分别12800/26112元素，准确匹配CPU预测。原失败包保留，不称native数值错误。v2仅用CPU构造(B,16,128) BF16全+0，再GPU copy_写回同一query view；原kernel/bridge/原9门/容差/Graph/ABBA未改，不修生产FlagGems。

每案Attention前保存整份backing的CPU位型并检查原guard，失败即保存证据且不调用Attention；原执行后guard保持。成功案.pt另存完整backing前后位型。neg_保持原样，不扩展零符号研究，不继承本v2的运行资格。
