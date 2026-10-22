# 下一 GPU 主线：仅缩短 2D V tile 的活跃期

当前6f/54c真实114435窗口：D1/P2047，2D占可见kernel累计60.2339%，实报regs102/shared65536。w16已严格通过但慢约32%，停止tile/warp扫描；visible-mask、mapped与overlap不重做，GQA已共享8个Q head，不能再声称8倍读取节省。

唯一候选是54c:436–476普通指针路径的 `v_offset` / `V_load` / `_cast_kv_tile(V_load,...)` 后移到:543原 `softmax_step` 与 `acc*=alpha` 后、原PV前。V在此前未被消费；分页表、seq_offset/dim_mask在softmax中不变。只普通BF16/2D/causal/noquant/noTD且输出不别名，原tile/BM128/T64/w8/s1、地址/读取量、QK/PV/softmax表达式及顺序不变，3D/C2走原JIT。V块逻辑数据64×128×2=16KiB；缩短其与QK/S/softmax的重叠只是源级活跃期，不证明恰省16KiB硬件shared或寄存器，也可能因失去预取而更慢。

一手实现依据（2026-10-22核读）：[Triton官方FA2 `_attn_fwd_inner`](https://github.com/triton-lang/triton/blob/main/python/tutorials/06-fused-attention.py)把V读取放在softmax/acc rescale之后、PV之前，并把M/L更新后置以控制寄存器压力；[官方教程](https://triton-lang.org/main/getting-started/tutorials/06-fused-attention.html)可复核。这里只借生命周期设计，不移植其exp2、TD、warp-specialize或新版本框架。未发现本站已测同一V迟加载点。

不优先split-KV：本站128个qblock×2KV head=256CTA，对16SM已不缺首波；[FlashAttention官方Hopper启发式](https://github.com/Dao-AILab/flash-attention/blob/main/hopper/heuristics.h)也把已有足够mblocks时默认不分段，并计入额外HBM读写代价。这只是排优先级的结构反证，不是把NVIDIA阈值当BI-V150参数。分段另需FP32 partial/merge且改归约顺序，当前不做已有3D路由或扫描。

已按root授权实现`tmp/next-prefill-v-late/`：policy89134ef1d49d532d91d460094ae7a0563d1546c7d1b8b529490b77ecfa16ab08；gate8f83395fbd8cef50cf1508e5cc05dfa94cba7fddc7961190920373c70a4675ae；generated b7aee63a1f45f39a8d917ae25b462b6c9a9ccf45c7c1d60b556e0cf1a8fad9d9。只一个新增constexpr，不添实际SME operand；exact54c byte逆回、浮点调用AST/顺序、87c6 selector原样和一次调用/异常/restore的唯一CPU合同0.0322s首次过，不是设备证明。gate复用上一D1/P2047KV16K真实层上界fixture/严格bit/KV/RNG/scale/新指针/非默认流及32ABBA，首baseline正确性call仅观察编译资源，计时baseline仍原binding。保存双方compiled资源/asm哈希；原始IR哈希可能受符号/调试身份影响，不独自证明指令不同。编译/数学门失败停止；无速度收益亦保留负结果，不接服务、不扩矩阵。root独占部署/设备，本owner无SSH/GPU。


121701实际回执（root唯一owner）：Vlate strict bits/KV/RNG/scale/新指针/流全部过，selected68/fallback0/原3D68；资源确由baseline regs102/shared65536变为candidate regs100/shared49152，双方spills0/w8/s1。32ABBA wall11.106083→11.267372ms慢1.4523%，Event10.993639→11.136706慢1.3014%，暂不集成。新源确改变了资源，并不证明优化了关键路径；减少V前取可能损失延迟隐藏，但无阶段stall证据不能定因。

是否因此再试pipeline：当前本地env/硬件记录没有每SM shared/register/thread总量，已归档actual Triton compiler.py:164/506的max_shared_mem仅证明装载上限查询/检查，不等于SM总池。比如64KiB SM池时原64与新48都最多1CTA；128KiB池时都最多2CTA，96KiB池才可能shared1→2，尚需512线程与真实寄存器分配颗粒限制。不能从shared降16KiB直接批准s2，更不能重做旧tile/stage扫描；stage加深还可能重新占用shared。没有实际上限/驻留证据前只保此负结果，优先末层tail真删工作；将来若root自然取得actual完整properties/occupancy信息再决定唯一流水点，本轮不增设备诊断。
