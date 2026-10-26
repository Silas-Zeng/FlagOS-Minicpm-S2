<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill序列内CTA调序

在当前stride与Q-hoist上反转每个序列内的query块枚举，尝试减少causal最后一波拖尾；不改变单query的K遍历/softmax/输出地址。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T055057881154Z-prefill-lpt-causal-component](../runs/bi-v150/20261026T055057881154Z-prefill-lpt-causal-component.md)（登记#305）：Q2048/KV2048原臂与候选输出有限、guard正常，但都被旧long-only FP64 max_abs≤5e-4拒绝：两臂同max_abs0.00352174、relative_l20.00095805。保存输出CPU后核整份逐位一致/max_diff0；不据此认定候选新增数值错，未计时。 **是否保留：** 原臂/候选逐位一致；旧FP64拒绝不改判，后继逐位组件单列。
- [20261026T055124182279Z-prefill-lpt-long-component](../runs/bi-v150/20261026T055124182279Z-prefill-lpt-long-component.md)（登记#306）：当前stride/Q-hoist上仅反转序列内query块，Q2047/KV16384初始及换值跨臂逐位、独立FP64、writer/Graph/输入RNG均过。完整Attention Event 8.168149→8.460097ms，慢3.57%，wall同向。长上下文无净益，不推进该范围；短c **是否保留：** 长上下文不进模型；短causal单独完成有界验证。
