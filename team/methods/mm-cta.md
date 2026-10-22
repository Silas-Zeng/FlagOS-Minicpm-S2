<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 矩阵乘 CTA 分组

固定tile下的映射与守卫诊断；单层收益不外推服务。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T173921Z-mm-cta-group-gate](../runs/bi-v150/20261021T173921Z-mm-cta-group-gate.md)（登记#75）：RNG true但guard_rows false **是否保留：** 未集成；失败或无收益记录保留。
- [20261021T180033Z-mm-cta-guard-diagnostic](../runs/bi-v150/20261021T180033Z-mm-cta-guard-diagnostic.md)（登记#81）：独立11源SHA/ee263/06c7/28basic文件 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T180646Z-mm-cta-group-cpu-guard-gate](../runs/bi-v150/20261021T180646Z-mm-cta-group-cpu-guard-gate.md)（登记#82）：wall1.4179341875到1.188571765625ms省16.17581577%，event1.4043543934822083到1.174988865852356ms省16.33245345%；仅fixedtile fixture非E2E/accuracy/稳定收益，不同时默认 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T182916Z-mm-cta-group-context16k](../runs/bi-v150/20261021T182916Z-mm-cta-group-context16k.md)（登记#84）：TPS+1.745903%但KV候选521840对基线521936，不称matched；原32/0后SIGTERM/abort forcekill时EngineDeadError保留，运行期无ERROR，未默认/accuracy **是否保留：** 待确认；通过某项检查不自动等于优化保留。
