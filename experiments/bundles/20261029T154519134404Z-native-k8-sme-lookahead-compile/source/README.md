# NativeK8 K-SME lookahead 编译候选

从 main `899ce77470b0b539aebc108fd122f668c2d5894d` 的 K8 lookahead `.cu` 与 codec `.cuh` 精确blob生成一个隔离的 compiler-only 候选。`make_variant.py` 固定base blob、每个锚点恰好一次替换，并反向还原到原始CU逐字节相等；生成的 `pins.json` 记录源/候选/codec身份。

候选仅将完整页K0 prologue及当前页之后的完整next-K搬运改成两条 `__ivcorex_sme_load_16x1b64_colxfb8`，descriptor strideBytes=256、K offsets 0/64。next-K issue 位于原V `waitcnt(8)`和ready barrier之后、当前PV loop之前；其 `waitcnt(8)` 位于当前PV loop之后，随后保留原页尾barrier。`PackedNextK`、read/publish删除。尾页partial path继续使用原`issue_k_i8(valid,...)`和mask；`has_next`仍限制为 `next_position < full_upper`，不会预读segment尾页。

Qcodec、QK、softmax、PV、FP累加/顺序、输出、S2/S4 grid及8192B shared声明均由锚点逆验证保证不变。预期成本：每个候选next full page发出2个异步SME load并消耗同一K stage；它与当前PV重叠，但页尾新增wait8，prologue也增加一次wait8。没有正确性、吞吐或硬件性能结论。

`compile_only.py --out /fresh/absolute/path` 只生成device LLVM IR与ASM并采集S2/S4符号、SME/wait/MMA相关行和可见资源注释；不导入Torch、不链接SO、不初始化CUDA或launch。由root显式执行编译；无需也禁止本准备任务运行GPU。编译后需从真实LLVM/ASM确认K-next SME在PV前发出、wait在PV后，若后端把wait提前到PV前则停止，不修补别的调度。
