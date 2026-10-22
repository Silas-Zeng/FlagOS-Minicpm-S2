<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 输入准备成本诊断

当前组合的真实输入等待与预处理累计；诊断耗时不作为性能收益。

相关代码：[prepare_input_prep_timing.py](../../scripts/remote/input-prep-timing-combined/prepare_input_prep_timing.py)；[biv150_input_prep_timing.py](../../scripts/remote/input-prep-timing-combined/biv150_input_prep_timing.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T104544Z-input-prep-timing-combined-decode4k](../runs/bi-v150/20261022T104544Z-input-prep-timing-combined-decode4k.md)（登记#126）：EngineCore288617最后快照256步，wait累计1.858095ms/max34.337us，preprocess累计4.553460970s，等待占0.0408%；诊断有计时扰动，不报性能收益 **是否保留：** 保留诊断结论；当前不据此实施输入同步优化。
- [20261022T104920Z-input-prep-timing-combined-context16k-long](../runs/bi-v150/20261022T104920Z-input-prep-timing-combined-context16k-long.md)（登记#127）：EngineCore289848最后快照2048步，等待累计14.059984ms/max132.438us，预处理累计14.488006758s，占0.0970%；输入等待方向暂降优先级，诊断不报性能收益 **是否保留：** 保留诊断结论；当前不据此实施输入同步优化。
