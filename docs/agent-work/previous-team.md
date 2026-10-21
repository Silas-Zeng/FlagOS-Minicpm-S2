# 上一组子智能体工作接续

整理时间：2026-10-21 10:06 UTC。以下按已落盘产物和父任务收到的最终结果整理，不将无法核实的聊天细节当原始证据。

## `/root/framework_review`：框架与端到端

- 初期源码与框架路线：[framework-review](../../analysis/2026-10-21-framework-review.md)、[large-gain-framework](../../analysis/2026-10-21-large-gain-framework.md)、[decode-gap-framework](../../analysis/2026-10-21-decode-gap-framework.md)。
- 独立 mixed 实现 `patches/framework/biv150_mixed_decode.py`（SHA a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42）及交叉审阅；纯 decode 不变，mixed 2D→3D 有归约数值变化，必须独立准确率门。
- SQL/C2/mixed 三项联合交付 delta：`patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode.patch`，SHA4b3e2e52b01d04a0f0477ae4e9b8dc3fed3c1f721360af3bbe6b01014572bbba。直接接 retained performance.patch，不先叠两项 joint。模块和 runner 精确等于080656源。
- 已完成 accuracy/screen/official owned runner 和 launcher 的编写；另一 owner/root 审阅后使用。当前 official driver SHA79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579，launcher SHAa4fac213238e13ecb9ef78af9b7cfc419efce90308c0a04c9583c6172cac78c8。
- 已否定/降级的框架方向：[prefill-graph-feasibility](../../analysis/2026-10-21-prefill-graph-feasibility.md)、[memory-lifecycle-feasibility](../../analysis/2026-10-21-memory-lifecycle-feasibility.md)。已有 prefill Inductor 编译/global graph pool 等不能重复当全新优化；未证明 GiB 级可回收空间。
- 下一候选仅完成源码审阅：[mixed-token-bucket-source-review](../../analysis/2026-10-21-mixed-token-bucket-source-review.md)，SHA4f96dead654da2f5bc93c8fb02e746b4cafae45fca55ed9bc3ec7c1c4d83d1c5。真实 Attention M/采样 N 不变，补合法 input ID 尾，借现有 positions0/slot-1；Attention output 尾未初始化、MM 配置/数值/峰值风险未设备验证。
- 最终交付状态：mixed 独立准确率103/105通过，默认performance.patch未覆盖，正式吞吐仍在途；已更新 `docs/candidate-usage.md`。

## `/root/biv150_hardware`：硬件、KV与代码独立审阅

- 一手资料及硬件分析：[hardware-research-v2](../../analysis/2026-10-21-hardware-research-v2.md)、[large-gain-hardware](../../analysis/2026-10-21-large-gain-hardware.md)、[gemm-launch-research](../../analysis/2026-10-21-gemm-launch-research.md)、[decode-gap-hardware](../../analysis/2026-10-21-decode-gap-hardware.md)。BI-V150 不是 Ascend NPU，不套用 Ascend 架构/API技能。
- 参与 C2 launch-only 候选/独立审阅，严格 BF16 MiniCPM 3D decode guard；五类设备输出 gate bitwise。端到端结果以 root 实验记录为准，不将单层约40%当整模型收益。
- async-token 整数 gather→scatter 融合有真实方法12类 GPU gate；尚未做服务吞吐/accuracy，不默认叠加。相关实现 `patches/framework/biv150_async_token_update.py`，SHA1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc。
- 读真实 SQLite 副本证明：083031 新增四投影 MM M=952，084659 M=259，各四个best配置及60条benchmark记录；新 index 是 BF16→BF16，更像 hidden_states[logits_indices]，不能归给 int32 token update，也不是168次独立调优。
- [mixed-token-bucket-plan](../../analysis/2026-10-21-mixed-token-bucket-plan.md)，SHAad5ffe15663acb267b4035939b5a49c2b49dd69a42a4a21835d127f3b475af79。通用128倍上取整有设计价值；旧BM下CTA数可能不增，但新调优配置不保证如此。官方丢首轮可能剔除全部冷收益；暖无收益就降级。
- 独立重建三项联合delta模块和runner，精确匹配080656；安装顺序SQL→C2→mixed，无夹带。未修改冻结源码，未拥有设备实验。

## `/root/competition_systems`：规则、复现与实验审计

- 规则/经验：[system-competition-research](../../analysis/2026-10-21-system-competition-research.md)、[next-framework-research](../../analysis/2026-10-21-next-framework-research.md)、`docs/official-verification.md`。
- 所有主张以原raw、source、launch、KV、DB before/after和cleanup审计为准。发现083031/084659后跑候选享用新增调优配置；要求最短warm控制而非清库或整套重跑。
- warm SQL+C2 085855 与 mixed085302 的KV均521840、DB均483表18119行且三类hash一致。mixed约+4.97076%只是单次信号；一次metrics观测preemptions=1不是最终完整计数，也不能说mixed=0。
- 独立审计 SQL+C2 073644：101/105；mixed090505：103/105、105success/0error/105stop/0cap，228归档文件SHA及四核心精确匹配080656。mixed sampling单次103高于101不等于质量提高。
- 修复本地 `scripts/analyze_benchmark.py` 先过滤成功再丢首轮的次序错误；现先按原case顺序丢首轮，报告不足三轮为incomplete，SHAadf1fd59181b4649fd20ff9565faef4d62119121f4ff6c4efeb9872950994c0d。针对性两项轻量检查通过，已有完整CSV数值不变。
- 官方 owned runner 审计原8raw/2summary、每档原第2–4轮成功数/tokens/finite和均值。当前总体对照计划为最终候选 vs 原13eb各一次完整两档四轮；历史只有4K完整且源不同，不当matched整体增益证据。
- 维护 [framework-experiments](../../analysis/2026-10-21-framework-experiments.md)、[registry](../../experiments/registry.csv)、[queue](../../experiments/queue.md)。新 systems owner 接续这些文件；root继续拥有所有 raw 官方测量及设备。

## 接下来不要重复的工作

- 不重跑已通过的SQL+C2准确率来代替mixed独立门；两者已分别有独立结果。
- 不恢复已拒绝的decodeT32低准确率候选，不重复external timing event已失败能力门。
- 不因缺少聊天而重做CPU/GPU gate；先读具体run的原始结果、源哈希及限制。
- 不在官方092944活跃时另开GPU。源码实现可以本地准备，设备验证等唯一owner安排。
