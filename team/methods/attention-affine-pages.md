<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Attention连续页段寻址

保持原KV分配与数学，仅对已存在连续物理页段用仿射寻址。真实组件四布局逐位通过，16K耗时下降约6.9%、4K约5.0–5.5%；保留为候选，真实服务覆盖和官方吞吐尚待。

相关代码：[prototype.py](../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/prototype.py)；[worker.py](../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/worker.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T071453655585Z-attention-affine-pages-component](../runs/bi-v150/20261025T071453655585Z-attention-affine-pages-component.md)（登记#250）：event耗时下降6.95%/6.93%，4K下降4.99%/5.50% **是否保留：** 保留候选；真实服务页段覆盖、P索引接入及模型准确率待验，组件收益不代替官方吞吐。
