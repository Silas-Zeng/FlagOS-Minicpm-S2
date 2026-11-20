<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA两页T32计算块

保持物理page16、原split和reducer；固定T32/w1/s1检验减少online-softmax迭代能否抵消寄存器/布局成本。旧T64失败不改写，本方法实际结果以每轮短记为准。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T055026341574Z-gqa-two-page-t32-hotspot-component](../runs/bi-v150/20261026T055026341574Z-gqa-two-page-t32-hotspot-component.md)（登记#304）：page16/split/reducer不变，计算tile T32/w1/s1；8类数值、FP64抽样、换值Graph/输入/RNG均过。完整producer+reducer Event 1.279242→1.829472ms，慢43.01%；SGPR spill0→84、VGPR93→136、sh **是否保留：** 不扩形状、不进模型；寄存器spill反证保留。
