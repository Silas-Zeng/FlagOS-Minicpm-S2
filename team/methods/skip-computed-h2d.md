<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 省去无消费者的 computed H2D

CPU metadata成功时省略一次计数GPU副本提交，保留原回退和固定buffer/event；方法门与独立短服务单pair分别记录，不与KV组合收益相加。

相关代码：[pr15-computed-h2d-accuracy.json](../../analysis/pr15-computed-h2d-accuracy.json)；[skip-computed-h2d-service-pair.json](../../analysis/skip-computed-h2d-service-pair.json)。

相关方法PR：[computed H2D #15（草稿）](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/15)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T214819Z-skip-computed-h2d-method](../runs/bi-v150/20261022T214819Z-skip-computed-h2d-method.md)（登记#174）：event/fixed graph消费者及RNG通过 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T215040Z-skip-computed-h2d-service-baseline-decode4k](../runs/bi-v150/20261022T215040Z-skip-computed-h2d-service-baseline-decode4k.md)（登记#175）：吞吐+0.619291%、时长−0.615480%、TTFT−1.026463%、TPOT−0.053834% **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261022T215331Z-skip-computed-h2d-service-candidate-decode4k](../runs/bi-v150/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k.md)（登记#176）：吞吐+0.619291%、时长−0.615480%、TTFT−1.026463%、TPOT−0.053834% **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261023T112356Z-pr15-computed-h2d](../runs/bi-v150/20261023T112356Z-pr15-computed-h2d.md)（登记#198）：PR15实际638c4ac0首次完整准确率100/105（95.2381%），通过原95%门 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
