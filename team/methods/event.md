<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Event / graph 能力与等待

能力门、完成性及等待CPU的正负结果。

相关代码：[validate_event_wait_gate.py](../../scripts/remote/validate_event_wait_gate.py)；[validate_native_event_wait_gate.py](../../scripts/remote/validate_native_event_wait_gate.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T045818Z-event-wait-gate](../runs/bi-v150/20261022T045818Z-event-wait-gate.md)（登记#116）：Event、B cuda.Event默认、C cuda.Event(blocking=True)，非0显式流/每trial8次32MiBpinned D2H/六窗ABCCBA各4trial，共24trial144checks及RNG全过，early_complete总0，完成后无额外同步才核host… **是否保留：** 未集成；失败或无收益记录保留。
- [20261022T051336Z-native-event-wait-gate](../runs/bi-v150/20261022T051336Z-native-event-wait-gate.md)（登记#117）：wall9.419391/9.421018ms，无CPU下降证据，未接入服务 **是否保留：** 未集成；失败或无收益记录保留。

## 未记录

- [20261021T044007Z-graph-events](../runs/unrecorded/20261021T044007Z-graph-events.md)（登记#16）：events fail elapsed_time after CUDAgraph replay and sync with ixErrorInvalidResourceHandle **是否保留：** 未集成；失败或无收益记录保留。
