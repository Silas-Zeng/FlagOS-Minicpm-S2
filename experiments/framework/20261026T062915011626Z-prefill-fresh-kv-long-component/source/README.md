# Prefill 本轮新 KV 直接消费：独立组件准备

**状态：CPU 原型已准备，尚未 GPU 编译/数值/性能，未修改生产main或现有候选。** 唯一设备由root统一安排，本目录不会自动启动或接入队列。

## 改了什么

基线直接从 main6971 源包的 `biv150_prefill_normalized.py` 和原 installed Attention `54c495dc…` 生成，保留当前11项stride特化、原初始softmax质量0和Q-fragment。**没有LPT、tile扩大、affine、next-K、cg、log2或其它负方案。** `current.kernel.py` SHA为 `b6703eef…`；新增loader为 `candidate.kernel.py`，完整差分见 `kernel.diff`。

原writer仍完整写入本轮KV。原绝对T64循环、QK/PV、P转BF16、online softmax、输出位置原样保留。只有KV地址来源变化：逻辑位置`t<context_len`读取原cache；其余有效位置读取当前post-RoPE raw KV的 `cu[i]+t-context_len` 行。页表load只对有效历史lane发生；跨ctx的一个tile按lane选同dtype指针，然后K、V各load一次。新增两指针和六个stride，无大副本或跨请求共享状态。

这省的可能是分页地址依赖，不自动减少KV字节。2K新KV共2MiB，原cache内容也可能命中本卡16MiB L2；新增指针select/寄存器成本可能更高。局部正不等于整模正。

## CPU 已完成

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 analysis/prefill-fresh-kv-prototype-20261026/prepare.py
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 analysis/prefill-fresh-kv-prototype-20261026/check_cpu.py
```

两脚本只用标准库，不导入Torch/Triton。`cpu-check.json`记录99种ctx/q组合、180320有效lane、3424无效尾lane、81个跨ctx tile、70968个实际生成offset表达式样本和3个ragged序列。覆盖非64/非16对齐ctx、qstart非零、尾query以及raw token stride256/2560；从生成AST取整数表达式执行，不另写一套地址公式冒充候选。源码变换可准确逆回基线，浮点body未改。

BF16同值依据是实际writer `f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb` 非FP8分支把key_load/value_load原值存入cache，未乘scale或反量化；CPU核其SHA和实际分支文本。组件还会用原writer在真实设备逐位核所有M行。CPU证明不代替该GPU门。

## 唯一两场景组件

同一包提供 `--case causal`（Q2048/KV2048、ctx0）和 `--case long`（Q2047/KV16384、ctx14337）。每次一个受控worker，root按顺序运行两场景；不是扩矩阵。真实EngineArgs/Builder/Impl、packed NHD KV、8192页表、原writer和Q-hoist调用链均复用既有组件；没有加载模型权重。raw K/V使用共同的token-stride2560视图模拟投影切片，非候选独有的contiguous转换；这仍是合成激活，不冒称已捕获模型post-RoPE输入。

组件先保存实际ABI并要求两臂真实Q-hoist，原数值合同原样：每臂独立FP64抽样 `max_abs<=5e-4 && relative_l2<=.01`、finite、输出guard；因为load的BF16值与原K遍历/归约完全相同，另要求跨臂逐位。保留同址换Q/rawKV/历史cache/页表后的Graph与fresh eager逐位、输入KV/RNG不变。

新增一次仅机制验证：cache保持不变，仅改变raw V，baseline输出必须保持、candidate必须变化；然后恢复raw，输出必须逐位恢复。此时两来源暂时不同的结果**不用于性能或数值分数**。它防止未实际读raw却误称新路径生效。

换页时同步重建slot_mapping，尤其ctx0的本轮KV就在换页范围；否则会制造验证器自己的错值。完整2D Attention计时复用单ABBA、每窗16次，包含loader的全部GPU成本。计时已暖直接JIT，原writer/metadata共同成本不重复计差额；raw参数装配/未来生产wrapper开销未包含，不能当整模收益。

## root 后续运行入口（尚未部署或启动）

本包 `entry.py` 的原main618 owner只换run名；唯一设备锁、GPU/9031预检、native14f/618源身份、DB保存恢复、原进程组清理不变。`entry.tar.gz`与资产pins由 `seal.py` 产生，复现时以 `package-receipt.json` 为准。

```bash
python3 <root部署本组件的目录>/entry.py \
  --source-dir <原main6971/treeaa43的已部署618源码目录> \
  --native-library <原native14f动态库> --case causal

python3 <root部署本组件的目录>/entry.py \
  --source-dir <同一原main6971源码目录> \
  --native-library <同一原native14f动态库> --case long
```

新参数的dtype/stride、跨界mask与别名检查需独立窄审后才由root上卡。任一编译/数值/Q-hoist错误立即停，不修框架或放宽容差凑通过。组件无净益则结束此实现，不扫描tile/warps/阶段数；两个场景都正再决定真实C3/P多序列接线，不自动进入模型或105题。

本owner无SSH、GPU或后台任务。未完成事项：独立审阅、两场景GPU组件、可能的生产接线与官方验证；没有任何新的准确率或吞吐资格。
