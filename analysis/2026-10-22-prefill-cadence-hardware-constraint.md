# Prefill节奏的一个源码约束：chunk数不等于Attention KV重读倍数

本轮只提供一条供framework调度研究使用的反证，不实现新策略、不修改token预算/服务参数、不新增扫描或设备门。仅适用本项目天数 BI-V150 16SM/32GiB、6CPU配额、MiniCPM5-2B BF16 与受测54c/59d9；不外推整板或C500。

## 一手资料与需要避免的外推

[Sarathi-Serve §4.3](https://arxiv.org/html/2403.02310v3#S4.SS3)讨论小chunk的固定开销、利用率和既有KV重读，并明确最佳预算依赖模型、硬件和SLO。[vLLM v0.24.0官方调优文档](https://docs.vllm.ai/en/v0.24.0/configuration/optimization/#chunked-prefill)也将较小预算的ITL与较大预算的TTFT/吞吐相权衡；其中面向大GPU的数值建议不是BI-V150结论。本比赛原参数保留，因此这些资料只作为实现成本分析，不转化为启动参数调整。

这里最重要的限制是：**不能把论文所述chunk重读直接算成本项目Attention原KV tile循环数乘以chunk数量。** 下述源码分块已存在，必须先按实际query tile检查。

## 固定源码的代数边界

actual installed源码保存于：

- `experiments/official/20261021T092944Z-sql-mixed-official/source/installed/vllm/v1/attention/ops/triton_unified_attention.py`，SHA `54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f`。:878–881为MiniCPM prefill固定BM128、BQ16、T64、8warps/1stage；:301虚拟CTA无效先返回，:320以 `16*q_block_local_idx` 构造query位置，:371取 `context_len=seq_len-query_len`，:402才逐KV tile循环。
- 同目录 `triton_attention_helpers.py`，SHA `59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1`。:179–193在当前causal、无MM/SWA等路径给出 `max_prefix=min(context_len+16*qblock+16,seq_len)` 和 `loop_hi=ceil(max_prefix/64)`。

设同一原prefill已有context C，本次Q个query。原第b个完整query tile的绝对起点为 `C+16b`。如果仅在16query边界拆成新chunk，且新chunk前已完成a个query，则对应tile满足 `a+16b_local=16b`，新context为 `C+a`。所以：

```text
(C+a)+16*b_local = C+16*b
```

对完整tile，新chunk的seq_len至少到该tile结束，helper的min/clamp和原路径得到同一最长可见前缀、同一loop_hi。末尾不完整tile只有原最终尾部，仍按真实seq_len处理。这只证明**已对齐、同query分区的逻辑KV tile范围不因拆chunk次数自然翻倍**；不证明真实HBM流量或时延相同。物理页位置、L2状态、其它请求穿插、launch顺序、metadata和数值编译路径均可能变化。

不对齐边界可能产生额外partial q tile/虚拟CTA；把尾query后移也改变后续chunk，不能把眼前少处理的query当总工作消失。framework owner正在做唯一精确整数tileloop模型，本owner没有重复枚举或运行新测试。

## 对当前调度研究的可执行约束

真实df780 scheduler:432先依 `running` 顺序调度，:468–470以原threshold/budget截断query，:629后处理waiting；修改节奏必须保持真实computed/placeholder/FCFS及原token总量，不能靠A100经验改参数。当前e155/SQL+C3的自然prefix split在guard通过时仍调用两个原forward，decode为C2 3D/reducer、prefill为2D；“与prefill同批”不表示Attention decode零成本。是否实际走guard还需真实命中证据，不能由metadata计划推launch统计。

本实例6CPU是cgroup时间配额，不等于可随意使用暴露的全部CPU；原服务 `FULL_DECODE_ONLY` 也不能被解释成mixed/prefill整个forward已被capture。拆得更细至少可能增加forward/metadata/42层提交与权重重用开销，不能只按ITL缩短判断总吞吐。相反，聚合chunk也可能让decode等待更久。源码约束不足以替代实际服务结果。

因此只建议framework在现有研究中把**总query tile覆盖、真实混合M形状与新增forward次数**一起核算，再决定是否有单一实现值得最短匹配服务门。当前不建议新增参数扫描，不给未测收益百分比；旧growth/terminal/overlap反证和当前KV主线保持原状态。

检索记录：先误开不存在的arXiv v4得到404，随后读到作者v3全文与USENIX正式PDF；本地旧证据文件首次路径误记，改用rg定位后只读真实文件。这些检索失败未触碰运行代码或设备，也没有将二手论坛/镜像用于结论。
