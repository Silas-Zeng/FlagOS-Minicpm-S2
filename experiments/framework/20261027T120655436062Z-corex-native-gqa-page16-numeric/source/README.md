# CoreX 原生单 page16 数值门

先前 b104 在未声明的 device `__exp2f` 处CPU编译失败，原件保留。v2只用实际SDK数学声明；11:40:38实际编译通过，原 `compile-check.json` 仍为false（唯一 `original_exp2_2` 前端名字不同）。`backend-equivalence.json` 固定原641478与v2的ASM/LLVM SHA：两者同 `float_mode=12`、无修饰 `ml_exp_f32`、无局部模式切换；其余原编译门全过。此补证仅允许该已核差异，不覆盖原false、不称设备数值已过。CU SHA `8545adc9…6cce` 不再变。

数值门先比SME共享全BF16位型，再比原GQA producer的partial/max/sum全FP32位型及独立FP64。另以与原核相同 `tl.exp2` 原语输出FP32 P与BF16 P逐位；underflow输入须在实际GPU score上覆盖normal、subnormal、低于最小subnormal范围，不能靠sum舍入或BF16/PV掩盖差异。任何差异立即停，不改容差。包括换值、零Q、Graph poison后同址换值、side stream；没有性能计时。

```bash
python3 entry.py --compile-dir /workspace/experiments/minicpm-s2/cpu-probes/20261027T114038Z-corex-native-page16
```

root按实际编译输出目录传 `--compile-dir`。owner默认使用仍冻结的main56源码 `/workspace/experiments/minicpm-s2/code/main56f1838-pr66-20261027`（807原文件/native14f），它只用于旧GQA单页数学控制；PR84未改该核，但不得将本门称为当前完整模型资格。原owner设备/9031预检、锁、DB恢复、自有进程与源码清理复用，finally AST未变。

数值extension显式同原CPU编译的目标/宏/标准/O3；build后、构造输入前保存一次实际 `ninja -t commands` 并硬核flags/no-fast-math。torch附带兼容flags保留；此处不猜其等价，设备逐位门仍必须通过。

范围仅page16/D128/每KV头8Q、两个64lane CTA、8KiB单shared slab、原8次QK/8次PV。不包含历史loop、tail/empty、多段reducer、生产接线、官方吞吐或模型准确率。raw共享诊断和中间输出均不用于任何性能主张。SDK专有头只在本地tmp，不随包发布。唯一GPU/SSH由root统一安排。
