# 当前实验与接续

**2026-11-20 双平台复现说明及源码 ZIP 修复已交付。** [双平台 readme.md](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/main/docs/submission/readme.md) 汇总两卡环境、启动和官方评测。 [FlagGems #15](https://github.com/Silas-Zeng/FlagGems/pull/15) 与[复现说明 #6](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/pull/6) 已合入。最终 ZIP 在 BI-V150 普通安装及 editable 安装通过，固定生成与此前一致，聊天加法答对 5，服务已退出。运行源码与此前 101/105 官方准确率测试逐文件一致。沐曦沿用团队 103/105。 [设备原件](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/fc334a548d82d17242bb241b39ae387b57e35689/experiments/framework/20261120T091032Z-source-zip-install/status.json) · [独立复核](experiments/framework/20261120T091032Z-source-zip-install/packaging-review.md)。

**2026-11-20 天数 BI-V150 最终主干准确率。** 官方 MATH-500 Level 3 答对 101/105 题，准确率 96.19%，通过比赛 95% 门槛。105 题均完成评分，0 个请求错误。 框架 `6220924c` 和 FlagGems `bda4a2e0` 均从完整 Git 检出构建。[官方报告](experiments/accuracy/20261120T082740Z-final-main-accuracy/math_500.json) · [逐题核对](experiments/accuracy/20261120T082740Z-final-main-accuracy/verdict.json) · [首次归档安装的记录](team/runs/bi-v150/20261120T082459Z-final-main-accuracy.md)。

当前有效BI-V150基线为[框架PR105](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/105)，merge `1cbac531ca9afaa0e9a68624d5d10cb1d0412055`。已完成原官方4K／16K各四轮与原105；源码实际启用原S2/S4 V等待重叠，不含mixed扩范围负候选。

| 结果 | 已有证据及限制 |
|---|---|
| 4K暖均6627.816667 | 1024成功，同KV548336／DB；对PR92单组观察+2.261763% |
| 16K暖均4832.66 | 512成功，同KV548288／DB；对PR92单组观察+0.128735% |
| 原105为103/105 | 95%门通过，零请求错误／截断／空；GQA两个shape启动capture有效，非逐题覆盖；通用stack缺compute_order marker的pending与旧105相同 |
| Q32 GPU metadata接线 | 091802实编通过；094028 pure2048的14硬门通过但Event慢9.30069%，wall省8.92290%；原FP64诊断两臂false且误差一致。按冻结Event筛选停止，mixed未测，无生产资格 |
| Q64两个Q32 cohort共享KV | CPU64KiB／83SGPR／107VGPR／0spill；长输入位型/FP64/Graph/side与Q33八门通过，完整Event6.880203ms；对原Q32慢4.862870%、对旧双槽慢7.479299%，停止，无模型/官方资格 |
| 原生GQA下一页16KiB双槽 | 102147完整窗口门NO-GO保留；后按部分next-K新假设测114531，原九门通过，Event慢4.116242%，停止，不扩S4 |
| Q32真实长metadata | Q2047/KV16384完整forward Event省2.609776%，20门与两组原FP64通过，仅长组件资格 |
| Q64 direct AND与真实长metadata | 标量组件对原省4.772124%／对双槽省2.421318%；真实metadata两B快于较快A，均值省7.015632%但A2漂移，只保留组件正信号；生产实际启用后125913官方首暖未通过，未获模型准确率或完整官方资格 |
| 16K上下文诊断首次启动 | source-manifest整文件SHA绑定失败，服务/GPU启动前停止；13原件保留，无官方成绩 |
| GQA逻辑T32 | 两页共同softmax属新数学顺序，115612实际编译16KiB／80SGPR／80VGPR／0spill；120451原九数值门通过，Event慢3.752166%，停止 |
| Q64真实mixed边界 | 61 decode+1987 prefill、context7948，20门/FP64/位型通过；Event省2.380581%、wall慢0.367369%，仅旧c75/f720组件证据 |
| 16K覆盖诊断v2 | 128请求成功，worker导出缺失，RAM观察不可恢复；覆盖诊断失败，不作为官方成绩、不重跑整轮 |
| T32复用8KiB | 121814实际64SGPR／80VGPR／0spill；123106新生命周期原九门全过，Event省0.221958%、wall省0.287814%，不称稳定或官方收益；实际包bfff519b |
| Q64生产16K官方两轮 | 125913首冷4041.81／首暖4819.11，256成功；对4834.45观察−0.317306%，按规则停止。KV548432≠548288，不称严格因果/稳定退化；未满四轮/准确率，不合并 |
| 生产离线成品与T64 CPU | 124728 Q64 SOc157a26a；125302 T32 SO502e1570；132607 T64 16KiB／88SGPR／88VGPR／0spill，当次仅编译资格，后续T64组件见下行 |
| T32复用4K官方两轮 | 132807首冷5491.63／首暖6412.53，512成功；对6441.35观察−0.447422%，按门停止。KV548432≠548336，不称严格因果/稳定退化；未满四轮/16K/准确率，不合并 |
| T64四页复用组件 | 134552原九case、六双臂FP64、三非有限与Graph/尾/side通过；ABBA Event慢2.809061%、wall慢2.675528%，恢复正常，停止，不进模型 |
| premax vote CPU编译 | 134934当次仅8KiB／64SGPR／76VGPR／0spill，无GPU资格；后续组件见下行 |
| premax vote组件 | 141255共12case、有限output/partial硬逐位、FP64/Graph/边界通过；Event近持平慢0.001408%、wall省0.084431%，按Event门停止，不进生产/官方 |
| Q32 direct-Q v2及组合 | 150532 pure2048与153450 mixed/long组件Event正向，但mixed wall慢1.110675%，均非官方收益；155444组合CPU编译审阅只批准一次pure组件A/B，无数值/生产资格。160148官方4K完整1024请求，弃首均6537.81，对PR105 6627.816667观察−1.358014%；KV548432≠548336，不作严格因果，按完整负结果停止direct-Q，不跑16K/105、不改基线 |
| direct-Q＋grouped pure组合162319 | Event A/B .519592→.550852ms（慢6.0163%），wall省8.4983%但B两次波动较大；按Event负信号停止，raw顶层numerical_component_passed=false为earlyreturn未赋值，18硬门实际全过，不能称数值失败；98项原件及原包SHA已回收核验，终态审阅与登记完成。PR107 K8格式不兼容，不组合 |

总443条／440个唯一run。本批覆盖12个run原件（含此前已登记的141255），98项原件与终态审阅已核验；累计964个原manifest成员。160148完整4K四轮为负，162319组件按Event门停止；不跑16K/105、不改PR105基线。

沿[实验总表](team/experiments.md)、[原生GQA](team/methods/corex-native-gqa-page16.md)、[Q32](team/methods/native-q32-transfer.md)查阅短记与原始证据。设备排期由主线统一安排。
