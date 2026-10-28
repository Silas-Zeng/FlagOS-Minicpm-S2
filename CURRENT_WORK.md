# 当前实验与接续

当前有效BI-V150基线为[框架PR105](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/105)，merge `1cbac531ca9afaa0e9a68624d5d10cb1d0412055`。已完成原官方4K／16K各四轮与原105；源码实际启用原S2/S4 V等待重叠，不含mixed扩范围负候选。

| 结果 | 已有证据及限制 |
|---|---|
| 4K暖均6627.816667 | 1024成功，同KV548336／DB；对PR92单组观察+2.261763% |
| 16K暖均4832.66 | 512成功，同KV548288／DB；对PR92单组观察+0.128735% |
| 原105为103/105 | 95%门通过，零请求错误／截断／空；GQA两个shape启动capture有效，非逐题覆盖；通用stack缺compute_order marker的pending与旧105相同 |
| Q32 GPU metadata接线 | 091802实编通过；094028 pure2048的14硬门通过但Event慢9.30069%，wall省8.92290%；原FP64诊断两臂false且误差一致。按冻结Event筛选停止，mixed未测，无生产资格 |

总408条／405个唯一run。最新三轮476原件和既有4K／16K证据已保存，未为上传或合并重复上卡。PR92历史基线和所有负结果保留；Q32长组件的小收益不外推到短causal或模型。

沿[实验总表](team/experiments.md)、[原生GQA](team/methods/corex-native-gqa-page16.md)、[Q32](team/methods/native-q32-transfer.md)查阅短记与原始证据。设备排期由主线统一安排。
