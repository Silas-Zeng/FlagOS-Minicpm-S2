# 冻结R64 head温度版本：16K原官方四轮B

仅CPU薄入口；生产31094098/809源/5diff逐字不变，不含R32改动。仅原test-case改成[[16384,1024,64,128]]、标签16K、baseline_reference固定真实本次A `official/20261027T075834Z-main56-control-16k-four-rounds`。不猜run、不自动挑旧run、不继承4K值。A未完整四轮成功/源码native与DB清理闭合则立即拒绝，不等待或排队。首暖及暖均从本A唯一原CSV动态读取，原参数/benchmark不改。

按root明确目的，本16K可合法不命中R64：head无SELECTED/SAMPLED且无异常只记not_exercised_R64，不因缺覆盖停；一旦选中则READY/SELECTED/SAMPLED和原身份须闭合。原REJECTED/RAW_FALLBACK/parse异常处置、compute-order/native/provider原栈、同KV及共同初始DB全部保留。若四轮通过却无head覆盖，只说明该源码在此负载的整体非退化观察，不把收益归head。组件/4K成绩不代替本16K。

root独审且A完成/设备空闲后手动决定执行，本包不启动、不排队：

```bash
python3 official_supervisor.py /workspace/experiments/minicpm-s2/code/main56-head-temperature-31094098 main56-head-temperature-16k
```

supervisor原首暖筛：第2轮对本A第2轮，负停；正则跑完四轮，不因后续暖轮波动停。driver异常立即停。冷后原stack/同KV门保留；完整posthoc/provider由原owner收尾。CPU只核负载/新A、缺R64覆盖及其余异常、原command/finally AST、原源码manifest，未做新GPU/SSH/105。小diff与cpu-check在本目录。
