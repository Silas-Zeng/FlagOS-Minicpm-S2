<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# KV 保存 / 恢复协议

单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T105526Z-mixed-bucket-row-kv-gate](../runs/bi-v150/20261021T105526Z-mixed-bucket-row-kv-gate.md)（登记#58）：Localraw independently reviewed **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T105930Z-mixed-bucket-row-kv-gate](../runs/bi-v150/20261021T105930Z-mixed-bucket-row-kv-gate.md)（登记#59）：bitwise maxdiff0 bothcases **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T200957Z-kv-protocol-context16k-long](../runs/bi-v150/20261021T200957Z-kv-protocol-context16k-long.md)（登记#94）：32成功0失败/524288in32768out/221.1178005039692s仅协议诊断，KV521936/CPU6/32768MiB/preempt0→1 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T202526Z-kv-retain-context16k-long](../runs/bi-v150/20261021T202526Z-kv-retain-context16k-long.md)（登记#95）：失败多抢占覆盖，详analysis/source/kv-transaction/202526-independent-review.json **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T204159Z-kv-page-order-context16k-long](../runs/bi-v150/20261021T204159Z-kv-page-order-context16k-long.md)（登记#96）：独立416源/0e2115+616+31cc+c95f/e155/bc51/原SERVER/seed721201；不与202526增长DB诊断算收益，未来free顺序改变保留，非完整accuracy/默认资格 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T205219Z-kv-pair-stable-context16k-long](../runs/bi-v150/20261021T205219Z-kv-pair-stable-context16k-long.md)（登记#97）：220.40704781701788s/2527.3964944282015total/TTFT62508.42458468105ms **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T205819Z-kv-pair-page-order-context16k-long](../runs/bi-v150/20261021T205819Z-kv-pair-page-order-context16k-long.md)（登记#98）：未命中ERROR但原shutdown日志保留 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T212106Z-kv-capacity-context16k-long](../runs/bi-v150/20261021T212106Z-kv-capacity-context16k-long.md)（登记#99）：227.19113439507782s/2451.9266629097337total/TTFT62762.77446313179ms **是否保留：** 未集成；失败或无收益记录保留。
- [20261021T213016Z-kv-capacity-pair-stable-context16k-long](../runs/bi-v150/20261021T213016Z-kv-capacity-pair-stable-context16k-long.md)（登记#100）：220.5050202300772s/2526.2735488686926total/TTFT62602.81379344815ms **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T213616Z-kv-capacity-pair-capacity-context16k-long](../runs/bi-v150/20261021T213616Z-kv-capacity-pair-capacity-context16k-long.md)（登记#101）：218.9170063282363s/2544.599021077285total/TTFT62573.5605845548ms **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T214400Z-kv-full-restore-context16k-long](../runs/bi-v150/20261021T214400Z-kv-full-restore-context16k-long.md)（登记#102）：226.79482778999954s/2456.2112171085555total/TTFT62775.54467374284ms **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T222731Z-kv-observed-pair-capacity-context16k-long](../runs/bi-v150/20261021T222731Z-kv-observed-pair-capacity-context16k-long.md)（登记#105）：FULL223613已齐，双方KV/组成/DB/几何同，首pair描述小信号+0.198765756%TPS；非稳定收益或独立ZERO计时 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T223613Z-kv-observed-pair-full-context16k-long](../runs/bi-v150/20261021T223613Z-kv-observed-pair-full-context16k-long.md)（登记#106）：TPS+0.198765756%/duration-0.198371462%少0.434074268s/TTFT-0.215245394%，保留单次小信号不称稳定收益或纯ZERO时间/新accuracy；本项不再重复，非稳定收益 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T224411Z-kv-observed-pair-capacity-context16k-long](../runs/bi-v150/20261021T224411Z-kv-observed-pair-capacity-context16k-long.md)（登记#107）：TPS+0.060305656%/duration省0.060269311%/TTFT+0.207191537%仅小信号，两组分层不混算 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T225501Z-kv-observed-pair-full-context16k-long](../runs/bi-v150/20261021T225501Z-kv-observed-pair-full-context16k-long.md)（登记#108）：TPS+0.060305656%/duration省0.060269311%少0.131898123305s/TTFT+0.207191537%，均保留单次小信号 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
