# Mixed 暖态性能分析

保留窗494.888s，GPU union489.748s（98.96%）；非Graph Q32 attention累计201.460s，约占窗口40.7%。实际Mixed调度样例Q2018/context12108/KV14126已回收，但不等同逐调用pointer ABI。profile/collector/analyzer成功；旧posthoc解析不完整，不是模型报错。这些时间是诊断结果，不是官方成绩或可直接省去的成本。

- [20261029T220702833593Z-mixed-a-16k-profile](../runs/bi-v150/20261029T220702833593Z-mixed-a-16k-profile.md)：benchmark前旧S2/S4激活门误拒绝K-only encoded路线；profile未完成，无性能样本；不是模型/算子正确性失败。
- [20261029T222344850512Z-mixed-a-16k-profile](../runs/bi-v150/20261029T222344850512Z-mixed-a-16k-profile.md)：同参非profile预热后完成128请求暖态诊断；Q32非Graph GPU事件201.460s。profile/collector/analyzer成功，旧posthoc不完整；非官方成绩、不更新基线。
