# Prefill log2 域组件

当前 normalized＋Q-hoist 为基准，仅将 `score_scale` 预乘 `LOG2E`，运行最大值同处 log2 域，`P` 与 `alpha` 直接 `exp2`。页表寻址、页序、BM128/T64/w8/s1、QK/PV、BF16 概率转换和归约代码保持。仅适用原 MiniCPM5-2B BF16 普通 causal 2D、无 sinks/ALiBi/softcap/量化等的既有 `_eligible` 范围；不注册模型或生产框架。

依据：PR43 整轮16K同窗 prefill 为209.497/555.887秒，不能据此宣称可省38%。现成旧组件原生产 LLIR 与 ASM 均存在每个概率元素 `(S-M)*LOG2E` 后再 exp2；候选把换底并入原 score scale，减少重复乘法，不减少 KV 字节或 QK/PV FLOP。[Triton 官方 fused-attention](https://triton-lang.org/main/getting-started/tutorials/06-fused-attention.html)亦采用同域最大值与 exp2；这里只借机制，不搬其硬件配置。浮点舍入改变，不能称跨臂逐位或模型精度不变。

复用已受测 head-major 组件的 M2047/KV16384、16Q/2KV/D128/page16、8192页表、真实 Builder/Impl/writer；页0..7倒序。两臂都走当前生产 Q-hoist 私有编译链，实际选中哈希须存在；预热后直接调用同一 JIT，Graph 捕获核哈希必须一致，避免 wrapper 捕获时保守回退原核。没有 affine、next-K、.cg 或队友大 tile 改动。

数值门沿相同输入的原合同：全输出finite/guard，NumPy FP64 causal参考七行×四头，固定 `max_abs≤5e-4` 且 `relative_l2≤0.01`；分别保存两臂误差。原同地址换Q/K/V、历史cache、页0/2后，Graph对本臂fresh eager逐位，原writer写槽、输入/RNG不变检查保留。抽样参考只给此组件资格，不能替代真实模型和官方准确率。

完整2D producer单ABBA，每window16次，计入全部输出；两臂共同的writer/metadata不计差额。ASM换底乘法计数、寄存器/shared/spill只作诊断，不因小机器码变化硬拒；无净正则收口，不扫tile/warp。原owner、526源码/native14f、唯一设备锁、9031检查、DB恢复和420秒收尾复用。

由主线程独占设备运行：

```sh
python3 /workspace/experiments/minicpm-s2/scripts/prefill-log2-20261025/entry.py \
  --source-dir <已冻结并部署的原 main526 目录> \
  --native-library <原 native14f 动态库>
```

新增 CPU 源码逆回/AST/接线验证见 `cpu-results.json`，`kernel.diff`/`worker.diff`/`owner.diff` 是增量审阅入口。当前未GPU、无收益或模型资格。原官方参数、生产源码与原件均未修改。
