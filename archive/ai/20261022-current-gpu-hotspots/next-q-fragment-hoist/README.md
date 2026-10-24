# Q fragment循环外保留：唯一单点准备

仅BI-V150、干净6f/Attention54c、原w8/BM128/T64/s1。尚未编译或上卡，不改installed、原JIT cache或全局编译hook，不叠Vlate/cache/lookahead。

资产：policy `80d63add1d209335ebdc2c16cc605dd5fd89e6d63d0f7b1b456990804c863097`；gate `6a7f042d91a509f5f0c6950c9856efcc9d0a4c22035f3747214c7d5e0f789853`。原TTGIR固定`ff6456f7…`，变换后`1543c2f348a96d68abda955e0333feaa1dd007eeb59593b5445d5d8a8e3f42af`。

实际原TTGIR的Q local_alloc在loop外、dot-layout local_load在loop内，LLVM/ASM每K tile重复读Q。变换仅把同一local_load外提；保初始shared写、所有mask/dot/softmax/PV及3D/C2。空loop时新读也是已初始化的内部Q scratch，不新增KV/页表访问；原早退、loop与输出计算保留。Q的跨warp可见性及scratch后续复用由原lowering负责，真实IR/数值门仍必需；不先宣称释放32KiB shared或驻留翻倍。

原baseline正常launch返回后才捕获真实TTGIR、native binder specialization/options、完整caller kwargs recipe和ASTSource ABI/constants/attrs。仅相同scalar值/类型、tensor dtype/device/shape/stride/对齐及native specialization才选；数据指针和tensor内容不缓存，当前Q/out原样传。KVQuantMode只接受actual7e3c的明确IntEnum类别。baseline/candidate每次仍走原JIT前缀、FlagPrism、SME、globals、current stream与hooks，额外per-call `ir_override`只指向新内容SHA命名文件，私有JIT cache隔离。保存的是caller binder recipe，并非声称另外重放了原prefix注入后的options；当前compile knobs另锁定，不重复调用FlagPrism。

IR只以`xb`写新文件并立即校验，首候选compile前、正确性后、计时前后再核。热cache路径没有IR文件读取；guard及额外binder开销仍计入submit/wall。没有手工CompiledKernel发射或全局override。

唯一新增CPU合同首次0.0627208s通过（cpu-check.json）：真实IR精确逆回、原alloc/dot/yield保留、真实baseline LLVM循环Q读16；fake编译器的已外提CFG识别、clone/cache隔离、当前指针、IntEnum、fallback、原异常一次/同context、热路径禁读IR与恢复。未导入Torch/Triton、未真实编译；stub数值和资源不是设备证据。复用原门其它合同，不重跑。

```text
python validate_q_fragment_hoist.py --run-dir RUN --runtime-path C2_RUNTIME --mixed-path C3_RUNTIME --policy-path biv150_q_fragment_hoist.py --model /workspace/MiniCPM5-2B
```

沿旧唯一controller/干净6f `cpu-combination-combined-20261022T100830Z`，D1/P2047/KV16K上界fixture。先strict bits/误差记录、整KV/RNG、scale、新Q/out与非默认流，实际TTGIR外提及LLVM循环Q内存读消失必须通过；无机制或编译/数值/资源失败即停。通过后同worker一次32ABBA，首次编译保存真实TTIR/TTGIR/LLIR/ASM/资源供检查Q写→同步→读及实际活跃成本，不把摘要barrier计数当完整同步证明。没有模型准确率、服务或E2E收益结论。

framework已全文定向终审80d63add/6a7f042d及CPU receipt，无当前CPU准备阻断，未重跑合同。其回执不是收益或上卡批准：真实barrier/空loop/lifetime、资源与循环Q读消失仍待实际编译及bits门。root唯一SSH/GPU owner，最终执行由root决定。
