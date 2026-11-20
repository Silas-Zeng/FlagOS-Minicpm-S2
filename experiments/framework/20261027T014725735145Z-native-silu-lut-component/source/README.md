# native SiLU有限BF16域查表：唯一M2048组件

主线main241的34层native gate先将gate/up反量化各舍入BF16，SiLU在FP32算完后乘up、再BF16输出。新核保留全部这些边界，仅把65536种BF16 gate的原FP32 `gate/(1+expf(-gate))`，由同device/同-O3表达式一次生成256KiB表，消费时索引读取；无近似/插值、无新量化或服务参数变化。原launch/tile/quant/int_mm不改，不重复vec2/PR37融合。当前仅CPU准备，尚未编译或GPU验证。

A加载已核14f真实生产SO调用gate_silu_auto，B私有前缀原cached256 quant→同ATen _int_mm→新尾，固定M2048与真实layer20 gate/up权重（按原生产quantize_weight函数生成Wq）。默认FlagGems上下文记录实际_int_mm dispatcher。设备表构造不在稳态Event内，256KiB持久额外成本明示；若未来接模型，必须在KV sizing前分配且全34层共用，不得每层复制或隐藏预算。

最短门先全部65280有限BF16 gate ×12种up的完整逐位，含±0/极值；再真实完整gate四pattern、独立CPU INT64样本、同址换值/poisoned Graph、side、输入/表/RNG不变。任何差异即停不放宽。全部通过只完整native gate一次ABBA；负即停止，不扫M或变体、不自动模型。不是只量尾处理。原owner设备/9031/锁/DB恢复及清理复用，入口python3 entry.py由root独审排卡；不自启动。表资源可能替换SFU等待为更多L2读/寄存器成本，不能预报收益。

已有084521 M64 native尾区间和0.325987ms/34层、旧072151 M2048约7.795ms仅供量级排序，非当前main241整场占比/收益上界；真实净收益看本完整gate，之后再决定其它M与整模。此包无当前生产接线、准确率/官方资格。源与CPU合同/pins均在同目录；baseline路径固定184110控制组14f原件，不替换SO。
