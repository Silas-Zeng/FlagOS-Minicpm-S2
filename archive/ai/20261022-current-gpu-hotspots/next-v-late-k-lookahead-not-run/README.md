# V迟加载＋一步K lookahead：独立单点门

仅适用本项目天数BI-V150。**当前结论：收益机制复审不通过，不上卡；保留未测草稿。** 原静态正确性审查通过不能代替收益判断。root、hardware、framework已结合130457同SHA真实IR复审：原循环无显式下一K carry，确有潜在计算重叠窗口，但没有K等待暴露的证据；该改动不减KV字节、dot或CTA，额外16KiB K和页向量存活还可能引入等待与布局开销。每SM128KiB下，48/64KiB均未跨过更高CTA粗上限，不支持并行度增益。没有新证据前不部署下述运行方案，也不为此另起profiling或编译测试。

真实编译原件见`analysis/source/current-attention-ir/`（项目根目录下），8份文件均匹配130457结果中的SHA，只读取回，无新GPU执行。以下内容保留为已完成的CPU准备，不表示上卡批准。

| 资产 | SHA256 |
|---|---|
| `biv150_prefill_k_lookahead.py` | `1919c50be7914d7d77ff81910e84835fa6ab0589f9e9ba677dab3aa0885e7559` |
| `validate_prefill_k_lookahead.py` | `ab9a47874b4234c2f7d9dbd51c98053204a4953685cafcb5a90130915e1ce5c2` |
| 由exact54c生成的`generated_attention.py` | `06ad08f22f275bb696143bbe9fdcd19821d262d01d99f57860e8606863f43644` |

变换保留w8/BM128/T64/s1、原page遍历、mask、QK→softmax→accscale→PV浮点调用顺序。V仍按受测Vlate后移；首K只在`loop_lo<loop_hi`时预取，之后仅`j+1<loop_hi`取下一K，且与对应物理页向量一同carry。当前V使用当前页向量的SSA值；最后/空loop不额外读页表或K，partial tile保持原边界mask。3D及未知配置全部原C2路径。

唯一新CPU合同`check_transform_cpu.py`首次0.0530856s通过，记录于`cpu-check.json`：两层精确byte逆回54c、FP调用AST、原guard、9个tile边界条件、当前指针、原异常不重试与完整restore。没有导入Torch/Triton，没有设备数值或流水证明。此目录的`baseline.llir.txt`/`candidate.llir.txt`仅CPU fakecompiled写出的`original`/`candidate`字符串，**不是编译器IR**；真门只分析独立run/source内的编译输出。

framework已全文只读1919/ab9/generated06ad和CPU receipt，无本轮最短门阻断；未运行合同或GPU。

运行接口复用Vlate门：

```text
python validate_prefill_k_lookahead.py --run-dir RUN --runtime-path C2_RUNTIME --mixed-path C3_RUNTIME --policy-path biv150_prefill_k_lookahead.py --model /workspace/MiniCPM5-2B
```

根owner沿现有launcher使用干净6f基点`/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z`，保留原helper依赖与唯一flock/child/monitor/cleanup。

同一次worker仅D1/P2047/KV16K上界fixture；实际native窗未记录精确seq_len，故不称精确回放。先严格bits、误差记录、整KV/RNG、scale、新Q/out与非默认流，编译/资源/数值失败即保原件停止。通过后直接一次32ABBA，同时在首次correctness编译时保存TTIR/TTGIR/LLIR等实际可得asm及资源，计时窗不重复写文件。没有compile-only第二次启动、tile/stage扫描或服务集成。

候选有不同hash/较少shared不足以证明有效流水。后验须核loop carry、真实load与PV次序/同步、实际shared/regs/spills及墙钟/Event；IR未保留lookahead或无收益就停止此点。SDK128KiB每SM仅给粗资源边界，不能推导实际驻留。当前尚无GPU结果或E2E收益。
