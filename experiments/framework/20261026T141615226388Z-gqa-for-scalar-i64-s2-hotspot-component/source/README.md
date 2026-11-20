# GQA 单个 s2 流水判别

CPU封包，未编译/未GPU。A严格保持main6971原生产641478、w1s1及原reducer；B沿用已通过8门/有限逐位的for＋scalar＋i64原kernel字节，只把候选launch的num_stages从1设2。page16/ROWS8/N64/S2长度、数学归约/FP顺序、span别名、Graph生命周期、原参考门和完整producer＋reducer ABBA均不变；这里S2是softmax split数，与num_stages=2不同。

机制针对134937真实s1有8条SME但K/V各copy后立即wait、Event慢10.73864%的反证。匹配本站Python入口的固定021f compiler在SmeLoad之后依次assign_latencies/schedule_loops/pipeline，原stage1跳过流水；单个stage2是最小判别，不是tile/stage扫描。公开generic LowerLoops.createAsyncCopy未显式转交inputStride，而CoreX SME async lowering需它；该公开C++链与本站binary身份未证，不能据此宣称本机必成功或必失败。编译失败即记失败停止；不会改compiler、硬开useSme、补s3或救错误候选。

理论新增至少跨一轮的K/V双buffer状态：每CTA两种4KiB载荷的额外live shared/寄存器、环索引与prologue/epilogue；实际分配以真实compiled资源为准，不按理论宣称occupancy。必须从新TTGIR/LLVM/ASM确认stride512B、copy与wait是否跨当前QK/softmax/PV，而非只看mask或async字样。实际stride/编译不支持则停止；数值原8门、有限硬逐位、非有限原门通过才跑唯一完整ABBA，资源只诊断。负结果停止，不进模型/官方；源码声明顺序不等于硬件FP逐位，故保留全部硬门。

一手源码（2026-10-26核读）：[固定compiler](https://github.com/flagos-ai/FlagTree/blob/021f24665bb4bcc255ddd7c38e055ece2660cda6/third_party/iluvatar/backend/compiler.py#L294-L309)、[stage1跳过规则](https://github.com/flagos-ai/FlagTree/blob/021f24665bb4bcc255ddd7c38e055ece2660cda6/lib/Dialect/TritonGPU/Transforms/Pipeliner/AssignLatencies.cpp#L306-L325)、[async copy与first-use wait](https://github.com/flagos-ai/FlagTree/blob/021f24665bb4bcc255ddd7c38e055ece2660cda6/lib/Dialect/TritonGPU/Transforms/Pipeliner/LowerLoops.cpp#L190-L223)。原地址/数学证明和s1实测引用旧包及134937，不重跑CPU几何、不把继承证明伪称新GPU资格。

root实查设备/9031后只运行一次：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/gqa-for-scalar-i64-s2-component-20261026/entry.py --source-dir /workspace/experiments/minicpm-s2/code/20261026T013104Z-main34942f7-prefill-stride-official --native-library <已核14f原生库.so> --shape hotspot
```
