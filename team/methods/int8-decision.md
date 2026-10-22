<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# int8 与 W8A8 决策测量

真实形状上的 int8 GEMM、W8A16、_int_mm+融合 epilogue 及 QDQ 精度模拟；负结果与候选并存，不混用证据级别。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T121921Z-int8-shape-decision](../runs/bi-v150/20261022T121921Z-int8-shape-decision.md)（登记#127）：int8 linear 候选在模型真实形状上的 A/B（seed=1234，权重预量化，激活量化单独计时） **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T125552Z-intmm-fused-epilogue-cost-model](../runs/bi-v150/20261022T125552Z-intmm-fused-epilogue-cost-model.md)（登记#128）：三 kernel 成本模型（自写 Triton per-token 对称量化、torch._int_mm、自写融合 dequant+bias）在合并服务形状上的分相实测 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261022T115949Z-w8a8-quantdequant-risk](../runs/bi-v150/20261022T115949Z-w8a8-quantdequant-risk.md)（登记#129）：teacher-forcing PPL（同脚本 --sweep scheme，105 篇 Level-3、22528 token）对 per-channel 与分组 32/64/128、含或不含激活量化都落在 bf16 的 ±0.15% 内，无法作为筛选指标 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T122551Z-w8a8-mitigation-arms](../runs/bi-v150/20261022T122551Z-w8a8-mitigation-arms.md)（登记#130）：缓解臂同协议（24 题、1024 token、greedy、bf16 参考臂在本 run 内）：去掉 down_proj（252 层）与只量化 MLP（126 层）都是 gold 13/24、最终答案一致率 0.95833、各 1 题翻转，与“只量化权重”同级 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T124239Z-w8a16-column-read-gemm](../runs/bi-v150/20261022T124239Z-w8a16-column-read-gemm.md)（登记#136）：W8A16 自写 Triton kernel 的第一版：权重按 [N,K] 存放，tile 以列方向读取（不合并） **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T125433Z-w8a16-coalesced-gemm](../runs/bi-v150/20261022T125433Z-w8a16-coalesced-gemm.md)（登记#137）：输出端 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
