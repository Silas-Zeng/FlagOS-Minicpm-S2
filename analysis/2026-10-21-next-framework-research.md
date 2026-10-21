# SQL 修复后的框架机会与缓存复现边界

2026-10-21。仅本地 CPU、原始日志/源码和一手网络资料；没有 SSH、GPU 操作或修改其他 owner 的候选。已读 CURRENT_WORK 及现有 decode-gap、SQL、硬件、mixed、GEMM、hidden-view 研究。

## 先重置收益基数

本地 SQL 首轮 `20261021T064632Z-sql-reflection-screen` 已完成：64请求全部成功，4096输入/128输出、合计262144/8192 tokens，duration **43.198655秒**，输出189.6355 tok/s，median ITL129.494ms，p99 ITL471.718ms。相同源、参数、seed、KV521840tokens的重复 `20261021T072153Z-sql-reflection-screen` 也已完成，为 **43.090572秒**、median ITL124.503668ms。matched B0 `20261021T071554Z-b0-sql-pair` 为 **120.471475秒**、同KV。两次 SQL 相近，构成很大的重复短测信号；B0仍仅一次、旧pair未快照DB初态，**不是官方分数或新accuracy通过**。

随后 SQL+C2 `20261021T073309Z-sql-decode-screen` 一次短筛选完成，为41.154068秒、64/0成功/失败；KV为521936，比SQL-only多96tokens，不能把全部差值归因于C2。该run的DB前后manifest均479表/17982行，schema与逻辑内容指纹相同。组合源的Level3 accuracy `20261021T073644Z-sql-decode-level3` 已启动，本文没有其结果。原始结果与边界见[框架实验记录](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-framework-experiments.md:175>)。

旧8步profile的13.9476秒、SQL get_config13.405秒是修复前的嵌套诊断时间。不能把它继续当新基线预算。SQL后服务日志中prefill仍持续约35秒，mean TTFT20.837秒，只比旧约22.9秒下降一小部分；主要消失的是请求退出时的decode长尾。prefill/mixed的实际成本因此应重新进入主线。

## 一手资料进一步限定了可行方案

| 证据 | 本项目结论与边界 |
|---|---|
| [FlagTree Iluvatar compiler](https://github.com/flagos-ai/FlagTree/blob/main/third_party/iluvatar/backend/compiler.py) 明确capability71→ivcore11、warp64、默认4warps/3stages。 | 本机编译cache已证实同一默认。框架改变批次组成会改变attention分支/launch资源；不能把NVIDIA sm71特性表用于推导TMA、PDL或外部event支持。公开main只作机制资料，不升级。 |
| [插件Iluvatar graph支持PR #232](https://github.com/flagos-ai/vllm-plugin-FL/pull/232) 于2026-06-25合并，作者验证Qwen并采用FULL_DECODE_ONLY，提醒默认图设置可能OOM。 | 说明CoreX图能力真实存在，亦有内存限制；没有证明本项目混合图或任意CUDA API都兼容。本项目external timing event小门已失败，不重复套nsys/新event参数。 |
| [vLLM v0.24图设计](https://github.com/vllm-project/vllm/blob/v0.24.0/docs/design/cuda_graphs.md) 区分uniform decode与mixed；FULL_DECODE_ONLY令后者不进入图。 | 当前参数已经优化decode图，但prefill/mixed仍有边界机会。不能把“开启CUDA graph”重复当新工作；也不直接改官方启动配置试FULL_AND_PIECEWISE。 |
| [插件GraphWrapper](https://github.com/flagos-ai/vllm-plugin-FL/blob/main/vllm_fl/compilation/graph.py)按ForwardContext模式和BatchDescriptor分派并使用global graph pool；[PR #381](https://github.com/flagos-ai/vllm-plugin-FL/pull/381)补入KV分配前的图内存估计。 | 本地保留source中这两点已经存在，不再提“改用共享pool/补图内存计算”作为全新实现。需要的是度量真实占用和改善具体生命周期。 |
| [Deep-Spark设备插件](https://github.com/Deep-Spark/ix-device-plugin#split-gpu-board-to-multiple-gpu-devices)明确BI-V150板有两个芯片可拆成两个device。 | 本实例单device32GiB/16SM不等于64GiB全板；研究并行、KV容量和带宽均按实际可见资源。没有第二device，不走跨die分离服务。 |

## 按当前落地价值排序

### 1. 在 SQL 新基线上复核已有 shape-aware attention 执行边界

这是新收益基数下最便宜、最有设备机制证据的一步；不是再次从头扫描attention参数。**SQL+w2s1的一次组合短测已完成，独立accuracy正在执行**；后续若要量化C2独立收益，仍须同源/同KV、同负载pair，再根据混合步占比决定是否加天然prefix split。既有w2s1只改3D编译launch，五类gate和图微测已逐位相同；mixed split保持整批GEMM和KV更新，只改变attention请求分组，仍有2D→3D归约精度风险。

旧C2/C3端到端结果受SQL秒级主机停顿遮蔽，不能由旧1–3%差值推导新pair上限；也不能把单层40%延迟下降说成模型快40%。估值应为 `新基线该路径的关键路径占比 × 局部下降比例`。例如attention若占整任务25%、局部下降40%，总时长减少约10%只是条件预算。官方128/256请求、1024输出与短测64请求128输出的相位比例不同。

**最短反证：** SQL后相同数值/安装门通过，而服务walltime/ITL无可辨信号；或mixed命中很少。此时保留已验候选，不扩大成warp/tile穷举。先C2再C3可避免一次叠三项无法归因。

### 2. 新研究方向：只对暴露的 prefill/mixed 计算段复用图

SQL后约43秒负载中，输入阶段仍约35秒。模型已有piecewise编译，在attention/KV-update opaque ops处分界；可以研究 **稳定token bucket的非attention编译段**，用持久input/output地址复用图，attention及动态元数据保持eager。按实际token总数与运行语义选择bucket，不按并发64或固定4K/16K识别benchmark，不把整个模型拆成两次forward，不捕获随机采样。

这需要提交具体wrapper/持久buffer实现；单纯将配置改成现有FULL_AND_PIECEWISE不作为实现方案。先核对本地GraphWrapper和编译partition接口，再从一个常见token bucket的一段开始。图内数学、kernel选择和算术顺序保持原样，短真实输入须bitwise比较、多次replay确认新输入、检查alias/stream及峰值内存。[PyTorch2.10图内存约束](https://docs.pytorch.org/docs/2.10/notes/cuda.html#graph-memory-management)要求长期持有捕获地址；共享pool还要求安全的执行顺序，不能并发重放会覆盖彼此输出的图。

**目前信心低于第1项。** 旧prefill的稀疏GPU样本大多94–100%，反对把它先验判成CPU launch bound；large-M GEMM/attention可能已经是设备主体。最短诊断只覆盖SQL后的2–3个mixed步骤，记录wall/threadCPU与native GPU时间；mixed不进整图，原生profiler有机会直接看到内部kernel而非只有graph壳。如果设备连续满载、CPU提交无空洞或图开销只有极少比例，这条停止，转去已准备的图内GEMM真实形状研究。不能为强求“框架大收益”隐去该反证。

### 3. 仅对16K成立的后备：生命周期减显存，而非按评测裁图

当前32GiB限制使16K约30–31请求驻留。可研究GraphWrapper的output强引用、编译段workspace与临时profiling graph的生命周期，核对估计与实际pool占用；先找不再需要却仍活着的buffer，保持原capture覆盖与官方gpu-memory-utilization。不能按并发64砍更大图，不能拿已有globalpool改名当新优化。

后续[内存可行性审计](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-memory-lifecycle-feasibility.md>)已将此项降为测量候选：global pool、由大到小capture与临时状态清理均已存在；表面weak-ref在本插件可能落到identity fallback，但35个最终输出的数据仅约16.53MiB。现有日志尚未证明可回收超过1GiB；Iluvatar跳过graph估计的sizing分支，也意味着少占graph显存不自动增加KV容量。下一步先做一次完整阶段账本，不直接实现“释放图输出”的方案。

BF16 KV每token42KiB：一条16K输入约672MiB；一条输入加1024输出约714MiB。以当前521840token容量，32条完整17408token请求需557056tokens，缺35216tokens，即约**1444MiB**。这只是容量量级，不保证调度恰好32驻留；动态分配、prefix共享和输出长度都会改变轨迹。省几十MiB无法宣称跨过满长度并发门槛。若看不到数百MiB至GiB级真实可回收buffer，降为小候选，不占主线。

**最短反证：** 生命周期账本显示pool已经充分共享、临时图确实释放，或新增图反而减少KV导致16K排队/重计算增加。官方4K/16K需分别看队列和吞吐，不用4K单档收益推断16K。

## 为什么不继续优先微调缓存、线程或采样

actual `libentry.py:986/1043` 的 `key in cache` 后 `cache[key]`确实重复查询；[固定FlagGems revision源码](https://github.com/flagos-ai/FlagGems/blob/4df52d9168ac55c1c1061cefb4638c570292d896/src/flag_gems/utils/libentry.py)亦可核对。但按表反射已大幅收窄ORM范围，不能把旧2.620秒Session.get或479个mapper带来的query编译成本直接外推。只有新profile仍显示它是较大占比才做一次lookup复用；不先加永久正/负缓存改变外部调优DB的可见性。

异步调度已经开；`synchronize_input_prep`的event保护复用pinned CPU staging，不能删除等待制造竞态。没有新残余CPU证据就不扫描6核线程设置，不重开已负面的sampler compile，也不把hidden prefix view、约70us页表H2D或intcopy当下一项必然大收益。它们保留为经验证的局部候选，端到端需新基线证明。

## 调优数据库：必须纳入复现指纹

actual `libentry.LibCache.__init__:284`：默认路径为 `config_cache_dir()/TunedConfig_{vendor}_triton_{major}_{minor}.db`。actual `code_cache.py`先读FLAGGEMS_CACHE_DIR，否则Path.home()/.flaggems，再加config_cache；FLAGGEMS_DB_URL可覆盖整个URL。最可靠路径是**已加载服务进程**只读的 `libentry.libcache.model.engine.url.database`，不是另起导入FlagGems的进程猜测。非SQLite不输出可能含账号的原始URL，转用脱敏driver/database身份。

061506观测每次约479个表被映射。它是这个暖持久DB的条件，形状/源码/config协议增多会增加表；不能宣称空库、新镜像或另一个缓存规模都有相同2.8倍收益。cold进程、warm二进制、warm调优行、warm进程model pool是不同状态；当前性能pair共享持久DB，其状态需留档，不删除库、不强制重新调优来制造对照。

最小只读工具已实现 `scripts/remote/snapshot_tuning_db.py`：

```text
python snapshot_tuning_db.py --database <actual SQLite path> --output <new run/db-before>
```

在计时区外、负载前与worker退出后各一次。源使用URI mode=ro和query_only，通过标准backup写新目录的snapshot.sqlite，然后只在副本计算完整文件SHA、排序sqlite_schema(type/name/tbl_name/sql)SHA、全部表名/数量、每表columns/PK、rowcount及内容SHA。内容按integer十进制/real.float.hex/text/blob.hex/null分型后排序，保留重复行；schema哈希不含物理rootpage。保留副本本身才能重放同一配置状态。每表内容排序使用最大单表大小的内存，适用于此类小型调优表。

SQLite官方 [backup API](https://sqlite.org/backup.html)支持一致快照；[Python3.12接口](https://docs.python.org/3.12/library/sqlite3.html#sqlite3.Connection.backup)提供标准实现。不能仅hash主.db而忽略WAL；[data_version](https://sqlite.org/pragma.html#pragma_data_version)只适合同一connection前后检测，不是跨run全局数据库版本。[sqlite_schema定义](https://sqlite.org/schematab.html)是schema对象指纹依据。工具不checkpoint、不VACUUM、不改原库，不导入FG/读取环境；临时WAL、引号表名、blob/null/float、源.db与WAL字节不变、拒绝重复输出的小型CPU检查已通过。SHA256 `0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2`。

下一轮有效结论须同时说明模型/源码/官方参数、KV容量、图覆盖、调优DB前后状态和是否包含profile。所有设备验证仍由唯一owner串行完成。
