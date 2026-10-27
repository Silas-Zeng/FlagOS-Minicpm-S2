<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# LM-head温度epilogue融合

完整head+Sampler组件省17.31% Event/12.24% wall；保留，待生产接入验证。

相关代码：[archive-receipt.json](../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json)；[result.json](../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json)；[candidate.py](../../experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T050730877973Z-lm-head-temperature-epilogue-component](../runs/bi-v150/20261027T050730877973Z-lm-head-temperature-epilogue-component.md)（登记#360）：R64真实LM-head权重130560×2048、合成hidden；保留原BF16舍入后融合FP32转换与温度除法，原stats/top-p/RNG不变。10组逐位/FP64/采样ID/RNG/换值Graph及输入不变检查通过。完整eager head+Sampler唯一ABBA含分配与提交，Ev **是否保留：** 保留局部正信号，待实际服务验证；不是官方收益。
