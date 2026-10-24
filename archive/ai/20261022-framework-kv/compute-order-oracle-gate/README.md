# 单个真实 outside q1 的独立 CPU oracle

只增诊断，原082246/075210资产不动。沿首层probe，在本次P第0层原callee返回而尚未回到o_proj/后续层时，先要求15个q1实际input/position/QKV/slot/seq/有效页表全逐bit相同，再选择本次首层Attention输出差最大的outside行。只抓该行首层实际页表对应的完整可见K/V（BF16原bits，约17MB），含本步q1；检查cache末token与实际输入K/V同bit，记录真实scale/因果/窗口/量化等配置，未知拒绝。

只做一次P时点快照，不冒充两phase各自回读。共同上下文的条件证明为：本步writer slots唯一且不碰所有活动prefix、当前K/V逐bit同、normal42层无alias、无跨步或后层写本层。若底层writer/执行违背这些已核前提，此oracle不能代替独立两phase cache实拍。额外gather/D2H同步亦可能掩盖竞态。

CPU构建：`python prepare_shadow.py --base <原422> --output <新目录> --emit-only`。root唯一GPU派发原bc51短负载。产 `oracle-context.json/.npz` 后，仅CPU运行：`python read_oracle.py --artifact-dir <EnginePID目录> --output <新JSON> --float64`。

reader只NumPy按Q-head//8选择KV，actual scale的QK→稳定softmax→PV，FP32并可追加FP64稳定性对照；不调用待疑Attention/GQA。保存两路相对独立reference的原始max/mean/RMS/逐head误差，无通过阈值、无官方accuracy/吞吐声称。
