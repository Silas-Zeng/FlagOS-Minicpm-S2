<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill i32 offset 组件筛查

M2048/KV16384、BM128/BQ16/page16私有单层组件。前三次入口/harness失败均未形成数值/计时结论；第四次通过单shape正确性门（FP64采样），但Event慢10.63%、wall慢10.21%，已停止。CPU资源变化不代表吞吐收益；不接入生产或官方。

相关代码：未单列，见原件源码清单。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component](../runs/bi-v150/20261029T003247313980Z-prefill-i32-offset-m2048-kv16k-component.md)（登记#476）：入口没有传固定GQA依赖，EngineArgs初始化时报缺少native GQA库；未进入A/B、数值或计时。 **是否保留：** 保留依赖接线失败，不称候选数值/性能失败。
- [20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component](../runs/bi-v150/20261029T004624060488Z-prefill-i32-offset-m2048-kv16k-component.md)（登记#477）：组件在scope断言停止；worker预设配置与当时selected compile scope不符，未进入A/B、数值或计时。 **是否保留：** 保留scope/harness失败，不判候选正确性或性能。
- [20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component](../runs/bi-v150/20261029T010243657857Z-prefill-i32-offset-m2048-kv16k-component.md)（登记#478）：组件完成A/B编译与Q-fragment proof后，结果记录代码访问未定义属性并退出；未形成数值/计时。 **是否保留：** 保留记录器异常，不判候选数值或性能。
- [20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component](../runs/bi-v150/20261029T010950054874Z-prefill-i32-offset-m2048-kv16k-component.md)（登记#479）：M2048/KV16384单层组件正确性门通过（FP64采样）；ABBA Event 8.347575→9.235266ms（+10.63%），wall 8.441216→9.303357ms（+10.21%）。 **是否保留：** 保留正确性与负性能证据，停止i32候选，不接入生产或官方。

## CPU

- [20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed](../runs/cpu/20261028T235007253864Z-prefill-i32-offset-v2-cpu-preparation-failed.md)（登记#472）：i32-offset v2 CPU-only编译在set_arg_attr失败：ABI attrs把整数值解成list，Triton拒绝；未进入正常kernel编译。静态7项guard通过但锁定BM128/BQ16/page32，和目标BM256/BQ32/page16不符。 **是否保留：** 保留编译接口失败，不称kernel数值/性能负；guard不适用于实际目标形状。
- [20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed](../runs/cpu/20261028T235532240420Z-prefill-i32-offset-v3-cpu-identity-failed.md)（登记#473）：i32-offset v3 CPU-only在A normal kernel身份门停止：未复现171100 selected normal hash，B候选未编译。静态guard仍是BM128/BQ16/page32，不适用于实际目标BM256/BQ32/page16。 **是否保留：** 保留A身份门失败；不放宽normal identity，也不据此判断候选数学或性能。
- [20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed](../runs/cpu/20261029T000655051332Z-prefill-i32-offset-v5-cpu-identity-failed.md)（登记#474）：i32-offset v5 CPU-only完成A normal编译，但身份仍未匹配171100 selected kernel；保留严格身份门拒绝。 **是否保留：** 保留为CPU身份失败；无GPU、模型数值、吞吐或生产资格。
- [20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic](../runs/cpu/20261029T001204223339Z-prefill-i32-offset-v6-cpu-mechanism-diagnostic.md)（登记#475）：i32-offset v6仅作CPU机制诊断：两臂normal/Q-fragment编译及proof通过，但A生产selected hash仍不匹配。资源观察A SGPR104/VGPR113/spill4，B SGPR85/VGPR112/spill0，shared 65536B。 **是否保留：** 机制proof不是数值或性能结果；明确不授生产、GPU或官方资格，保留证据并停止。
