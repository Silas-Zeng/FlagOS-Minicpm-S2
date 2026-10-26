# 长prefill完整历史热循环组件

仅CPU准备，尚待独立审阅与主线统一上卡。基线是main6971原stride＋Q-hoist，无LPT；候选保持原绝对K tile/FP32顺序，完整历史热loop无mask，尾部至多两次原tile。M2047/KV16384、ctx14337及末ragged块都在首shape中。无效query行不写输出，各行独立；不改变有效行数学。

复用原prefill owner/618源码/native14f/DB保存恢复与清理。命令仅供主线设备空闲后执行：

```bash
python entry.py --case long --source-dir <冻结main6971/treeaa43完整源码> --native-library <原native14f.so>
```

新核私有Q-hoist只允许同一Q allocation、同布局的1至3处只读fragment load共享；真实IR形状不符、SSA/LLVM循环内Q读取机制门失败即停止，不修改生产守卫。A沿原Manager，B仅复制Manager._compile函数globals中的transform_ir，不污染原模块。实际原Q-hoist守卫与参考门不放宽。

初始/换值完整跨臂逐位、原FP64硬门、writer、同址变Q/K/V/page表Graph、有限性/输出guard/输入/RNG原样保留。资源仅诊断：不下降则不能宣称降SGPR/spill机制成立，但数值通过后仍做唯一ABBA完整2D输出，以免寄存器档位未变漏掉指令成本收益。无益或错误就停，不扫tile，不自动补官方。仅正向后再补分界边界资格。Graph用于正确性，原ABBA为直接已暖JIT，不能混称Graph计时。

CPU范围、源码差分、私有IR改动见prototype.py、kernel.diff、worker.diff、cpu-results.json。没有生产/模型资格，不能继承main103/105。独立审阅结果由root另行保存。

## v2只复用真实IR已有的外层Q fragment

v1首次编译因保守IR顺序门拒绝，未计时，没有数值/性能结论。实际normal TTGIR在268行分配Q，294行已有tail共用fragment，296行进入hot loop，338行重复读同一Q allocation。v2仅对精确已核TTGIR SHA `4f544f3d...` 将338行替换为同布局identity convert复用294行定义；其它指令不动，原唯一allocation/readonly/类型/layout门先执行，外层定义支配loop及两tail。原生产守卫不改，A不改；新LLVM零循环Q读取门仍必须通过。

本目录为单独v2包，未改原17f受测包或原件。candidate.kernel.py、current.kernel.py、worker.py字节与v1相同，完整数值/FP64/Graph/ABBA和资源仅诊断策略不变。CPU只新增实际IR一指令差分/逐字逆回及4类反例，未重复4096几何。审阅prototype.diff、actual-ir.diff、real-ir-cpu-check.json。
