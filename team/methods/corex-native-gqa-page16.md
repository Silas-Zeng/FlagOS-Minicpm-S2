<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# CoreX原生GQA单page16数值诊断

v3仅修CPU coverage两行，CU8545与原数学未变。122022实际7组全位型/独立FP64、Graph poison、side stream、underflow三范围均通过；只取得单page16数值资格，没有计时/历史loop/tail/empty/reducer/模型资格。120655旧failed_stop与coverage false仍保留，事后CPU覆盖补证不冒充未执行门。113301编译失败和114038前端exp名字门/机器码补证限制见链接。

相关代码：[comparison.json](../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/result.json)；[result.json](../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/result.json)；[recompute.py](../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/recompute.py)；[llvm-build.log](../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/related-cpu/113301/llvm-build.log)；[compile-check.json](../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/compile-proof/compile-check.json)；[backend-equivalence.json](../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/source/backend-equivalence.json)；[archive-receipt.json](../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/archive-receipt.json)；[comparison.json](../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/result.json)；[independent-review.md](../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/independent-review.md)；[archive-receipt.json](../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T120655436062Z-corex-native-gqa-page16-numeric](../runs/bi-v150/20261027T120655436062Z-corex-native-gqa-page16-numeric.md)（登记#372）：4组已执行数值均逐位；第四覆盖检查false停止，Graph/side未到。 **是否保留：** 保存原failed_stop，CPU事后仅补输入覆盖解释；不接生产、不报性能。
- [20261027T122022380438Z-corex-native-gqa-page16-numeric](../runs/bi-v150/20261027T122022380438Z-corex-native-gqa-page16-numeric.md)（登记#373）：v3七组全位型/FP64/Graph poison/side与coverage通过，无计时。 **是否保留：** 保留单页数值资格；不授历史loop/性能或模型资格。
