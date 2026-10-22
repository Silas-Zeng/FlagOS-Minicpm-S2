# 末层 Attention 后的死行裁剪：局部门

仅CPU准备，尚未设备执行。当前真实链已经按root取回actual源码核实：LlamaAttention最后的o_proj（llama:233）→LlamaDecoderLayer post_attention_layernorm／MLP（328–330）→LlamaModel final norm（427）。不是删prompt的QKV或Attention，42层KV写入均不在此工具内。

`last_layer_tail.py` 用原RowParallelLinear／LlamaMLP.forward／RMSNorm.forward_native，`disable_tp=True`明确TP1、不构造分布式组。实际四源与归档副本都锁hash。只创建约80MiB随机BF16投影权重及两个norm，不加载MiniCPM5-2B权重。无安装入口、无模型hook、无主代码改动。

`validate_last_layer_tail.py` 是**纯设备child**：

```text
python validate_last_layer_tail.py --device-worker --output-dir RUN --source-dir RUN/source --model /workspace/MiniCPM5-2B
```

root的outer负责唯一设备锁、空闲／端口、child PID与超时清理、DB前后、source/env和后态封存。source目录需同名复制helper和actual四源`llama.py/linear.py/layernorm.py/activation.py`，不得改已安装文件。运行环境使用完整干净6f源码（含两原CPU helper），本门不加载ModelRunner或C3views／gather候选。

单卡owner已另备`launch_last_layer_tail_gate.py`及薄`.sh`：无参启动，固定`code/cpu-combination-combined-20261022T100830Z`，按原410参考＋6f及两helper核完整412 map，归档完整plugin；actual四源与模型config按固定SHA从安装路径复制到本轮source。唯一锁后先idle、source／DB准备后再idle，唯一GPU child超时300s、进程组清理、monitor、DBafter／双栈端口与68MiB后态／sourcepost／完整seal沿已审Event outer保留。新入口和两个原代码上传`ROOT/scripts`后执行`bash launch_last_layer_tail_gate.sh`；无需另设PYTHONPATH、另启动owner或在活跃服务旁运行。没有执行本outer主流程、copy或DB命令，只有CPU语法／stdlib无设备导入、Bash `-n`与原清理函数AST一致性核对。

只一个`lengths=[1,2047]`、M2048／N2的上界fixture，indices=(0,2047)。baseline运行全M尾段后选同N行；candidate在O投影之前选同Attention output和**同residual**，再跑相同原尾段。比较final hidden与final residual，额外一次换值／新指针／非默认stream；输入和RNG保持。实际norm可能原地消费residual，所以计时每窗32份独占工作副本在窗外重置；candidate两gather计入32-call预record ABBA。没有把baseline输入clone算成速度差。

局部容差明确为atol=0.01、rtol=0.01，记录bitwise、max abs／rel及有限性；非有限值转成字符串保存，失败也保原结果。容差不是整模型准确率或新采样结果保证。此处是**实际类的局部eager调用**，没有生产Inductor／AOT尾图接线，不能把局部提速当完整模型收益。future模型接线还需保护text-only、无spec／aux／pooling／LoRA、TP-PP-DP1及完整hidden消费者；原runner仍期待M行，不能直接把这个N行结果接回现有logits_indices。保持原M输出契约的scatter或修改logits契约都尚未实现。

收益只覆盖42层中末层的一部分；即使局部大量省时也不承诺大E2E收益。没有GPU、完整模型KV、准确率或服务验证。必要CPU检查仅语法／stdlib导入不载torch和query末行正整数边界，未铺模拟器／重跑旧套件。

最终helper **99d5a8c86dac67b7a2c0029842576fbd1439060525d4c6789b0ddd32703fc9ec**、worker **25d3e9cb194b9a6504db7f678f05d0f2113495e5bdd4d3829b82d813f153b650**。hardware已只读actual四源与新增调用／计时差分，终审无当前局部门阻断；未重跑CPU合同或设备。两文件冻结，由root串行决定最短局部门。

outer **75b06e49dbae9d39301b3cc13144a0f0b12821d6c570584cda2acea0466d4f1b**、launcher **987c3702a37e00c371f19b6780ca5a4b99044b7674e90221f0d095676adfa1b7**；新增部署差分见`outer-vs-event.diff`，CPU静态记录`outer-check.json`。只待hardware定向审外壳／root唯一设备执行，不用重跑原child合同。

hardware已完成75b06／987c增量终审并回root，无当前部署阻断；没有执行main／copy／DB或任何套件／GPU。四asset现全部冻结，等待root串行局部门。
