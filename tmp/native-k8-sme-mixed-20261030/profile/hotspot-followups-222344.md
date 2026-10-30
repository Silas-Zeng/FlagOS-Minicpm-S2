# Mixed 暖态热点解释与后继候选

本次 A profile 在同一 16K/1024/128/seed0 请求前先做一轮无 profiler 预热，再采一轮；它只用于诊断实际路径，不是性能资格测量。Mixed bridge 对每个符合条件的 eager forward 都再次做身份/shape/layout检查。源码中该次调用约有 18 次 bounds 检查（Mixed 层 9、Native decode 层 9）和 35 次 backing-storage overlap 检查（Mixed 层 11、producer 层 24）。按当前 `storage()` 实现，overlap 两端各读一次 storage，合计约 88 次 `storage(t)` 访问/次 Mixed producer；这些检查逐次验证新张量与别名关系，属于实际 host 路径，不能跨层或跨请求缓存。`scratch_metadata` 可复用计划中的 scratch allocation，但仍检查已有张量身份/布局。Mixed bridge 明确拒绝 CUDA Graph capture，因此这些 Python 检查不会在 Graph replay 中重复执行；纯 decode Graph 路径则不进入此 Mixed forward。

Profile analyzer 能将 worker 的 prefill/decode step 区间与 ixsys GPU event 相交，分别统计 Graph span、Graph 外 kernel、memcpy/memset、GPU 未覆盖区间，并按 kernel 名/launch metadata 聚类。Graph 事件是 opaque span，不能还原其内部每个 kernel；Graph 外的 Mixed eager 工作可落入相应 phase 的非 Graph kernel 集合，但 first-selection 是主机 marker，不能单凭它把任一 GPU event 精确归给某层或某个请求。Prefill GEMM 可按已记录的 kernel 名和 launch cluster 观察，不能从 grid/block 反推出线性层 M/N/K。Host phase/API elapsed 包含等待 GPU，不能当作纯 CPU 耗时；GPU 空隙也不能直接归因到上述校验或调度。

现有证据只能说明局部与端到端口径不同：Mixed N30/S4 组件 producer+原 reducer Event 观察省 7.7811%、wall 省 7.4730%；官方 16K A/B 首暖观察 −0.087435%，且 KV 页数和末态调优 DB 不同，不能作严格因果比较。热点占整轮比例、Graph/非 Graph 工作比例和 host gaps 仍需从这次暖态 trace 看；不能把局部改善直接外推成整轮收益，也不能把小幅官方差异说成 Mixed 回退。

后继仅保留两项由 trace 决定的候选：

1. 若暖态 trace 显示 Mixed eager 期间有明显 GPU 空隙，再评估本地 `native-k8-storage-snapshot` 的单次 forward 局部 storage 元数据复用；它保留每次调用的 bounds/alias 检查，现有真实 Torch CPU helper 中位数约省 33.47%，尚无 GPU 服务收益。PR121 是 Runtime metadata JSON key 索引，不改这些 storage/alias 访问，两者不重复；需要先核其 main/接线前提。
2. 若非 Graph 的 NativeK8 Mixed kernel 本身占据可观 GPU 时间，再据 kernel 名及 launch cluster 选一个内核数据搬运/流水点做最小组件对照；若热点集中在 prefill GEMM 或 opaque decode Graph，则转向相应热点，不以 Mixed 的局部 7.78% 作为立项理由。

PR123 是 multi2 prefill 的 invariant Q 共享内存前移，PR124 是 raw I8 Q32 `num_stages=2` compile scout；均不是本次 NativeK8 Mixed host 校验或 K-lookahead SME kernel 的同一改动，不应重复实现。它们是否改变本次服务的热点占比只能由 trace 证明。当前不对准确率、端到端收益或稳定性作结论。

### 222344 暖态 trace 增量

本窗口确认 `kernel_cjj_konly_q32` 是最大非 Graph GPU 热点：38,682 次合计 201.460s（占所汇总 kernel GPU 时间 55.10%），其中 37,566 次、192.325s 与 worker 的 Mixed phase 相交。主簇 launch metadata 为 grid 64×2、block 1024、135 registers、104 SRFs、57,344B 动态 shared；另有少量同名事件位于 worker scope 外。服务日志首次 INSTALL/选择 marker 记录 profile 的 Q32 参数（2048 query rows/1 sequence、implementation SHA `57cd7870…`、`block_m=256`、`block_q=32`、16 warps、1 stage、tile64，Q32 hoist关闭）；该首次 marker可说明profile/prefill配置，未与Mixed主簇逐次launch绑定。Mixed 64×2主簇的实际Q length仍未知，不能由grid推断。Native Mixed SME producer另有23,142个非 Graph事件，合计15.565s；因此组件局部收益与Q32主热点不是同一成本项。

诊断 wrapper 返回1是 posthoc 返回1；profile、collector、analyzer均返回0，128请求成功、无scope错误。posthoc的失败来自旧 PR105 规则无法解析本次 `overlap_v=true` 安装marker，并等待本路径不产出的旧 selected-ABI/stack receipts；它限制旧资格报告，不否定本次trace或benchmark。active window retained为494.888s，profile envelope retained为495.499s；GPU union覆盖98.96%是相对active window，未覆盖5.140s；CPU storage快照最多直接针对Mixed host校验，Q32的201.460s是GPU时间，不能折算为CPU节省。CPU/API scope包含GPU等待，未覆盖区间也未被证据归因到storage校验；当前只能保留为候选，不能据此声称能改善端到端。


