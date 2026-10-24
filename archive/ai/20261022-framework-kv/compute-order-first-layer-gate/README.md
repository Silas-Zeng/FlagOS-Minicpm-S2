# 第0层最短分歧定位

沿075210同一一次原序→P shadow，只在actual Attention3414 custom-op内部动态读取的第0层 `impl.forward` 实例加临时观察。原C3 bound callee两phase各一次，不改算子、编译入口、graph/调度/采样或旧证据。只观测15个q1，P恢复原请求行比较输入ID、位置、Q/K/V、Attention输出、seq及有效页表/slot；第0层输出若已不同便无需猜42层传播。原序outside可能走Q-hoist 2D，P走GQA，因此不预先判任一方正确。首层Q/GQA计数仅为这次callee内Python选路证据。

入口沿 `prepare_shadow.py --base <原422> --output <独立新目录> --emit-only`，五路径镜像、完整424map；env沿 `BIV150_COMPUTE_ORDER_SHADOW_DIR`。旧shadow目录和075210原件不动。新增 `original-layer0.npz`/`permuted-layer0.npz` 保BF16原bit及FP32值，小JSON保实际layout、行映射与路由；`layer0-comparison.json` 保原始误差和有效页表逐行相同，不加容差门。整体logits原诊断继续保留，任何shadow后异常原抛且不重试。

最终镜像用 `files-final/` 与 `files-final-prepare.json`；`files/` 是生命周期修复前初稿，禁止部署。helper `d958a1b660dc643ccc63b49e00e7bae07edfee52ee3dae3ffc34c71177172254`、runner `af830c1e971f0f040afa03134329e55034463c2c0e36e2f47ae3bc84abfe287a`。两phase各自只在原_model_forward局部try/finally内拥有实例入口，原序后层/logits或P准备失败不留hook；cold锁同ForwardContext的第0层对象与原a129 bound callee，无宽泛unwrap。

CPU已过语法/完整map/精确逆回，待新增窄审；未运行模型、设备或新mock。owner由root唯一派发，诊断开销不作吞吐；额外gather/D2H同步可能掩盖竞态，所以只归因于诊断同期的实际输入/输出。必须同时产 `layer0-comparison.json` 和两个NPZ才称首层覆盖，普通exit0或旧 `result.json` 不代替它。


新增只读互审已完成：helper `d958a1b660dc643ccc63b49e00e7bae07edfee52ee3dae3ffc34c71177172254`、`files-final` runner `af830c1e971f0f040afa03134329e55034463c2c0e36e2f47ae3bc84abfe287a`、preparer cd3475ac、receipt 9a85f079；旧files初稿不部署。actual3414 custom-op动态impl接点、staticcontext实际第0层对象/原a129 bound、原请求q1行对齐与实际input/position/QKV/seq/table/slot/output快照均核。初稿phase0后异常归还缺口已用两phase各forward外局部try/finally修正，原callee各一次、无采样或旧路重试；Q/GQA计数字段与当前源一致。当前可进入一次短诊断；新增gather/D2H同步可能掩盖时序问题，首层相等不代表后续层/全模型等价，不改容差或称性能。只静态新增风险审核，未运行合同、模型、SSH或GPU。
