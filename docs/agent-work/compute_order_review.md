# compute-order 增量互审

2026-10-23，CPU-only。只写 `tmp/compute-order-review/` 与本交接，不 SSH、不上卡、不改作者或已测源码。

已读实际 cc442 runner、51f63275 dispatcher、页表实现及 0e961 metadata helper。等待作者冻结的最小补丁，重点只核新风险：计算序 P 必须覆盖页表/slot/seq/query 与 positions，原 optimistic/discard/prev_positions/请求和采样行保持原序；私有 pinned staging 仍受原 `synchronize_input_prep` 事件保护；下一未选中步骤完整 commit 必须覆盖上次 P 表；mixed NONE/no-padding 必须在第一次写前成立，不能先写后 fallback；部分 prefill 仍占原 N 个采样行，不减少 RNG draw。

新增短 CPU 门 `tmp/compute-order-review/check_async_input_contract.py` 已准备、**尚未执行**：从 actual runner 提取真实 `_prepare_input_ids` AST，使用最小 NumPy/Tensor 替身验证非单调 end 与异步前次行重排、新请求及旧 identity slice。候选函数需 AST 完全相同。它只检接线依赖合同，不能证明 Attention、fused helper、CUDA 次序、数值或性能。作者仅做语法/精确逆回，不重复本门。
