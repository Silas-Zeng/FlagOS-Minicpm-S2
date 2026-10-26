# GQA动态for＋2D span：实际N64/S2单组件

仅CPU准备，未GPU编译/数值/性能合格。复用已测SME-span组件的owner、同址view、原8类FP64/特殊值/Graph/side-stream门及原生产reducer，固定main6971/618、native14f。没有修改生产。

新增实现只把原page16 while转换为动态for range(lower,full_upper,16)，移除手动position+=16；每个query/K顺序、online softmax、BF16 P舍入、原尾页分支、ROWS8/w1/s1/S2均不变。逆AST与旧span核完全相同；CPU核全页序列、空段、非整页尾部覆盖。没有增加下一KV片段或扩大tile。

依据：当前真实Graph42个GQA节点采样区间和中位23.970ms，真实grid64/2/2、shared8192、hash641478e6…；原IR为scf.while/useSme0。固定021f对应编译源码getOperandUseSme分别处理For和非For，后者的backward-slice包含间接页编号等地址依赖，具体拒绝guard或遍历顺序尚未定位；标量load并非必然失败。这是待实际编译证伪的机制，不把对应源码当本站C++binary构建证明，也不将mask变化当SME生效。

timing-shape.json使用本次Graph replay32的64个computed+scheduled长度多重集（4K负载），合成Q/KV、非真实激活，也未证明物理row次序。为原边界门仍分配16K cache，实际初始/恢复计时长度为该多重集。必须自然捕获生产grid64/2/2和原ABI，不路由现成替代核。组件计时完整producer+原reducer ABBA，view创建在Graph前且不计入replay；生产接线仍需核主机成本。

root统一实查GPU/9031后，将entry.tar.gz解至独立scripts/gqa-for-span-component-20261026：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/gqa-for-span-component-20261026/entry.py --source-dir /workspace/experiments/minicpm-s2/code/20261026T013104Z-main34942f7-prefill-stride-official --native-library <已核14f原生库.so> --shape hotspot
```

不自动扩矩阵或官方测；核实际TTGIR for/copy/wait、ASM资源/spill，不能只看前端mask62。若未选SME，真实for计时仍可说明该结构本身的净成本，但不能称SME优化。任何原数值门失败立即停，不改容差或框架凑过。性能负则保留证据停止；正向才由root决定下一步。
