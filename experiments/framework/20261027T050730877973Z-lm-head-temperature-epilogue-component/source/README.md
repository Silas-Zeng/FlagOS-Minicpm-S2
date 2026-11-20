# LM-head温度epilogue单组件

只固定R64，实际head权重130560×2048、合成hidden。A为真实UnquantizedLinearMethod.apply＋完整原Sampler；B复用实际被选linear的配置/原累加代码，只在store前保BF16舍入→FP32→原温度除法，原Sampler仅跳过已完成temperature，原stats/top-p/softmax/exponential/generators保持。不是已失败stats融合；没有权重副本、量化、框架安装或官方资格。

首次真实原head调用捕获实际kernel/config/IR，SPLIT1/EVEN_K/BIAS/安装SHA不符即停，不调tile。四组hidden/temperature全scaled逐位、独立FP64样本、全filtered/IDs/global及per-request RNG、换值poisoned确定性prefix Graph/side/input不变门；错误立即停，不调容差。门后唯一完整head+Sampler eager ABBA同时计Event/wall与分配；非正停止，不扫其它R。Graph不捕随机链、不算官方收益。Event包含实际GPU全链，wall包含Python/分配，加载W不计稳态。

```bash
python3 entry.py --source-dir /workspace/experiments/minicpm-s2/code/main56f1838-pr66-20261027 --native-library /workspace/experiments/minicpm-s2/official/20261026T184110Z-main241-control-16k-four-rounds-control/native/biv150_native_w8a8.so
```

source-dir必须匹配807文件main56清单；native14f、默认FlagGems、原DB/9031/独占锁/自有PID清理沿用已审sampler v2。source路径可传实际冻结目录，不允许借其它版本。准备仅CPU，无GPU结果；每R64省95.625MiB逻辑中间流量及2launch仅预算，新增epilogue成本可抵销。

组件为输入不变门共同保留W的510MiB克隆；这是两臂共享验证资产，候选本身没有额外优化权重副本。A实际head_method在计时外构造，不把方法对象构造计作A热路。TP1/no-softcap/scale1条件下未另构造完整LogitsProcessor模型；基线真实UnquantizedLinearMethod.apply与完整Sampler，不能冒称整服务计时。
