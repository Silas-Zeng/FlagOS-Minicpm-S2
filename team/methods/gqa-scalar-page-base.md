<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA标量KV页基址与动态for组合

scalar＋while慢0.38635%且SME未生效；for＋scalar＋一维i64 stages1实际SME8却慢10.73864%；stages2实际async-copy4/SME16仍慢27.63241%。三项原8门/逐位通过，均停止不接模型，机制生成不等于净收益。

相关代码：[kernel.diff](../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/source/kernel.diff)；[results.json](../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/results.json)；[archive-receipt.json](../../experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/archive-receipt.json)；[gqa-scalar-page-base-114133.json](../../analysis/main6971-084521-nodes/gqa-scalar-page-base-114133.json)；[kernel.diff](../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/source/kernel.diff)；[results.json](../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/results.json)；[archive-receipt.json](../../experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/archive-receipt.json)；[gqa-for-scalar-i64-134937.json](../../analysis/main6971-084521-nodes/gqa-for-scalar-i64-134937.json)；[kernel.diff](../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/source/kernel.diff)；[results.json](../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/results.json)；[archive-receipt.json](../../experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/archive-receipt.json)；[gqa-for-scalar-i64-s2-141615.json](../../analysis/main6971-084521-nodes/gqa-for-scalar-i64-s2-141615.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T114133003627Z-gqa-scalar-page-base-hotspot-component](../runs/bi-v150/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component.md)（登记#333）：8类门及跨臂逐位通过；Event0.542196542→0.544291317ms，慢0.38635%，停止。SGPR spill75为lane保存非HBM；实际SME仍0，for＋scalar未验证。 **是否保留：** 停止当前scalar-page-base实现，不进模型或合并；保留正确性通过及小幅负结果，不把一次ABBA写稳定因果。for＋scalar尚未实现验证，不自动列为已获益组合。
- [20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component](../runs/bi-v150/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component.md)（登记#335）：8门/逐位通过；实际SME LLVM8/ASM8，完整Graph慢10.73864%，停止。资源下降不是收益证明，无官方/105。 **是否保留：** 停止本组合及模型扩展；保留真实SME已生成、数值通过与净性能负证据，不以指令成功或资源下降继续盲扫。
- [20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component](../runs/bi-v150/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component.md)（登记#336）：8门/逐位通过；实际stages2、async-copy4/SME16，完整Graph慢27.63241%，停止不扫stage。 **是否保留：** 停止当前SME流水路线并保留数值通过、机制生成与净负结果；不以异步指令数或低寄存器替代收益。
