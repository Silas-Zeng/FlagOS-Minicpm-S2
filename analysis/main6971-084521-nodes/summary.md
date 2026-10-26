# BI-V150 Graph节点诊断

解析完整性：**通过**。完整有效的4K/16K成对诊断：**否**。仅用于定位，不构成官方吞吐成绩。

以下所有节点区间均包含插桩影响。full/boundary差值来自固定顺序的配对诊断，不能当作无偏开销估计。

| 输入长度 | Graph | 样本数 | boundary中位ms | full中位ms | 配对新增计时中位% | DAG核全有序 |
|---:|---|---:|---:|---:|---:|---|
| 4096 | worker-361793-window-1.json:886e76b260d1 | 4 | 34.603107 | 37.140869 | 7.229367 | True |

## 输入4096：Graph worker-361793-window-1.json:886e76b260d1的主要驱动核

按每个样本的**插桩区间之和的中位数**排序；该数值不是原生墙钟耗时或正常负载占比。

| 排序 | 驱动核名称 | 计时调用数 | 单区间中位µs | 每样本区间和中位ms |
|---:|---|---:|---:|---:|
| 1 | `_gqa_decode_attention` | 168 | 570.750 | 23.970038 |
| 2 | `linear_kernel` | 536 | 44.815 | 7.960562 |
| 3 | `_ZN18Gemm_tcu_mr_kernel10gemm_tcu_hILj64ELj256ELj64ELj16ELj64ELj2EL13ixblasTrans_t1ELS1_1EL23ixblasTCUGEMMCategory_t0ELN5ixmma15MMEdgeCheckModeE0EL20ixblasGEMMBoundary_t2EL18ixblasLtEpilogue_t1ELb0EiL27ixblasLtMatmulMatrixScale_t1002ELS7_1002ELS7_1002ELb0ELb0ELj4ELj4ELb0EiiiaaEEvPT22_PT23_PKT24_PKT25_iiiiiiiiT21_SI_llllll21ixblasGEMMBatchMode_tiPvSK_SK_j` | 136 | 52.556 | 1.790910 |
| 4 | `_reduce_partials` | 168 | 10.477 | 0.439975 |
| 5 | `_ZN12_GLOBAL__N_113silu_epilogueEPKiPKfS3_P13__ix_bfloat16i` | 136 | 9.581 | 0.325987 |
| 6 | `triton_red_fused_fused_add_rms_norm_linear_1` | 136 | 8.892 | 0.302713 |
| 7 | `triton_poi_fused_2` | 136 | 7.819 | 0.265687 |
| 8 | `reshape_and_cache_kernel_flash` | 168 | 5.873 | 0.246765 |
| 9 | `triton_red_fused_fused_add_rms_norm_gate_silu_auto_0` | 136 | 7.031 | 0.239910 |
| 10 | `_ZN12_GLOBAL__N_120quantize_cached_rowsILi256EEEvPK13__ix_bfloat16PaPfi` | 136 | 6.150 | 0.209312 |
| 11 | `triton_red_fused_fused_add_rms_norm_linear_2` | 28 | 8.829 | 0.061865 |
| 12 | `triton_poi_fused_linear_mul_silu_slice_1` | 32 | 7.608 | 0.060948 |
| 13 | `triton_red_fused_fused_add_rms_norm_linear_0` | 32 | 7.050 | 0.056583 |
| 14 | `triton_poi_fused_3` | 28 | 7.831 | 0.054892 |
| 15 | `triton_red_fused__to_copy_embedding_linear_rms_norm_0` | 4 | 10.875 | 0.010875 |
| 16 | `triton_red_fused_fused_add_rms_norm_2` | 4 | 7.885 | 0.007885 |
| 17 | `triton_poi_fused_1` | 4 | 7.660 | 0.007660 |

## 范围提醒

- 仅本次4K诊断，缺少16384输入对应的样本，不补称完整双负载。

## 解读边界

- 节点区间包含新增计时节点及依赖，不是原生核延迟。
- full减boundary及其比例是固定顺序插桩诊断，不是无偏开销。
- boundary自身也有计时事件；本JSON没有未插桩Graph总GPU时间。
- 区间和、事件窗口并集均不得改称正常GPU墙钟。
- DAG描述允许的并行关系，事件窗口重叠本身不能证明核并发。本图497核、496边为串行链。
- 选中的诊断步会重复计算并同步，吞吐不能用于计分。
- 调度元数据为事实；cached/new身份不能直接分类为decode/prefill。
- 样本GPU偏移相对Graph；调度monotonic_ns不是绝对GPU时间轴锚点。
- function handle只在本进程、本worker窗口内匹配。
- 调用估算为图节点数乘调度replay次数，不含额外诊断重放。
- 排名仅代表这个被采样的Graph，不是全负载占比；不含eager与未采样图。

## 入口与下一项

[原工具英文产物](summary.original.md)、[结构化解析](analysis.json)、[区间CSV](kernel-intervals.csv)、[排序CSV](kernel-rankings.csv)保留原测量数值。原始JSON位于项目根archive/hotspot-layout-20261026/batch-091200/profiles/20261026T084521Z-main6971-production-hotspot-4k/observations/。

优先研究42个GQA节点：真实grid64/2/2、block64、shared8192，活跃hash641478e6…；[真实编译原件](../../archive/hotspot-layout-20261026/main6971-real-gqa-ir/)已回收。此处没有缺失GQA热点；posthoc的diagnostic_incomplete仅指日志未链接本run新FX，不能抹掉已通过的Graph与prefill证据，也不能用旧FX补成新证明。

后继[动态for＋2D span组件](../../tmp/gqa-for-span-component-20261026/README.md)已实测负75.05%停止，未进模型；实际for成立而SME未启用。[字节预算与资源](gqa-byte-budget.json)记录原核逻辑KV有效率507.603GB/s，尚不能认定HBM饱和。

实际linear分项已绑定本图编译缓存：[分项JSON](linear-breakdown.json)。down42节点3.645377ms、QKV42节点1.868252ms、O42节点1.614013ms、BF16 edge gate8节点0.826906ms；均为插桩区间和。单项连续流读参考665.432GB/s已并入[字节预算](gqa-byte-budget.json)，它比GQA必要KV有效率507.603GB/s高，不能据两者比例宣称HBM利用率或可实现收益。
