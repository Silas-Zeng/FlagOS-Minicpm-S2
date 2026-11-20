# 局部正而官方负：定向复核

2026-10-26，CPU只读既有实验库原件；未SSH、未上卡、未修改受测代码或原始结果。

**结论：N-only新接线漏同步compute-order的runner源码身份，官方对照不再是只改变布局。此前QKV-wide、down SplitK8、O-wide、LPT均没有此漏项，不能用本次发现解释或抹去它们的已有结果，也不据此重跑O-wide。** 没有发现这四项中可通过同类最小身份修复而恢复公平对照的一项。

## 实际标记与身份

以下路径均相对实验工作树 `experiments/`。`selected/rejected`指原server的`BIV150_COMPUTE_ORDER_FIRST_SELECTED`和`BIV150_COMPUTE_ORDER_SCOPE_REJECTED`。原预期runner完整SHA为`cbbbabcea66663b033f2209febc55e75a9e14ac72d1693173d9d4aad1be7fac6`。

| 官方run | 原server行号与实际marker | 拒绝/预期与实际runner |
|---|---|---|
| `framework/20261026T044032Z-main6971-qkv-wide-four-rounds` | 第459行selected，`original_model_forward_returned=true`；selected1/rejected0 | 无拒绝；`-control/source-sha256.json`实际runner与原预期完全一致 |
| `framework/20261026T053835Z-main6971-down-small-split8-four-rounds` | 第461行selected，同上；selected1/rejected0 | 无拒绝；runner完全一致 |
| `framework/20261026T055632Z-main6971-o-wide-four-rounds` | 第459行selected，同上；selected1/rejected0 | 无拒绝；runner完全一致 |
| `framework/20261026T071618Z-main6971-lpt-early-four-rounds` | 第526行selected，同上；selected1/rejected0 | 无拒绝；runner完全一致；私有LPT Q-hoist另由`-control/lpt-posthoc-activation.json`核实际选中 |
| `official/20261026T112706Z-main6971-nonly-down-four-rounds` | 第459行rejected；selected0/rejected1 | `ValueError: 未自然加载的固定compute-order源：vllm_fl.worker.model_runner`。实际runner为`60b5dd74cbffbec3c8efc915c64e4f5e1097de0f238153339faee9c926de64b3`，而`EXPECTED_RUNNER`未同步 |

四项的`-control/stack-activation.json`均`valid=true`。前三项冻结`tmp/biv150-{qkv-wide,down-small,o-wide}-model-20261026/source.tar`内实际compute-order源码SHA均为`aab56009335ab903d1787d2b29b45721b5c7785f203d90ea4da38472e24801cd`，预期runner确为上表原SHA；LPT已存`source/plugin/vllm_fl/patches/biv150_compute_order.py`同预期。额外只核PR61 down-wide的042110与合格基线013104，分别第459/456行selected且无rejected，runner也未变。

N-only的`prefill-activation.json`并非解析器误判：`normalization_install`、Q-hoist的实际编译选中/全部constexpr stride、Graph日志和stable-small路径均通过；parse_errors为空。只有compute-order实际scope拒绝使stack/prefill总valid=false。`_cold`第138–145行对已加载runner文件逐字节核SHA，新安装钩子改了model_runner但遗漏相应身份更新。这是集成与独审漏项，不能只读“校正”JSON为通过。原路回退不等于请求、框架数值报错；两轮512 SUCCESS原样保留。

## 局部对照与新增成本

| 方法 | 局部对照是否真正生产opaque | 实际新增成本与官方结果边界 |
|---|---|---|
| QKV-wide | **不是**。043518组件worker第51行起直接调用解包的FlagGems `mm_kernel`固定256/128/32 w8s2；生产M>8原路是PR51 opaque内部`F.linear`，不能拿手工MM收益当实际生产加速 | 无永久packed副本，沿原W＋一次BF16输出，宽tile的shared/寄存器/调度变化须按实际核看。官方候选确实第93/448行命中M2048/2030；4K四轮4881.10/5496.38/5332.94/5705.54，16K冷/首暖3751.32/4104.55；已有模型结果保留 |
| down SplitK8 | 组件直接原`_small_o_kernel`而非整opaque，但它是M1–8原opaque的实际kernel；缺Python分配和所有图交织成本已声明，不能假定组件为整服务 | 每调用FP32 scratch `8*M*2048*4` B：M8为524288B，M1为65536B；producer＋reducer两launch。服务第198/206/214/222行分别命中M8/4/2/1。4K冷/首暖4889.20/5513.95，首暖观察−0.3448%；未发现身份修复理由 |
| O-wide | **不是**。055149组件worker第43–48行直接固定`mm_kernel`；实际生产原基线是opaque→`F.linear`，同QKV的控制面错位 | 无1GiB权重副本；候选只改受测M2030/2048路由与tile，原W及输出形状不变。服务第93/449行确实选中，4K三轮4894.19/5538.59/5568.49；compute-order已闭合，不能因为首暖微正或旧组件省20.33%再称其未公平测试 |
| LPT | 不是linear/GEMM候选；组件对比的是原服务Attention kernel/原数学与仅CTA工作序变化，不能套MM路由问题。私有Q-hoist实际选中已有posthoc原件 | 不新增整份权重，不改输出/scratch尺寸；改变CTA顺序可能影响cache与工作分配。4K暖均5722.4833对5656.77观察+1.1617%；16K首暖4111.36对4119.46观察−0.19663%停止，是混合结果，不能统称整体负 |
| N-only M64 | 新组件已用真实opaque→F.linear并精确原kernel hash，9门通过且单层省10.5534%；新官方pack42/FX42/M64首次选中均有实际原件 | 常驻增加1008MiB，KV实为516320对基线548336，比理想523760更低；还叠加compute-order回退。4K4758.57/5440.33、512 SUCCESS及首暖观察−1.675393%可报告，但**纯布局因果未定**；无16K/105，不修改原件、不自动重测 |

前四项服务KV均548432，参考main6971为548336；已有96-token差异继续明示，不从差异大小认定因果。N-only减少32016 token不能只用1008MiB理论24576 token完全解释；没有拆分Graph/allocator的独立测量，不编造差额原因。

## 下一步取舍

**本次审计不推荐给O-wide做“SHA修复后官方重测”**，因为其compute-order从未拒绝，官方已实际命中。若主线另有必要研究wide，唯一能改变局部结论的新证据是实际同FlagGems上下文的原opaque完整组件，而不是重复手工MM或再跑原官方；先有明确新差分才立项。

N-only是本次唯一已证实的集成对照缺口。技术上应先审新runner相对原runner仅增加安装调用，再同步实际受审身份或复用不改runner的原钩子；**这只是公平性修复，不证明收益，也不消除1008MiB/KV代价**。旧v1原样运行停止；主线已完成精确身份修复及增量独审，另以treeb528adcd进入原官方对照，结果未出。本记录本身不改变原始结果。数学错误候选一律未恢复。

已结束官方登记为#332，实验工作树332条/329唯一run。脚本`tmp/record-nonly-official-final-20261026.py`、回执`tmp/record-nonly-official-final-20261026-receipt.json`；287份原件及valid=false/SIGTERM/exit1保持原字节。
