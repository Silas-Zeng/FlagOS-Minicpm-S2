# R64采样预处理与原首遍统计融合组件

只准备CPU，尚未Corex编译、GPU数值/计时、105或官方验收。原main241与native14f不改，旧负Gumbel路线不启用。

固定真实词表130560、R64、BF16。先用真实lm_head.weight和合成hidden调用当前`UnquantizedLinearMethod.apply`，确认实际BF16输出、原head provider源码；此一次head调用不计采样收益，也不是live模型输出。A是当前实际`Sampler.forward`完整调用，FlagGems与Iluvatar原unwrap/原histogram top-p安装与当前worker相同。B只改FP32转换/温度除法/首遍stats的物化边界。

新首遍读BF16→精确FP32转换→原FlagGems同表达式`x / y`（**不换div_rn**），写原大小FP32 logits，然后走逐字保留的4096列块max/sum-exp次序。原row_max_reduce、两轮hist/walk、mask、softmax、exponential_、argmax不改；每请求生成器与随机调用仍原函数。组件私有函数克隆不重绑生产类；原forward/sample均有精确逆AST，TopK forward_native复用原code object，仅确定性filter入口绑定本实例。

适用合同是all_random、top-p-only、无logprobs/penalty/allowed mask/badwords/任一processor/thinking tracking/spec。未知拒绝组件，不通过提前温度处理改变processor次序。component只构造合法正温度与合法top_p，并使用真实SamplingMetadata；空processor对象仅提供原方法读取的两列表。其它生产场景没有新增路由。

R64逻辑读写143.4375→47.8125MiB，少95.625MiB/2 launch；这是字节预算而非收益。FP32输出与原cast相同形状和大小、原hist workspace共用，pending在filter前消费并在finally清空，不留每轮logits持久引用。**完整eager ABBA包含新分配、原softmax/噪声/除法/argmax及提交；Event与wall都报告，任一非正就停。** 不只计新首遍。head预生成/一次编译、正确性快照不计稳态，但原调用和新调用的每轮分配都实作；不能把Graph replay称计入CPU allocator。

先核当前15个安装文件SHA/实际_to_copy与div_.Tensor注册及CUDA dispatch，在真实A调用观察BF16→FP32和FP32除法；身份不符即停。逐位比较scaled、filtered、全部stats、sampled IDs和最终global/per-request RNG；首个真实head输入另外走独立CPU FP64温度1转换参考。含换值、零/ties、合法不同温度、top_p0/1、混合每请求生成器、side stream和计时后检查，任错停止不放宽。Graph只覆盖**新改动的确定性前缀**，输入/温度/p换值、污染输出并与eager逐位对比；随机数仍eager原路，不声称完整随机Sampler可capture。

入口由root排卡：`python /workspace/experiments/minicpm-s2/scripts/DEPLOYED_DIR/entry.py`。同旧owner单卡锁、GPU/9031前后检查、DB备份恢复与自有PID清理；不会启动服务。result非正/错误停止，不扫其它R/参数、不进模型。

当前安装源码原件：`archive/hotspot-layout-20261026/installed-sampler-20261027/`，manifest标实际路径/SHA；sampler1a2f18dd、topk35b9a1ff与旧原件逐字相同，但本轮已重新只读确认。histogram main241 SHAda77c411。CPU检查仅证明源码合同、65280有限BF16转换和8355840输出地址覆盖，不模拟Corex近似除法，也不宣称设备逐位已通过。

`cpu_harness.py`以无Torch/GPU假对象执行实际Sampler/TopK方法及新克隆，确认原tail→softmax→原随机函数次序和同一个generators对象、仅一次新FP32分配、13类资格拒绝及pending异常释放。它只验证Python调用合同，不冒充设备RNG或数值通过。
