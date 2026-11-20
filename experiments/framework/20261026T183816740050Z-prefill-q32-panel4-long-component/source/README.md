# main241 Q32＋panel4：单个完整组件

新主线2412207已合并PR47，实际single Q>=1024默认BM256/Q32/T64/w16s1。旧Q16 panel4的2.22%与边界资格均不继承。本包只Q2047/KV16384/ctx14337，保持新Q32 tile/warp/FP规则，复用原a8的source transform、producer源码、reducer原字节；唯一B差异仍为4个绝对K panel及完整FP32部分归约。不把Q32切回Q16制造收益。

真实A来自原backend→Q32 Policy→q32._MANAGER.wrapper的实际选中参数，临时观察该wrapper并恢复；不能从generic BM128外参数推定Q32。硬核BM256/Q32/w16、grid64×2、实际优化hash与Policy未禁用。B新private Manager显式BM256/w16，仍要求实际Q-hoist proof；不改编译器或放宽资格。编译/数值失败即停，不救过。

workspace仍68124160B（64.968MiB），每次B完整producer＋reducer计入唯一暖JIT ABBA；Graph单独保持同地址换值与scratch poison、eager逐位回放资格。初始/换值独立FP64 max_abs5e-4 / relL2 .01与新增全输出allclose(5e-4,.01)保留，跨臂bitwise仅诊断。输入/RNG/输出哨兵和DB/source/native/owner清理复用。

Q32已将Qblock数量减半，panel新增约130MiB读写的相对成本可能更高；新单组件负即停，不扫panel/形状，不自动生产或官方后继。源为765文件、tree4e068333，native固定本站14f；不混用队友5cbb成绩。

root唯一排卡，入口：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/prefill-q32-panel4-component-20261027/entry.py --source-dir /workspace/experiments/minicpm-s2/code/<已核main241目录> --native-library <已核native14f.so> --case long
```

CPU仅证明实际Policy传参、新捕获恢复、scalar覆盖、源码/门复用，未证明GPU编译/数值/性能。单seq host maxK继承问题不影响本包：合成metadata真实KV固定16384，不作生产scope或覆盖率结论。
