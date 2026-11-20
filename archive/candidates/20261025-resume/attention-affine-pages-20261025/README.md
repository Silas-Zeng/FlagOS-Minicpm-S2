# 现存连续页区间的仿射寻址组件

2026-10-25，**仅 CPU 准备通过，等待 root 审阅；未编译候选、未上卡、未接服务**。固定 main `0bf9d2efeaa10144dd7f0ff4597298df029f9328`（526 文件）。来源动机和去重边界见 [现有手记](../../docs/agent-work/hardware_innovation.md)，不重复社区调研。

实际产物检查收窄了省量：[旧 Q-hoist ASM](../../experiments/framework/20261022T135941Z-q-fragment-hoist-gate/source/candidate.asm.txt) 的 `BB0_38` 循环在 2056/2105/2155/2205 行各有一条 `ml_lsa_load_dword ... ca`，读四个物理页号；随后 `sl_wait vmcnt(0)` 和 `ml_mov_v2s_b32` 转 scalar，再形成 K 地址。V 复用 `s43/s45/s55/s80`，没有另读四次。TTGIR 两种分布布局、LLVM 16 个 load 已被后端去重成四个 uniform 访问，不能按 lane 数、LLVM 条数或 64 个 token 计 HBM 交易。缓存命中率、wait 的实际耗时未知，且 wait 可能同时等待此前 K load。此产物是旧真实门的证据，不是新候选或当前主线性能。

[component.patch](component.patch) 相对当前正常化数学只增加一个 descriptor 参数、循环外三个 int32 读，以及循环内 uniform 区间判断。整 TILE64 的四个 page16 都落在 `[lo,hi)` 时，以 `base + logical_page - lo` 代替页表读取，跨界/尾部/碎片照旧；没有省 KV 字节、dot、softmax、CTA 或 KV writer。潜在收益是四条 cached load→地址依赖；代价是每 CTA 三个描述符值常驻、比较/分支/phi、CPU 计划和 H2D。旧资源为 VGPR114/SGPR104/private0，新增 descriptor 可能抬资源档位，不能先断言成本很小。

`prototype.py` 生成完整真实 kernel，保留 main 的 `L=0`；其精确逆变换证明浮点路径、mask、循环边界没有顺带改动。两臂**还必须**复用当前 `biv150_q_fragment_service.py` 的私有 JIT 编译/`transform_ir` 与 `lowered_proof`，生成后确认 Q local_load 在循环外。这里没有另写 Q-hoist，也没有把未编译的函数叫作当前受测核。`instantiate` 仅为未来组件提供原模块 helper namespace，不触碰已安装 binding。`.kernel.py` 是可审阅函数片段，不能直接运行。

CPU `plan` 每次绑定请求顺序、当前 P（query length）、KV 长度、每行有效物理页数组和 batch epoch，只从当前 CPU 页表镜像找最长 +1 区间，P=1 置空。`matches` 是组件断言，避免换页/重排/恢复时沿用旧描述符；不作为每层热路径实现。页表容量、stride、padding 保留原样，不能用有效页数组替换 GPU 页表，否则原核末 TILE 的无 mask 页表读会越界。descriptor 不能与页表不同步上传，也不能在旧 kernel 未完成时覆盖。生产生命周期/图 replay 尚未实现；不改 allocator、不重排页、不搬 KV、不从 GPU 读回做计划。

下一次最短组件门：

1. 使用 main526 当前 CPU 页表快照及实际 P2019/M2048，KV4K/16K、原 stride；若现存完整 TILE 命中覆盖很低就停，不先改 allocator 补覆盖。先在一组高覆盖页表 compile 两臂，固定 BM128/T64/w8/s1、BF16/H128/q16/kv2/causal/2D。对 fallback 分支检查四次 cached page load；对 affine 分支检查这些依赖确实消失，并核 Q-hoist 保留、无新增 spill/大 scratch。若编译把两臂变为 select 并无条件保留页表 load，直接否决。
2. 复用现有 component 门的 strict output bits、KV/guard/RNG 检查；只增加整连续、单大段加碎片、跨段/尾页、下一次输入修改页表/请求顺序四种地址边界。比较的是当前正常化＋Q-hoist 与同数学新寻址，保持原 KV writer 和 3D decode 路径。源码生成通过不是设备正确性证明。
3. 无明显回退才交替计时，保存每轮；内核耗时与描述符计划/复制耗时分列。描述符是每批次一次、42 层共享，不能隐藏准备成本，也不能错误地按每层重算。用 `42 × 单层差额 − 一次 CPU 计划/H2D` 仅作筛选估算，真实服务仍需一次完整路径实测。若只够少量层或图调度不能复用，则按实际复用次数计算。最理想连续页都无可信正向，或新增资源/分支抵消，即停。

CPU 命令：`python -B -X utf8 tmp/attention-affine-pages-20261025/check_cpu.py`。本轮 [cpu-evidence.json](cpu-evidence.json) 为 `CPU_PASS_ONLY`：85 组页表、472784 个有效 token 地址 oracle，通过精确逆回、P/换页/epoch/重排/共享前缀断言；约 0.13 秒。原 IR/ASM 与当前 Q-hoist 源哈希已保存。首次检查误写 Q 行号 347，现已复用 main 的实际源码定位 helper 修正并重跑，无设备影响。

**结论：机制尚未被源码否决，可审最小组件；收益预期下调到消除四次缓存页号依赖，暂不作为大收益主线。** 待完成的是 root 独立审阅、设备编译/数值/成本门和当前页表覆盖证据；无 GPU 后台任务/PID。
