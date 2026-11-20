<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 当前Q32与GQA混合双流

完整GPU耗时负，不进入生产，不扫形状或流优先级。

相关代码：[archive-receipt.json](../../experiments/framework/20261027T030312159264Z-q32-mixed-overlap-mixed-component/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T030312159264Z-q32-mixed-overlap-mixed-component](../runs/bi-v150/20261027T030312159264Z-q32-mixed-overlap-mixed-component.md)（登记#356）：main241真实D63/P1985/KV4096，Q32 grid63×2，GQA自然S4/grid63×2×4。A串行、B原93c双流，完整writer+两路Attention/reducer+fork/join/event/record_stream/collect均计入。32calls AB **是否保留：** 完整GPU耗时负，不进入生产，不扫形状或流优先级。
