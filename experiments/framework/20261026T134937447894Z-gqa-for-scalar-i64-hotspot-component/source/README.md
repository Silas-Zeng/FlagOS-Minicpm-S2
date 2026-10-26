# GQA for＋标量页基址＋一维i64后expand

CPU候选，尚未GPU。只固定实际N64/S2、page16/ROWS8/w1s1，原每query K顺序与全部浮点表达式、原reducer保持。仍是原NHD缓存及合法同storage span，无新KV副本、无HND、无tile扫描、不改编译器或useSme bit。

三项缺一未证可用：旧for+span非uniform page-offset被资格拒绝，慢75.05%；scalar-base+while实际K/V dot useSme16/32但最终copy0，慢0.386%、SGPR104/spill75。固定021f的getSmeStride只接受For/Func直接子load，并只识别ExpandDims直接乘scalar stride。当前Extsi位于Expand之后会阻断；新先在1D转i64，再Expand。HEAD_SIZE必须并入scalar slot stride后才乘rank2 tensor，使恢复值为256元素而非row单位2。新for与scalar base共同处理前两guard；源码推演不是本站C++binary或SME传输生效证明。

原8门/原FP64/ABI/完整producer＋原reducer Graph ABBA、换Q/KV/page、side/RNG/DB与清理复用；有限值新增跨臂输出bitwise硬门，非有限保留原分类语义门及bit诊断。CPU逆函数AST精确回受测scalar-base while，16384地址验证新整数重组；旧span尾界/长度/for页序证明复用。不拿更低资源替代数值或计时。

root待当前官方完成、实查GPU/9031后，解包到独立scripts/gqa-for-scalar-i64-component-20261026：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/gqa-for-scalar-i64-component-20261026/entry.py --source-dir /workspace/experiments/minicpm-s2/code/20261026T013104Z-main34942f7-prefill-stride-official --native-library <已核14f原生库.so> --shape hotspot
```

只一组，不自动队列。实际TTIR/TTGIR必须核scalar/Splat、direct ExpandDims×真实stride256、For层级及K/V dot资格；LLVM/ASM核真正SME copy/load、wait、资源与SGPR spill。若编译器重组指针或stride不可恢复，记录拒绝事实不继续盲扫；数值/运行错立即停，性能负保留后停止。无新模型、官方或准确率资格。
