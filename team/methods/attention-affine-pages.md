<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Attention连续页段寻址

保持原KV分配与数学，对现存连续物理页段用仿射寻址。组件四布局逐位通过、局部耗时下降约5.0–6.9%；原四语义及三个串行prefill页表绑定通过，仅P恒等/C3prefix0。完整官方两档各四轮1536成功，弃首轮4K5741.68/16K4050.10 tok/s，相对main526观察−0.30%/+0.12%；KV546432对547536，不确认净收益、不定基线、不追加105。

相关代码：[biv150_attention_affine_pages.py](../../experiments/framework/20261025T074041Z-attention-affine-pages-model-verify-control/plugin-source/vllm_fl/patches/biv150_attention_affine_pages.py)；[prototype.py](../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/prototype.py)；[worker.py](../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/worker.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T071453655585Z-attention-affine-pages-component](../runs/bi-v150/20261025T071453655585Z-attention-affine-pages-component.md)（登记#250）：event耗时下降6.95%/6.93%，4K下降4.99%/5.50% **是否保留：** 保留候选；真实服务页段覆盖、P索引接入及模型准确率待验，组件收益不代替官方吞吐。
- [20261025T074041Z-attention-affine-pages-model-verify](../runs/bi-v150/20261025T074041Z-attention-affine-pages-model-verify.md)（登记#252）：连续页寻址527/tree41449b98，仅worker安装入口+新helper **是否保留：** 保留进入原官方吞吐；完整105与混合/P实际覆盖尚待，不声称已恢复旧mixed2资格。
- [20261025T075732Z-main0bf9-affine-affine-official-four-rounds](../runs/bi-v150/20261025T075732Z-main0bf9-affine-affine-official-four-rounds.md)（登记#253）：官方两档各4轮、1536成功；弃首轮5741.68/4050.10 tok/s，观察−0.30%/+0.12%。KV失配，不确认净收益。 **是否保留：** 保留完整结果及局部正信号；未确认净收益，不定新基线、不追加105。
