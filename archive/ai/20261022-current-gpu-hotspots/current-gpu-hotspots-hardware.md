# 当前组合 GPU 热点与下一单点

以天数 BI-V150 的干净 `6f918ae6` 组合为基点；新诊断只追加 profile footer，没有启用 C3views、pure gather 或 hot-key。真实 16K/32req/128out 原参数服务在 114435 抓到三个连续 `[N2,M2048,P2047]`、scheduled `[1,2047]` 步，第四 execute 入口停止，因此包含前三步完整 sampler。原件：`experiments/framework/20261022T114435Z-current-mixed-native-diagnostic/`，`native-hotspots.json` SHA `220e2576ea4e82317a693cd1d51c14e3b10d27fe146c96cba64c083fcdfa44e5`，trace SHA `54e62f23f2c814b7e076a1bb9732a37b093f9d343fab7adbe2c42a2e9e56d3dd`。

| 可见 GPU 路径 | 次数 | 累计 ms | kernel 累计占比 |
|---|---:|---:|---:|
| 2D Attention | 126 | 640.380398 | 60.2339% |
| GEMM mm_kernel | 504 | 337.191759 | 31.7161% |
| 3D Attention | 126 | 28.589193 | 2.6891% |
| KV writer | 126 | 3.929684 | 0.3696% |
| Attention reducer | 126 | 1.323940 | 0.1245% |

1656 kernel 总计 1063.156218ms；这是被抓窗口的累计 kernel 时间，不能当端到端占比或 GPU 利用率。2D 实际 grid(128,2,1)/block(512,1,1)、regs102/srfs104、dynamicSharedMemory65536。旧 b0 prefill 的 92.96% 是不同早期源；042609 decode 多数在图壳，壳外 LM-head/sampler 排名不能迁移为当前总热点。当前可见 sampler 分类仅 0.0426%，不优先温度 identity。

下一唯一门见 `tmp/next-prefill-w16/README.md`：历史 a4 未测 BM128/T64/w16/s1，只将当前 2D w8→16，原 C2/3D/reducer 不动。D1/P2047/KV16K 是上界 fixture，非精确 seq_len 回放；先真实层数值/整 KV/RNG/流/指针门，过后仅 32 ABBA，失败亦保留，不做 sweep 或服务预接线。1024 线程/CTA 可能资源不足或更慢，资源实际编译结果优先于纸面寄存器均摊推导。


实际后继120226已完成：w16 严格正确性通过，但32ABBA wall慢31.7087%、Event慢31.9930%，实际regs101/spills0/shared65536/warp64。只少1个记录寄存器没有形成性能收益，不从纸面线程均摊推导occupancy；停止w16/tile扫描。纯decode CPU gather独立服务亦−0.7983%，不集成。下一只保末层全M行KV写入后按原logits_indices裁死Q/Attention及尾MLP的设计，原6f最终取行 :4445/:4451是可观察死行接点；不能直接把取行前移到模型入口，也不能删前41层或最后层任何KV。收益上界受一层/42限制，未知feature严格原路，先CPU核模型实际调用链，当前没有实现或新设备计划。
