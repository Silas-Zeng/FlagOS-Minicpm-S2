<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# LM-head双行GEMV

随机BF16 M2/N130560/K2048组件：原FlagGems linear固定配置对比唯一BN32/BK256/w8 paired-GEMV，FP64参考、换值/指针、guard/RNG通过。Event0.834885→2.045513ms，明显负，停止。未加载框架模型/native，也未取得模型或官方资格，不扩调参、不建优化PR。

相关代码：[candidate.py](../../experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/source/candidate.py)；[installed-linear.py](../../experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/source/installed-linear.py)；[worker.py](../../experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/source/worker.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T130418879497Z-lm-head-paired-gemv-component](../runs/bi-v150/20261025T130418879497Z-lm-head-paired-gemv-component.md)（登记#268）：数值/变指针内容/guard/RNG通过；Event0.834885→2.045513ms、wall0.892245→2.076413ms，明显负。 **是否保留：** 停止唯一配置，不扩调参或接模型；保存负结果，不建优化PR。
