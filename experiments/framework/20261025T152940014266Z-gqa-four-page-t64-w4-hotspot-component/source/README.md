# BF16 GQA 四页 tile64：固定四 warp 后继

仅在已受测四页 tile64 组件上，将候选 launch `num_warps=1` 改为 `4`；原生产 T16 基线仍为 1 warp，candidate 内核、page16、S16、输入、FP64/Graph/guard/RNG 与完整 producer＋reducer ABBA 均原样复用。只测 N33/bucket40/KV16K；不扩 T32/w2/w8 或其他形状。

旧一 warp run `20261025T151303364296Z` 数值通过，但 Event 1.276535→2.896506 ms，SGPR spill 0→138、VGPR 93→199、shared 8→32 KiB。旧失败原件保留。真实 TTGIR 显示扩大四倍的 K/V 与 P 片段仍由 `warpsPerCTA=[1,1]` 持有；另有同后端小 M 矩阵沿 N 分 warp 的实际产物，因此本次只检验固定四 warp 的片段分摊。不能预称 spill 消失或性能恢复；QK 与 PV 的 N 维不同，P 重排、softmax 跨 warp 归约以及 CTA 资源成本可能抵消收益。

运行后读取已有 `ir-candidate/ttgir.txt` 核实际 MMA/blocked 的 warpsPerCTA，并与 `results.json` 的寄存器、spill、shared 和 ABBA 联合判断；不把元数据单独当性能因果。编译/数值异常立即停止，无净益则收口，不扫参数。组件正向也不授予模型或官方准确率资格。

由 root 唯一调卡：`python3 entry.py --source-dir <原冻结main526目录> --native-library <原14f库>`。旧 source/native/owner/DB/清理审据复用。新增 CPU 只核两个差分精确逆回、candidate 与 FP64 源字节相同及 Python AST；`cpu-check.json` 是原一 warp 的 9 项地址接线检查回执，未伪称本轮重跑。
