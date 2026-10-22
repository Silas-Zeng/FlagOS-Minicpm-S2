# 当前版本由哪些优化组成

核对时间：2026-10-22。框架私有仓库当前主分支为 `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c`，完整 tree 为 `82e37f8f263eeb09563a4790359ec95a0de1ca17`，对应本地 `70d04f38382e900949ddeb34d2ac75aacdc93af4`。

这是一次性导入的已验证组合版本，此前没有把以下各项分别建 PR 后逐个合并。组合中已有多个优化方法，后续协作按方法拆分 PR；不重写主分支历史来补造已经发生过的 PR 流程。

| 已有组成 | 代码入口 | 当前范围 |
|---|---|---|
| 保留的 prefill 路径 | `vllm_fl/patches/biv150_runtime.py` | 已包含于完整 SQL+C3 候选 |
| 确定性 top-p 实现 | `vllm_fl/patches/biv150_top_p_triton.py` | 已包含于完整候选 |
| SQLite 目标表反射 | `vllm_fl/patches/biv150_sql_reflection.py` | 减少重复反射工作，已包含于完整候选 |
| 3D decode launch | `vllm_fl/patches/biv150_decode_launch_runtime.py` | 已包含于完整候选 |
| mixed Attention 分流 | `vllm_fl/patches/biv150_mixed_decode.py` | 已包含于完整候选 |

整体补丁 SHA256 为 `4aba147aa0bd3ec8dd1c12b6ae94bf39537a4cbad449e68e2fcdbfbdc0f8def6`，基于比赛插件 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`。官方准确率103/105和完整官方吞吐对应这一历史组合；不能将它们自动分配给后续的新方法或新组合。

后续的 CPU metadata 复用、async token update、KV 连续页复制、二维 SAVE 复制属于本轮分开整理的草稿 PR。完整 KV 保存恢复事务和两种无收益的 blocking Event 实验仍在实验记录库中保留，不能说主分支已启用它们。FlagGems 仍为固定版本代码与中文协作首页，本轮没有新的算子源码改动。

分开提 PR 有利于审阅、定位回归和撤回单一方法，但“Git 能自动合并”不等于“组合运行已验证”。涉及同一个 runner 的两项须检查合并后的实际差异；每项各自通过的设备证据不能替代组合的验证。具体 PR、冲突处理、合并顺序及剩余验证见[方法协作安排](pr-collaboration-plan.md)。
