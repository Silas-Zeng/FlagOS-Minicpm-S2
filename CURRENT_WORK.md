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
| Q32真实长metadata | Q2047/KV16384完整forward Event省2.609776%，20门与两组原FP64通过，仅长组件资格 |
| Q64 direct AND与真实长metadata | 标量组件对原省4.772124%／对双槽省2.421318%；真实metadata两B快于较快A，均值省7.015632%但A2漂移，只保留正信号，尚无生产或模型资格 |
| 16K上下文诊断首次启动 | source-manifest整文件SHA绑定失败，服务/GPU启动前停止；13原件保留，无官方成绩 |

总417条／414个唯一run。最新103515／104549／104855／105914／111346及ef8f5d62六轮316原件已保存。Q64 direct AND与长metadata保留组件正信号，A2漂移不作稳定收益；启动前manifest失败无GPU成绩。当前PR105正式基线及原准确率／覆盖限制不变。

沿[实验总表](team/experiments.md)、[原生GQA](team/methods/corex-native-gqa-page16.md)、[Q32](team/methods/native-q32-transfer.md)查阅短记与原始证据。设备排期由主线统一安排。
