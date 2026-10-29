<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill i32 offset CPU 编译筛查

v2/v3在编译接口与A身份门停止，且其旧guard BM128/BQ16/page32不适用于实际BM256/BQ32/page16目标；v5正常编译后A身份仍不符。v6只做CPU机制诊断：两臂normal/Q-fragment编译与proof通过，但A生产selected identity仍不匹配。全部保留为CPU筛查，不授予生产、GPU、官方、数值或吞吐资格。

相关代码：未单列，见原件源码清单。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## CPU

- [20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed](../runs/cpu/20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed.md)（登记#472）：i32-offset v2 CPU-only编译在set_arg_attr失败：ABI attrs把整数值解成list，Triton拒绝；未进入正常kernel编译。静态7项guard通过但锁定BM128/BQ16/page32，和目标BM256/BQ32/page16不符。 **是否保留：** 保留编译接口失败，不称kernel数值/性能负；guard不适用于实际目标形状。
- [20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed](../runs/cpu/20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed.md)（登记#473）：i32-offset v3 CPU-only在A normal kernel身份门停止：未复现171100 selected normal hash，B候选未编译。静态guard仍是BM128/BQ16/page32，不适用于实际目标BM256/BQ32/page16。 **是否保留：** 保留A身份门失败；不放宽normal identity，也不据此判断候选数学或性能。
- [20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed](../runs/cpu/20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed.md)（登记#474）：i32-offset v5 CPU-only完成A normal编译，但身份仍未匹配171100 selected kernel；保留严格身份门拒绝。 **是否保留：** 保留为CPU身份失败；无GPU、模型数值、吞吐或生产资格。
- [20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic](../runs/cpu/20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic.md)（登记#475）：i32-offset v6仅作CPU机制诊断：两臂normal/Q-fragment编译及proof通过，但A生产selected hash仍不匹配。资源观察A SGPR104/VGPR113/spill4，B SGPR85/VGPR112/spill0，shared 65536B。 **是否保留：** 机制proof不是数值或性能结果；明确不授生产、GPU或官方资格，保留证据并停止。
