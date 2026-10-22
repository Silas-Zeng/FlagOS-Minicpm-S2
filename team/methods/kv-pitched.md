<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# KV 二维 SAVE 复制

保留KV字节和逻辑顺序的正等差复制；单层信号与真实42层诊断分开看。

相关代码：[biv150_kv_pitched_copy.py](../../patches/framework/candidates/biv150_kv_pitched_copy.py)；[biv150_kv_pitched_bridge.cpp](../../patches/framework/candidates/biv150_kv_pitched_bridge.cpp)。

相关方法PR：[二维SAVE工具 #4](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/4)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T032653Z-kv-pitched-copy-gate](../runs/bi-v150/20261022T032653Z-kv-pitched-copy-gate.md)（登记#113）：两case18checks/计后5checks/CPU-GPU RNGtrue，独立CPU页号+offset pattern payloadSHA均复算同，源及两端guard/完整输出通过；首case8call ABBA wall7.415286/0.672265/0.681895/1.454229ms，event0.652492/0.628267/0.628109/0.652680ms，仅C batch+2D组合单层信号，基线wall波动大不报稳定收益/2D独立贡献/42层服务或E2E **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T035754Z-kv-pitched-threeway-gate](../runs/bi-v150/20261022T035754Z-kv-pitched-threeway-gate.md)（登记#114）：两case30checks+计后7+CPU-GPU RNG/独立CPU完整payloadSHA全部过 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T042225Z-kv-pitched-save-context16k-long](../runs/bi-v150/20261022T042225Z-kv-pitched-save-context16k-long.md)（登记#115）：event完成且源free前42层旧c95f对照966calls/同nbytes全bytespass **是否保留：** 待确认；通过某项检查不自动等于优化保留。
