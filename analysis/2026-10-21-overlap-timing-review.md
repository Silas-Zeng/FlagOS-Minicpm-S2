# 双流 Attention 首轮：正确性通过，速度证据冲突

2026-10-21。CPU-only读取root已下载的 `experiments/framework/20261021T113727Z-mixed-attention-overlap-gate/results.json`、manifest、exit-code；无SSH/GPU，未改原run或914脚本归档。root继续独占设备，下一次只需一个长计时窗口复核，不扩形状/正确性suite。

## 原始证据

run113727原gate SHA914f7…，overlap runtime93c312…，同原C2e5f68/C3a129、D29/P2019/KV16K。exit0；全部output int16 bits/finite/padding/整KV/RNG/实际两call选中、no-plan fallback均true，pending_after_sync=0。原preflight/postflight为9031free、32700MiB free；这是合成单层验证，不是模型accuracy或端到端性能。

| 原ABBA窗口，每组4calls | wall ms/call | GPU event ms/call |
|---|---:|---:|
| serial A1 | 12.899097 | 12.428180695 |
| overlap B1 | 12.59615525 | 12.550149918 |
| overlap B2 | 12.5275255 | 12.484626770 |
| serial A2 | 12.86824525 | 12.414301872 |

由原数据独立算得：serial wall中位12.883671125，overlap12.561840375，表面wall下降 **2.497974%**。但event中位为12.4212412834→12.5173883438ms，反而增加约 **0.77405%**。不能仅挑wall作为正收益，也不能直接说硬件重叠已经发生。

serial平均每组wall-event为 **1.849719ms**，overlap为 **0.177808ms**；两者组间差 **1.671911ms**，除4后是0.417978ms/call。它减去event路径增加的0.096147ms，恰好等于表面的wall减少0.321831ms。因此现有结果完全可以由GPU窗口之外的host/计时差别解释，没有必须诉诸真实Attention加速的剩余量。

这不是已定位“Event constructor必然是根因”。old914把timing Event对象创建、首次record、提交、collect及末尾全卡wait都放在wall中；OS/驱动等待和事件惰性初始化都可能影响wall-event。且event窗口仍包括device队列中因CPU提交造成的空档，并非孤立kernel累加时间。[PyTorch2.10 Event文档](https://docs.pytorch.org/docs/2.10/generated/torch.cuda.Event.html)明确底层event首次record时才惰性初始化；仅提前构造Python对象不保证排除驱动创建成本。CoreX具体实现尚未据源码或trace定位。

## 最小方法修正

原914完整bytes另存 `analysis/source/mixed-attention-overlap/validate_mixed_attention_overlap_914f7eb3.py`，SHA仍`914f7eb3abee25f05af8cb1a7a78eb96ede7b8c88aaf427014e16b3f745ae291`。原run source/results保持原件。

当前gate改为 **`ab1cd95e2f0582e1efa1deb1321887a041a88a068c655627360bb6eee4817eba`**：

- 新CLI `--timing-loops {4,32,64}`，缺省仍4；仅改变每个ABBA窗口调用次数，仍只有原一个形状、一个ABBA、同runtime/kernel和原正确性步骤。
- controller→worker exact argv、manifest和results均记录loops；worker同时记录自己的完整argv与shell命令，避免默认参数丢失。
- 方法明确标`v2`：timing Event Python对象在wall begin之前创建；record、callback submit/collect、末尾synchronize仍在wall内，elapsed读取仍在wall外。不声称首次record的惰性驱动初始化已排除。

假如旧组间1.671911ms差为固定项，32calls摊到约0.052247ms/call，64calls约0.026124ms/call，远小于4calls的0.417978。此为条件算术反证，不是新实测预测。root可只选 **64calls一次ABBA** 或32calls一次，不需要两套都跑；先观察warmbucket按既定队列完成，不能并发。

新旧gate方法和loops不同，因此不要把两次“下降百分比”直接当重复确认；判断同一个新run内serial/overlap pair的event与wall是否趋于一致，以及每组额外时间是否按调用数摊薄。若长窗口event仍慢而wall优势消失，则停止服务集成；若仍有一致可辨正信号，才值得后续完整42层强引用峰值设计与端到端筛选。

CPU最小检查仅py_compile、--help及对比原914的具体diff，均通过；未加新CPU模拟、正确性suite或形状。framework_innovation已独立核最终ab1 SHA及全diff，确认CLI/default、controller/worker/result参数贯通、方法边界和旧914归档无阻断，可按root只补一次32或64窗口，不扩新测试或精度门。详细回执已落handoff。

## 64calls真卡复核：不服务集成

root执行并下载 `experiments/framework/20261021T114553Z-mixed-attention-overlap-gate/`。本owner已CPU读实际results、exit-code/source SHA；gate ab1、runtime93c、loops64/method v2身份正确。全部原正确性true、exit0、pending_after_sync=0、peak_pending_frames=9，仍只说明单层对象生命周期/数学通过。

| 新run内ABBA，每组64calls | wall ms/call | GPU event ms/call |
|---|---:|---:|
| serial A1 | 12.465604563 | 12.414513588 |
| overlap B1 | 12.418428031 | 12.415083885 |
| overlap B2 | 12.415788156 | 12.413187981 |
| serial A2 | 12.455693953 | 12.403859138 |

wall中位12.460649258→12.417108094，仅下降 **0.349429%**；event中位12.409186363→12.414135933，增加 **0.039886%**。event几乎持平略慢，没有GPU窗口的明确正信号。serial/overlap平均每组wall-event仍相差3.103407ms，摊64为0.048491ms/call，足以解释全部wall差0.043541ms/call；不能把它当硬件并发加速。

因此首轮2.50% wall不构成可重复收益，当前只剩未确认的微小host信号；**停止服务集成，不追加窗口、形状或大准确率测试**。不宣称硬件不支持并发，仅说明这一实际同层方案尚无值得承担42层强ref峰值/流依赖复杂度的明确收益。原914和ab1两个run/source/raw结果均保留，新旧计时方法不混算重复结果。
