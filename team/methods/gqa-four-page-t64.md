<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA四页T64计算块

将page16按四页组成T64计算块，减少循环与地址开销。N33/B40/S16、KV16K三轮8类数值/Graph/FP64抽样通过，跨臂不要求逐位。原T64 Event慢126.9037%、固定w4仍慢64.7108%且mma仍[4,1]；最后真实N4布局实现[1,4]，Event1.278378→1.827178ms仍慢42.9294%，wall慢42.5630%。N4的SGPR99/spill68、VGPR88/shared32K，实际occupancy未证明。机制落地仍明显负，整个四页T64路线收口，不再扫参、不进4K或模型；原件保留，不授官方/105资格。

相关代码：[ttgir.txt](../../experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component/ir-candidate/ttgir.txt)；[results.json](../../experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component/results.json)；[kernel.diff](../../experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component/source/kernel.diff)；[ttgir.txt](../../experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component/ir-candidate/ttgir.txt)；[kernel.diff](../../experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/source/kernel.diff)；[worker.py](../../experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/source/worker.py)；[fp_reference.py](../../experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/source/fp_reference.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T151303364296Z-gqa-four-page-t64-hotspot-component](../runs/bi-v150/20261025T151303364296Z-gqa-four-page-t64-hotspot-component.md)（登记#276）：8类数值/Graph/FP64抽样门通过；Event1.276535→2.896506ms，慢126.9037%；SGPR spill0→138、shared8K→32K。 **是否保留：** 明确负结果收口，不测4K/模型、不扫参；保留原件及资源代价，不授模型或官方资格。
- [20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component](../runs/bi-v150/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component.md)（登记#278）：8类数值/Graph/FP64门通过；Event1.278072→2.105123ms慢64.7108%，wall慢64.3265%；SGPR spill92/shared32K。 **是否保留：** 明确负，不进入4K或模型；原IR供CPU布局分析，不授官方/105资格。
- [20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component](../runs/bi-v150/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component.md)（登记#279）：8类数值/Graph/FP64门通过，实际mma=[1,4]；Event1.278378→1.827178ms慢42.9294%，wall慢42.5630%。 **是否保留：** 整个四页T64路线收口，不再扫参、不进入4K或模型，不授官方/105资格。
