<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 专用 GQA decode attention kernel

为 MiniCPM5-2B 的 16Q/2KV、head128、单 token decode 重写的 attention kernel 与其段归约；只在该守卫命中时生效，其余路径走原 kernel。

相关代码：[biv150_gqa_decode.py](../../patches/framework/biv150_gqa_decode.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T093453Z-gqa-decode-official-4k](../runs/bi-v150/20261022T093453Z-gqa-decode-official-4k.md)（登记#121）：相对官方基线 1878.47 为 +156.0%，相对队友官方 3683.65 为 +30.6% **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T095640Z-gqa-decode-official-16k](../runs/bi-v150/20261022T095640Z-gqa-decode-official-16k.md)（登记#122）：同一构建的 16K 官方四轮：原始 3349.87 / 3364.23 / 3364.10 / 3363.77，协议平均 total 3364.03 tok/s，mean TTFT 155385.04 ms，mean TPOT 133.37 ms，后三轮极差 0.0137% **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T170900Z-gqa-decode-level3](../runs/bi-v150/20261022T170900Z-gqa-decode-level3.md)（登记#123）：evalscope math_500 Level 3 全 105 题、temperature 1.0、top_p 0.95、max_tokens 32768、model-graded：0.9714（102/105），门槛 0.95，余 2.1 分 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T191500Z-team-main-warm-probe-control](../runs/bi-v150/20261022T191500Z-team-main-warm-probe-control.md)（登记#124）：KV 相差 96 tokens（521840 对 521936，0.018%） **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T191500Z-team-main-warm-probe-control](../runs/bi-v150/20261022T191500Z-team-main-warm-probe-control.md)（登记#131）：KV 相差 96 tokens（521840 对 521936，0.018%） **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T193500Z-team-main-warm-probe-gqa](../runs/bi-v150/20261022T193500Z-team-main-warm-probe-gqa.md)（登记#125）：相对 #124 得 +33.6%（4K）与 +24.9%（16K），两臂均用“丢第一轮取中位”同一口径，比值由 CSV 原始行直接相除 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T193500Z-team-main-warm-probe-gqa](../runs/bi-v150/20261022T193500Z-team-main-warm-probe-gqa.md)（登记#132）：相对 #124 得 +33.6%（4K）与 +24.9%（16K），两臂均用“丢第一轮取中位”同一口径，比值由 CSV 原始行直接相除 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T125654Z-gqa-off-official-16k-two-rounds](../runs/bi-v150/20261022T125654Z-gqa-off-official-16k-two-rounds.md)（登记#126）：官方仪表（benchmark_throughput_serve.py 未改动，test-cases=[[16384,1024,64,128]]）在合并基上跑 kernel 关闭的对照臂 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T152000Z-gqa-kernel-rows](../runs/bi-v150/20261022T152000Z-gqa-kernel-rows.md)（登记#133）：kernel 级 A/B，同一份 seed 固定操作数，参考为通用 kernel 钉住 w1s1 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T133309Z-gqa-on-official-16k-two-rounds-default](../runs/bi-v150/20261022T133309Z-gqa-on-official-16k-two-rounds-default.md)（登记#134）：对 #126 控制臂同口径稳态 2734.40 为 +23.3% **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T140539Z-probe-gqa-gate-overclose](../runs/bi-v150/20261022T140539Z-probe-gqa-gate-overclose.md)（登记#135）：失败原因 **是否保留：** 未集成；失败或无收益记录保留。
