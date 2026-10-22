# 2D Attention 单点 w16

当前干净组合 `6f918ae6` 的自然 mixed 原生轨迹 114435 显示 2D Attention 占可见 kernel 累计耗时 60.2339%。历史 a4 的 17 配置没有 BM128/T64/s1/w16，因此只测试当前 w8→w16；不改变 Triton 数学、tile、K 遍历、C2 3D 或 reducer。

- runtime：`biv150_prefill_w16.py`，SHA `c27a4da71feae630252c46a1cc310fed9fc6d26b2dd00783459c206dce27463d`。
- gate：`validate_prefill_w16.py`，SHA `279424148f3837e300646e6006d7cf2a300d19e7c198d138d8a8a418954a67b3`。
- root 编写 `launch_prefill_w16_gate.sh`，传干净 100830 组合 source；本 owner 不运行远端或设备。

唯一 D1/P2047/KV16K 是真实 query 组成对应的长 KV 上界 fixture；native 窗口没有记录每层实际 seq_len，不能称精确上下文重放。复用原 realBuilder/Impl/writer、随机物理页/共享旧 prefix/负 slot、整 output bitwise/finite/padding/KV/RNG、非 1 scale 与原输出 scale 错误、新 Q/out 指针及非默认流。严格 bitwise 未过即停 timing，同时记录 max_abs/max_rel/NaN/allclose；这不是模型 accuracy 的最终结论，未自行放宽容差。编译/launch 资源失败保存 traceback，不尝试换配置；实际 compiled metadata/regs/spills 在成功返回后记录。

只在上述门通过后做 P2047 的 32-call ABBA，预 record Event、窗口外 v1 cpu.stat，wall/event 与 submit CPU 分开。无模型、服务或 accuracy 结论。runtime 默认关闭，不改安装文件。

唯一新增 CPU launch stub 合同 `check_launch_cpu.py` 首次通过：仅 kwargs 8→16、fresh pointers、3D/其余条件不变、调用者 kwargs 不变、原 compile error 对象/context 恰一次、恢复 binding。`cpu-check.json` 是 CPU 假元信息证明，不是 GPU 资源或数学证明。framework_innovation 最终只读审 c27a/279424 无当前短门阻断，未重复执行合同或设备。

## 120226 真实单点结果：负结果，停止此路线

root 唯一 owner 回执：`20261022T120226Z-prefill-w16-gate` exit0，严格 bitwise/finite/padding/整 KV/RNG/scale/新指针/非默认流及原全局还原全部通过；selected68/fallback0/原3D68。32-call ABBA 中位 wall 11.08956495→14.60591725ms，慢31.7087%；Event 10.98337078→14.49728155ms，慢31.9930%。w16 实际 compiled regs101/spills0/shared65536/warp64。正确性通过不等于有收益；w16 及进一步 tile 扫描停止，不接服务、不扩大 accuracy。本 owner 在完整归档下载前按 root 原始回执记录，不冒称另跑或独立重验原件。

下一阶段只保一条删工作设计：原6f在整个模型返回后 :4445/:4451才按 logits_indices 取 N 行。在没有 prompt-logprobs/spec/未知feature 的精确子集，若真实模型末层能在全M行K/V写cache后仅算N行Q/Attention/O/MLP/norm，可删最终未被使用的末层hidden行；前41层和末层全部K/V不能删。当前N2/M2048提供机会，但最高约一层/42，且尚未证明模型接点、metadata重建、residual与返回顺序/随机抽样的完整等价；这里只设计，不实现、不排设备。
