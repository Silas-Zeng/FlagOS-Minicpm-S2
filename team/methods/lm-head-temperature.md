<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# LM-head温度epilogue融合

组件完整head+Sampler Event省17.31%；生产同main56/native14f/DB/KV原官方4K本组暖均5921.12对5902.77 tok/s，观察+0.3109%。保留小收益信号，尚待16K/105，不把局部组件收益迁移为模型结论。

相关代码：[archive-receipt.json](../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)；[comparison.json](../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json)；[archive-receipt.json](../../experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T050730877973Z-lm-head-temperature-epilogue-component](../runs/bi-v150/20261027T050730877973Z-lm-head-temperature-epilogue-component.md)（登记#360）：R64真实LM-head权重130560×2048、合成hidden；保留原BF16舍入后融合FP32转换与温度除法，原stats/top-p/RNG不变。10组逐位/FP64/采样ID/RNG/换值Graph及输入不变检查通过。完整eager head+Sampler唯一ABBA含分配与提交，Ev **是否保留：** 保留局部正信号，待实际服务验证；不是官方收益。
- [20261027T055059Z-main56-lm-head-temperature-4k-four-rounds](../runs/bi-v150/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds.md)（登记#362）：head温度epilogue原官方4K暖均5921.12对A5902.77 tok/s，本组+0.3109%；同KV/native/DB，1024请求及实际启用/清理通过。保留小信号，待16K/105。 **是否保留：** 保留单组4K小收益，待16K和105；非稳定净收益结论。
