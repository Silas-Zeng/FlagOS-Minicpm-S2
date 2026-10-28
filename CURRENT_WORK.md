# 当前实验与接续

当前有效BI-V150基线为[框架PR105](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/105)，merge `1cbac531ca9afaa0e9a68624d5d10cb1d0412055`。已完成原官方4K／16K各四轮与原105；源码实际启用原S2/S4 V等待重叠，不含mixed扩范围负候选。

| 结果 | 已有证据及限制 |
|---|---|
| 4K暖均6627.816667 | 1024成功，同KV548336／DB；对PR92单组观察+2.261763% |
| 16K暖均4832.66 | 512成功，同KV548288／DB；对PR92单组观察+0.128735% |
| 原105为103/105 | 95%门通过，零请求错误／截断／空；GQA两个shape启动capture有效，非逐题覆盖；通用stack缺compute_order marker的pending与旧105相同 |
| Q32 GPU metadata接线 | 091802实编通过；094028 pure2048的14硬门通过但Event慢9.30069%，wall省8.92290%；原FP64诊断两臂false且误差一致。按冻结Event筛选停止，mixed未测，无生产资格 |
| Q64两个Q32 cohort共享KV | CPU64KiB／83SGPR／107VGPR／0spill；长输入位型/FP64/Graph/side与Q33八门通过，完整Event6.880203ms；对原Q32慢4.862870%、对旧双槽慢7.479299%，停止，无模型/官方资格 |
| 原生GQA下一页16KiB双槽 | CPU S2/S4均59SGPR／82VGPR／0spill；QK/softmax后、PV前提前g2scnt0；未达冻结完整重叠窗口，停止、不进入GPU；不是数值错误或实测性能负 |

总411条／408个唯一run。最新100025／101658／102147三轮134原件已保存，未为发布重测。Q64性能负、GQA双槽机制门否决，均已停止；当前PR105基线及原准确率／覆盖限制不变。Q32长组件小收益不外推模型。

沿[实验总表](team/experiments.md)、[原生GQA](team/methods/corex-native-gqa-page16.md)、[Q32](team/methods/native-q32-transfer.md)查阅短记与原始证据。设备排期由主线统一安排。
