<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Attention热key复用

复用绑定后的key/cache并保留原launch尾；未命中、实际命中及负结果都保留。

相关代码：[biv150_attention_key_recipe_v2.py](../../patches/framework/candidates/biv150_attention_key_recipe_v2.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T085923Z-attention-key-recipe-gate](../runs/bi-v150/20261022T085923Z-attention-key-recipe-gate.md)（登记#121）：失败源码和原件保留 **是否保留：** 未集成；失败或无收益记录保留。
- [20261022T100149Z-attention-key-recipe-diagnostic](../runs/bi-v150/20261022T100149Z-attention-key-recipe-diagnostic.md)（登记#122）：独立诊断仍exit1、未计时 **是否保留：** 未集成；失败或无收益记录保留。
- [20261022T104349Z-attention-key-recipe-v2-gate](../runs/bi-v150/20261022T104349Z-attention-key-recipe-v2-gate.md)（登记#124）：wall增加0.1869%，event增加0.1134%，提交CPU也增加；仅局部门，未测整模型accuracy或官方吞吐 **是否保留：** 未集成；失败或无收益记录保留。
- [20261022T105536Z-small-input-hot-key-v2-gate](../runs/bi-v150/20261022T105536Z-small-input-hot-key-v2-gate.md)（登记#128）：wall从0.464890547到0.502826703ms，增加8.1602%；原件保留，不报服务收益或整模型accuracy **是否保留：** 未集成；失败或无收益记录保留。
