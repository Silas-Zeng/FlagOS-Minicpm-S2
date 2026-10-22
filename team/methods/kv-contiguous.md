<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# KV 连续页复制

连续页合并提交工具；提交不是完成ACK，工具与服务协议分开看。

相关代码：[biv150_kv_page_copy.py](../../patches/framework/biv150_kv_page_copy.py)。

相关方法PR：[连续页KV工具 #3](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/3)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T191017Z-kv-page-copy-gate](../runs/bi-v150/20261021T191017Z-kv-page-copy-gate.md)（登记#91）：遮蔽stdlib copy触发dataclasses循环，尚未import torch/初始化复制 **是否保留：** 未集成；失败或无收益记录保留。
- [20261021T191545Z-kv-page-copy-gate](../runs/bi-v150/20261021T191545Z-kv-page-copy-gate.md)（登记#93）：失败保留，详independent-gate-review.json和analysis/2026-10-22-kv-page-copy-result.json **是否保留：** 待确认；通过某项检查不自动等于优化保留。
