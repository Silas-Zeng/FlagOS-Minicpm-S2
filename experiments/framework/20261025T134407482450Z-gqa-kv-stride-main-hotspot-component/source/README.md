# 原生产 GQA 的固定 KV stride 特化

当前只准备独立组件，不改生产、不自动排队。`.cg` 在官方4K首暖轮相对历史对照下降约14%，主线程已停止该候选；此前共同cg的组件包 `../gqa-kv-stride-constexpr-20261025/entry.tar.gz` 保留，不继续作为后继。新双臂共同基线是原生产 `2596cc09`，没有 `.cg`，只评价stride特化。

- **改了什么**：五个K/V stride参数改 `tl.constexpr`，用五个 `tl.full((), stride, tl.int64)` 局部常量保持原64位寻址；page、页序、mask、浮点数学、split、归约完全不变。不改KV格式，不做int32地址窄化。
- **为什么测**：已有16K Graph GQA约44ms/步；实际机器码逐页保留动态stride的64位乘法及高半部补算。packed NHD stride固定 `(8192,256,128,1)`，特化可望使编译器改用移位/合并地址。成本是每种真实stride增加JIT变体，净收益待测。
- **源码依据与去重**：原FlagGems v5.3.5 `ops/flash_kernel.py:384,846` 已使用 `k_page_stride: tl.constexpr`，但长varlen `:1328` 仍为动态参数；不笼统套用全部路径。此次改的是自有GQA实现。最新PR49保留这五个动态stride；PR38、46/47调度或大tile路线不重复，head-major与paired-GEMV负结果不恢复。
- **怎么测**：复用原Builder/Impl/writer捕获真实ABI、526/native14f组件入口。默认N33/bucket40/S16，全producer＋reducer原CUDA Graph ABBA；不扫描参数，不与cg收益相加。先保存ASM并核原ca策略、按源行归属的页乘法不再出现且总整数乘法至少少4条，否则不计时。行号证据不能代替完整数据依赖追踪，原机器码须保留供窄读。
- **正确性**：复用原8组逐位、输入/RNG、变化输入Graph边界；新增同进程相同KV数值的合法stride `(16384,512,256,1)`，检查全五项实际变化、新JIT身份、间隙/输入不变，再回原kwargs/原JIT身份及原Graph。不对非官方布局计时。错误即停，不继承模型105题资格。

原owner独占GPU/9031、420秒边界、DB/源码/native及所属进程清理不变，仅run名变化。旧24项CPU审据复用；本次只核新原生产接线、cache策略与源身份，见 `main-wiring-check.json`。GPU未运行、无性能结论，待另一智能体窄审后由root唯一排期。

```bash
python entry.py --source-dir /workspace/experiments/minicpm-s2/code/<原冻结526目录> --native-library <已核native14f的绝对路径> --shape hotspot
```

`asset-pins.json` 与三个 `.diff` 是执行/审阅入口。新组件的main来源不借用cg官方失败成绩，也不重复计算局部收益。
