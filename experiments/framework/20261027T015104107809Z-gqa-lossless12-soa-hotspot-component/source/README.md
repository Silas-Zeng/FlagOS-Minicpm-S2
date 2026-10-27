# 无损12bit page内SoA：唯一N64/S2完整组件

基线是本次main241/765文件实际backend选中的原GQA source2596，原tile16/while/FP顺序/split和reducer不变。直接A编译hash必须等于本次真实production hash，旧641478只记历史来源。长度多重集复用旧084521 N64/S2，不冒称新main完整profile。

实际采样SHA `f4821117…`：一条原Math500题256prompt tokens、42层各128tokens，K/V共5.25MiB；不是16K激活轨迹。本组件按实际16token页重复到容量、Q随机，用来测真实codec分布，不能推成模型吞吐/精度。CPU逐位逆变换覆盖全部真实21504行及混排65536种BF16位型，尚未GPU。

每physical page仍16KiB，4个K/V×KVhead group各4096B。每组SM区16×128B、低指数nibble区16×64B、高nibble区16×64B；另每row mode/base2B，128B/page metadata。span≤15用16码delta/base，span大时低/高nibble无损保存完整指数；没有逐元素escape/prefix/popcount，也不改变mantissa、特殊位型或数学。compressed的高区保持原字节且不读取；raw按mode额外读高区。CPU实样K raw197/10752、V78/10752，128B粒度地址模型分别省23.3259%/23.8560%，不是实测HBM事务。未找到足以证定本站32/64/128B sector的厂商合同，SME64B和每lane指令宽度不代替该证据。

新producer仅替换K/V载入；V位复原移到softmax后PV前，避免新整数宽活跃集跨QK，但实际compiler调度未证，全部计入候选成本。编码、低字节/指数拆分、metadata、tail load及布局转换可能抵消少读；不靠资源数字预报收益。真实LLVM/ASM和资源留原件，不硬开SME、不改compiler。

整池encode仅初始化及8门输入切换时刷新，不进任何每decode计时call。原8类FP64/特殊值/换QKV页表Graph/side-stream/输入RNG/guard保留，有限输出新增跨臂逐位硬门；GPU另做65536位型独立cache roundtrip，不用NaN Attention冒充codec逐位证明。新writer的compressed→raw→compressed换值Graph含同址slots改邻行/-1，CPU原始K/V+旧页overlay算预期；packed及metadata整个allocation逐字节相同、原writer cache同CPU预期后才计算FP64，故参考不由错误writer自证。所有未知/数值错误即停，不放宽门。

最终ABBA只测同流完整Graph：A原writer+原producer+原reducer，B新writer+新producer+同原reducer；缓存分配/整池初始化不计单步，所有新token编码/读取/softmax/输出计入。组件并存两池便于AB，不报生产容量收益；新metadata约原池0.78%也单独记录。任何完整负结果停止，不扫tile、不进模型；正向也须后续prefill/短多query/SAVE-RESTORE等全部消费者和模型准确率/官方资格，不能把编码字节落到旧BF16 reader。

原owner的source/native/9031/GPU/DB/自有进程清理finally保持，root独审后统一排卡：

```bash
python3 entry.py --source-dir <冻结main241完整765源码> --native-library <已核native14f.so> --shape hotspot
```
