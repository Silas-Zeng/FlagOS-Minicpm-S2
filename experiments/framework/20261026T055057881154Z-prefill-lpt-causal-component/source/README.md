# Prefill stride 常量特化组件

当前 normalized＋Q-hoist 基线保持不变，候选仅把11项运行时stride改为constexpr，并用局部 `tl.full((), value, tl.int64)` 保留原64位寻址。固定BM128/T64/w8s1、页序、mask、QK/PV、softmax、BF16 P及所有浮点表达式，不叠加log2、affine、next-K、cg或队友大tile。

依据：PR43整轮16K prefill为209.497/555.887秒，实际152608原prefill ASM有SGPR104/spill30，K/V stride用于循环内页地址、output stride一直活跃到末尾。特化可能消除动态整数乘法和长期保存的参数；不能先认定spill全由stride造成。旧GQA五stride组件虽无收益，其基准SGPR spill0与本处不同，不复用其性能结论。付出是每个合法布局新增编译变体，不承诺冷轮或整模收益。

复用log2组件受测输入与原current基准：真实M2047/KV16384、16Q/2KV/D128/page16、8192页表及writer，普通BF16 causal 2D。两臂实际Q-hoist产物、直接JIT、Graph哈希必须一致。原全输出finite/guard、FP64七行四头固定5e-4/.01、自臂同址换输入Graph逐位、writer/输入/RNG及完整2D单ABBA（每窗16次）保留。

新增一次同进程合法stride切换：仅增加query/output的token间隔、K/V的page间隔、页表行间隔共5项，逻辑值不变；另6项为原eligible固定的slot/head几何，完整记录11项常量值，不为测试放宽范围。新JIT须实际Q-hoist并换hash，核同值输出/间隙、alternate Graph，再finally恢复原kwargs、原JIT及原Graph。固定单序列的seq_idx=0，因此页表行stride仅覆盖特化身份，未数值覆盖非零行偏移。此验证不计入ABBA；原官方布局及服务参数不变。

ASM整数乘法、SGPR/VGPR及各自spill分别回收作诊断；不能把metadata n_spills=0当全部spill为零，也不因某计数不降硬拒有益实测。正确性或Q-hoist错误即停；性能负则收口，不扫布局/warps。owner、526/native14f、DB、锁与清理原样复用。增量审阅看kernel.diff、worker.diff、alternate_stride.py、owner.diff。当前只有CPU准备，无GPU或收益资格。

```bash
python3 /workspace/experiments/minicpm-s2/scripts/prefill-stride-constexpr-20261026/entry.py \
  --source-dir <已部署的原main526源码> \
  --native-library <原native14f动态库>
```

只由主线程统一调卡，不改变生产或官方参数。
