<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Q-hoist + GQA 框架组合

仅适配精确GQA包装的安装身份，保留两条算术路径与原服务参数；已获单pair正信号及独立101/105准确率通过，评测DB增长另列。

相关代码：[METHOD.md](../../archive/ai/20261022-framework-kv/q-gqa-framework/METHOD.md)；[biv150_q_fragment_service.py](../../archive/ai/20261022-framework-kv/q-gqa-framework/biv150_q_fragment_service.py)；[q-gqa-service-pair.json](../../analysis/q-gqa-service-pair.json)；[accuracy-review.json](../../experiments/accuracy/20261022T184819Z-q-gqa-framework/accuracy-review.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T183552Z-q-gqa-service-baseline-context16k-long](../runs/bi-v150/20261022T183552Z-q-gqa-service-baseline-context16k-long.md)（登记#159）：32成功0失败 **是否保留：** 保留作GQA对照基线；组合单pair正信号与独立准确率另列。
- [20261022T184141Z-q-gqa-service-candidate-context16k-long](../runs/bi-v150/20261022T184141Z-q-gqa-service-candidate-context16k-long.md)（登记#160）：吞吐+7.466632%、wall省6.947861%、TTFT−9.416976%、TPOT−6.786409%；单pair正信号保留，非稳定统计或完整官方性能，组合accuracy pending不继承单项 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261022T184819Z-q-gqa-framework](../runs/bi-v150/20261022T184819Z-q-gqa-framework.md)（登记#161）：组合准确率101/105（96.190476%）通过原官方Math500 Level3门，105 success、0 transport错误、0 output cap、无空答案 **是否保留：** 组合准确率通过；性能仍仅单pair，不据此声明稳定或完整官方成绩。
- [20261022T202736Z-q-gqa-framework-official](../runs/bi-v150/20261022T202736Z-q-gqa-framework-official.md)（登记#170）：两case×4完成exit0、1536成功0失败，原driver核8行raw/2行summary及丢首轮2–4均值，未改CSV **是否保留：** 待确认；通过某项检查不自动等于优化保留。
