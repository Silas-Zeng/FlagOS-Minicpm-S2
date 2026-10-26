# GQA page-only下一页号预取：N64/S2单组件

纯CPU准备，未GPU资格。baseline为原main6971 page16 while，候选保持相同4D KV指针、tile16、while、FP运算/尾页、split与原reducer。只在首个完整页前加载i32页号，在每次循环提前读下一完整页的i32编号；不保留第二份K/V、不带已负dynamic-for/span，不改生产。

原641478 ASM每tile有page load→vmcnt(0)→v2s→页基址→KV load串联；这里尝试把下一页编号的等待移入当前KV/compute区间，是否实际重叠须看新LLVM/ASM的load/wait，源码早写不代表有效。页表仅约0.05%字节，不按该比例算收益。实际原组件.541ms、必要KV约274.7MB；本站665GB/s纯读参考不能当GQA硬上限或收益承诺。

与原N64/S2观测长度多重集、合成Q/KV，原8类FP64/特殊值/Graph/side-stream/输入/RNG门保留；新增CPU只核预取页序及最后/仅tail/空段不额外读表。每次Graph仍读取原seq_lens/page表，页号不是host缓存。记录跨臂bitwise诊断但不修改原FP64合同；任何原门失败停，不放宽容差。

owner仅run名变化，设备/9031/DB/source/native/cleanup原样。主线独审后统一GPU执行：

```bash
python entry.py --shape hotspot --source-dir <冻结main6971完整618/treeaa43源码> --native-library <原native14f.so>
```

计时完整producer＋原reducer，同一GPU输入的Graph ABBA，不只测producer。源码/编译资源/ASM load-wait均保存；寄存器档位只诊断，不省略秒级ABBA。若实际prefetch被wait压回原依赖则不宣称重叠；完整净负就停，不扩矩阵或模型。当前没有准确率/官方资格。
