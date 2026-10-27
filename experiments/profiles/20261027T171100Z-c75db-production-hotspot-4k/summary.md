# BI-V150 graph event diagnostics

Analysis integrity: **PASS**. Complete valid 4K/16K pair: **False**. Diagnostic only; no official throughput claim.

All node durations below include instrumentation. The full/boundary delta is a fixed-order diagnostic comparison.

| Input | Graph | Samples | Boundary median ms | Full median ms | Paired added timing median % | DAG kernels ordered |
|---:|---|---:|---:|---:|---:|---|
| 4096 | worker-95174-window-1.json:98d4b412d8ac | 4 | 26.725334 | 29.222067 | 9.342634 | True |

## Input 4096, graph worker-95174-window-1.json:98d4b412d8ac: top driver names

Ranked by median per-sample **sum of instrumented intervals**, not native wall time.

| Rank | Driver kernel name | Timed calls | Median interval µs | Median sample interval sum ms |
|---:|---|---:|---:|---:|
| 1 | `_Z31corex_native_gqa_producer_draftILj2EEvPK13__ix_bfloat16S2_S2_PKiS4_fllllllllPfS5_S5_` | 168 | 426.463 | 17.900485 |
| 2 | `mm_kernel` | 536 | 37.046 | 6.114815 |
| 3 | `_ZN18Gemm_tcu_mr_kernel10gemm_tcu_hILj64ELj256ELj64ELj16ELj64ELj2EL13ixblasTrans_t1ELS1_1EL23ixblasTCUGEMMCategory_t0ELN5ixmma15MMEdgeCheckModeE0EL20ixblasGEMMBoundary_t2EL18ixblasLtEpilogue_t1ELb0EiL27ixblasLtMatmulMatrixScale_t1002ELS7_1002ELS7_1002ELb0ELb0ELj4ELj4ELb0EiiiaaEEvPT22_PT23_PKT24_PKT25_iiiiiiiiT21_SI_llllll21ixblasGEMMBatchMode_tiPvSK_SK_j` | 136 | 53.102 | 1.805267 |
| 4 | `_reduce_partials` | 168 | 10.246 | 0.430467 |
| 5 | `_ZN12_GLOBAL__N_113silu_epilogueEPKiPKfS3_P13__ix_bfloat16i` | 136 | 9.581 | 0.326138 |
| 6 | `triton_red_fused_fused_add_rms_norm_1` | 136 | 8.765 | 0.298096 |
| 7 | `triton_poi_fused_2` | 136 | 7.863 | 0.267540 |
| 8 | `reshape_and_cache_kernel_flash` | 168 | 5.888 | 0.247352 |
| 9 | `triton_red_fused_fused_add_rms_norm_gate_silu_auto_0` | 136 | 7.050 | 0.240762 |
| 10 | `_ZN12_GLOBAL__N_120quantize_cached_rowsILi256EEEvPK13__ix_bfloat16PaPfi` | 136 | 6.062 | 0.205860 |
| 11 | `triton_red_fused_fused_add_rms_norm_2` | 32 | 8.819 | 0.069621 |
| 12 | `triton_poi_fused_mul_silu_slice_1` | 32 | 7.588 | 0.061208 |
| 13 | `triton_red_fused_fused_add_rms_norm_0` | 32 | 7.092 | 0.056865 |
| 14 | `triton_poi_fused_3` | 28 | 7.865 | 0.055092 |
| 15 | `triton_red_fused__to_copy_embedding_rms_norm_0` | 4 | 10.788 | 0.010788 |
| 16 | `triton_poi_fused_1` | 4 | 7.671 | 0.007671 |

## Warnings

- Partial run: missing mapped workload lengths [16384]

## Interpretation limits

- Node intervals include inserted timing nodes/dependencies; they are not native kernel latency.
- Full minus boundary and ratios are paired fixed-order instrumentation diagnostics, not unbiased overhead.
- Boundary also contains timing events; there is no uninstrumented graph GPU total in these JSON files.
- Interval sums and event-window unions must not be reported as native GPU wall time.
- DAG comparability describes allowed concurrency; event-window overlap does not prove kernel concurrency.
- Selected diagnostic steps repeat computation and synchronize; throughput is not a score.
- Scheduler metadata is factual. Cached/new membership never classifies decode/prefill.
- Sample GPU offsets are graph-relative; scheduler monotonic_ns is not an absolute GPU timeline anchor.
- Function handles are process-local and only matched within their own worker window.
- Call estimates count graph nodes times scheduled replay counts, excluding extra diagnostic replays.
- Rankings are per graph, not workload-wide hotspots; sampled shapes/steps exclude eager work and unsampled graphs.
