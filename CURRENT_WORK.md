# 当前实验与接续

本批完成七轮归档：398条登记／395个唯一run，七轮725份原始文件全部保留；未为发布复跑实验。

当前有效基线仍是[框架PR92](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/92)／main b3b87d2，受测c75db814源／GQA SO f720／native14f。原官方4K／16K各四轮弃首均6481.226667／4826.446667 tok/s；原105题102/105。KV不同限制及105未证明每请求覆盖原生分支分开保留。

| 最新方法 | 已完成结果 | 处理 |
|---|---|---|
| macro0／macro1严格对照 | N64/S2/KV4096完整producer＋原reducer Event省1.0521%，wall省1.1805%，新增位型／Graph门全过 | 保留小正候选，未接生产／未扩S4，不称稳定官方收益 |
| Q32 direct-P | 175958实编；180735完整数值全过，Event慢0.0984%近持平，wall省1.0096% | 停止该方向追加优化／官方；不是数值错误 |
| mixed B61 | 真实step125的61decode＋1987prefill完整eager Event省8.8533%、wall省5.6627%，全部门过 | 保留扩原生覆盖依据；合成QKV，非官方幅度 |
| 新mixed-S4生产Runtime | 仅helper／CPP扩原已选S4的32–63且排40，CU／S2／chooser不变；182749离线SO b9bff11d；B63单次位型与B60初始／换值门全过，B60完整eager省25.5143% | f6b4／814源、treee055；候选未授新准确率／官方资格 |

mixed-S4候选原官方4K已完成主动收尾：run183747，前两轮512请求成功，首暖6168.07对145950首暖6301.93观察−2.1241%，按预设停止第三／四轮及16K／105，候选不合并。新eager覆盖与原stack门通过；KV548432对A548336不同，不能严格归因。原state completed=false及KeyboardInterrupt15是信号收尾，不是数值／框架故障；DB、源码、两库及设备清理通过。全部353原件保留，不能把两轮冒充完整官方成绩或新基线。

本批不自动启动后继测试，其他探索由主线统一安排。macro1小正候选仅保留；Q32/direct-P停止；mixed-S4组件正但官方筛选负，源码／原件保留，不为发布复测。

原始证据沿[实验总表](team/experiments.md)与[mixed-S4方法](team/methods/native-gqa-mixed-s4.md)查阅。181731完整tar流xz与全部105成员SHA已恢复验证；其余原gzip直接无损分块，原失败／负结果不改写。代码优化另按方法走PR，本实验同步不等于代码合并。
