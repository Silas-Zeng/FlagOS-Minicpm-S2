# 固定 tile MLP CTA group8：隔离候选与最短设备门

2026-10-22，hardware_innovation。用户已恢复持续优化，覆盖此前阶段性冻结，并明确小收益也要最短上卡实测、保留结果。本文只记录天数 BI-V150；沐曦－曦云 C500 由队友验证，不外推另一平台或团队总分。

**当前状态：首次173921门的guard失败保留；180033诊断证明旧高级索引oracle在尚未JIT时已读值异常，而七阶段正数basic guard bits全正确未变。正式门已修为basic D2H CPU int16判据并完成互审，待root重新执行两shape；尚无timing或down结果。** 本 owner 无 SSH/GPU 或远端导入；root 是唯一 GPU owner。本候选没有改已安装 FlagGems、已验收 SQL+C3/default 或私有代码库工作树；prefix-mask 后续服务 pair 单独保留，不与 CTA 合并。


## 最新设备失败与最短分阶段诊断

root 已执行 `framework/20261021T173921Z-mm-cta-group-gate`，原 gate 为4b44b930…，原件完整保存在该 run/source，不改写失败。gate-up 的全部输出 int16 bits、finite、inputs、RNG均true，但合并的 `guard_rows_untouched=False`，exit1，正确性阶段立即停止，无计时、未执行down。本owner已实际读本地results/worker.log并核11份source SHA全匹配；两kernel均97 registers、0 spills、65536B shared。root回执完整postflight空闲32700MiB/68MiB/0%，未并发其它设备任务。

不能仅凭原 `storage[[0,-1]]` 的高级索引负index判据区分真实越界与检查问题，原门也没有分开保存两个storage的guard值。固定源码M2048/BM256/grid384的合法store只覆盖out有效2048行；若热调用简单丢失C的storage_offset，最后有效out行应保留NaN而使finite失败，与当前记录不合，但这不是排除真实越界的证明。另一待证伪解释是poison的out.fill_NaN对view偏移或高级index/比较路径有问题，必须定位发生阶段，不能删guard后宣称通过。

180033所用诊断门增加可选 `--guard-diagnostic`（SHA ee263763948421193fc7a323a13ca20e184d7ef074812ac5486f5eee5fe60213），该历史版本normal流程仍保留旧guard判据；policy06c7、两个派生kernel和数学/launch参数未改。诊断仅gate-up、没有timing/down：在full初始化后、各JIT后、各out poison后、各compiled热调用后，分别用正数basic view读取row0和rowlast，完整CPU int16原值保存到guard-bits/*.i16，同时保存原高级索引raw、CPU比较与原GPU predicate、读操作是否改变storage。每行有SHA、异常元素数及头尾原值，另记录C的data_ptr/base_ptr/storage_offset/stride及闭包all_args[2]是否为原out对象。比较所有阶段相对初始化原值的变化，不以期望常量替代原始证据。

诊断完成的status为 `guard_diagnostic_complete_not_a_correctness_pass`，exit0仅表示采集完成，绝不表示候选数学通过。它保留所有guard和旧判据，不修改baseline/candidate内核，不增加扫描。由root在其它作业清理后，沿用下方命令追加 `--guard-diagnostic`，使用新的UTC目录；本owner不执行GPU。当前py_compile/--help通过；root与systems_innovation分别只读审阅ee263增量，均无当前阻断。systems确认正数basic完整CPU int16 bits/SHA才是oracle，旧advanced仅旁证，七阶段、真C指针及无计时边界齐备；未重复suite或GPU。

root已串行执行 `experiments/framework/20261021T180033Z-mm-cta-guard-diagnostic`，18:00:33.650193Z启动、18:00:42.910097Z结束、exit0，前后9031均空闲、可用32700MiB。本owner实读原件并核全部source SHA匹配：七阶段、两个storage的first/last basic异常数均0、SHA不变；原advanced在`after_full_initialization`尚无JIT时就已`matches_basic=False`、12288个异常，后续各阶段同样；advanced读取后basic storage未变，compiled C真对象与24576字节offset均正确。只证明该旧高级索引oracle异常，未定位Torch/FlagGems具体责任，不把诊断exit0当正式两shape正确性通过。原4b44失败与ee263诊断原件均保留。

按root授权，正式门现为 `b216a49a02c90234f7cdfc12db990b2759771d5129169a237824fa9cddd12d91`。每shape在初始化、各JIT、各poison、各compiled热调用后与计时后，分别正数basic D2H读取完整CPU int16 bits，要求期望-17 bits全相同且SHA与实际初始化一致；初始化自身也必须全为期望bits。高级索引raw/原GPU predicate仅保留诊断，不决定pass；高级读后再次basic回读须未改storage。所有采集在32call计时窗外，两个shape/C0/kernel/预record ABBA不变。py_compile/--help通过，systems只读终审无阻断、未重跑suite/GPU；root待按原正式命令重跑，不追加`--guard-diagnostic`。

## 证据与固定参数

actual mm 源码来自已验收官方候选 `experiments/official/20261021T092944Z-sql-mixed-official/source/installed/flag_gems/runtime/backend/_iluvatar/ops/mm.py`，SHA256 为 `4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090`。原件也保存在 `analysis/source/mlp-cta-grouping/iluvatar_mm_original.py`。

SQL+C3 的 `database-before/snapshot.sqlite` SHA 为 `dc6a07db6d31ab210aede0ae92dce0378440729e7c91a0183c269111b3c0ad5e`，after 为 `e90b666d97547ef35ebc5e2a01d24d56a5d16a38d49fcb3908ddb7fc62cad342`。用 SQLite `mode=ro&immutable=1` 读取两份快照，best 表 `mm_kernel_7ea0a6df3012d3bc5475d21d5eb156a7-45eed7266d4cc0f7be44aaaa091bc3b1` 的下面两行前后一致；没有把 benchmark rows 当作选中配置。

| 投影 | M / N / K | BM / BN / BK | warps / stages / CTAs | SPLIT_K | grid |
|---|---|---|---|---|---|
| gate-up | 2048 / 12288 / 2048 | 256 / 256 / 32 | 16 / 2 / 1 | 1 | 384 × 1 × 1 |
| down | 2048 / 2048 / 6144 | 256 / 128 / 32 | 8 / 2 / 1 | 1 | 128 × 1 × 1 |

actual 源码 `:113–122` 注释掉 grouped PID 映射，实际 N 索引变化最快；`:234` 虽传 `GROUP_M=8`，原 kernel 并未使用。M2048 有八个 M tile，gate-up/down 的独特 BF16 权重为 48/24 MiB，大于本实例 16 MiB L2；相邻 M tile 复用相同 B tile 有机制依据。A 的 cache 竞争、已有 L2 命中、compute-bound 或实际 CTA 调度都可能抵消收益，不能把请求字节减少当作 HBM 流量或速度保证。

旧 prefill trace 中两投影共 84+84 次、178.705440 ms，仅用于确认真实投影热点；其源码/配置与 SQL 后服务不在同一完整测量 manifest，不能把旧占比、调优 DB 的 p50 或权重比例外推到当前服务。更详细的历史边界见 `analysis/2026-10-21-mlp-cta-grouping-evidence.md`。

一手来源：[Triton matmul 教程](https://triton-lang.org/main/getting-started/tutorials/03-matrix-multiplication.html)说明 program reordering 改善 L2 复用，并使用末组实际高度；[FlagGems v5.3.5 Iluvatar mm](https://github.com/flagos-ai/FlagGems/blob/v5.3.5/src/flag_gems/runtime/backend/_iluvatar/ops/mm.py)可对照注释的映射。只参考机制，不升级依赖、不用教程的其他硬件数值预测本卡。

框架反证也保留：actual `libentry.py` SHA `414e8a3f74e2522e40659e7fccd84e301f4517220837a87af0311f050bbf3025` 的 `:1682` 只在 entry miss 时进入 tuner，`:1742–1777` 热命中直接调用 compiled kernel；没有“每层每次仍重复 SQL”的新证据。框架 owner 正独立研究 metadata 消除工作，未与此处重复。

## 最小实现与数学边界

`biv150_mm_cta_group.py` 全文件 pin 原 mm4c2e，只抽取原 `@triton.jit mm_kernel`，不导入外层 libentry/autotuner/heuristics。Baseline 的 JIT AST 与原函数相同；candidate 只替换 PID 整数块。源版权头保留。

令 R=ceil(M/BM)、C=ceil(N/BN)、W=8C；g=pid//W，u=pid%W，r0=8g，h=min(R-r0,8)。新映射为 `(pid_m,pid_n)=(r0+u%h,u//h)`。最后一组只有 hC 个合法 pid，u 逐一覆盖行列笛卡尔积；不同组行区间不交。必须对局部 u 取模，不能照搬旧注释中直接使用全局 pid 的末组写法。

原 K 循环、load 地址表达式、tl.dot、FP32 accumulator、`fp8_fast_accum=True`、`input_precision=None`、BF16 转换、原 modulo load 与输出 mask 全部不变；SPLIT_K=1 直接 store，没有跨 CTA 浮点归约。固定两种 C0 下 EVEN_K=True，四个 UPGRADE 标志均 False，与原启发式计算一致。

严格只接受上述两种 M2048 投影、同 CUDA device 的 BF16、A stride `(K,1)`、B stride `(1,K)`、out stride `(N,1)`，输入输出 storage 分离，设备名包含 BI-V150 且有 16 个 SM。非匹配输入直接拒绝，不路由其他后端。它是隔离门组件，不是已经安装的通用 mm 替代；服务集成尚未实现。这里只覆盖 M2048，259/952/decode 等不在候选调用范围。

首调使用裸 JIT 编译；计时前保存 compiled handle。热调用完全按受测 Triton 3.6 / actual LibEntry 的接口传入 12 个普通参数和 14 个 constexpr 占位，共 26 参数。固定 launch 参数显式给出，不查 DB、重新 autotune 或扫描配置。计时窗内无首次 JIT/模块载入；每形状记录 compiled hash、registers、spills 和 shared memory，不能只凭配置不变声称编译资源不变。

整数重排不等于已证明 GPU 逐位恒等：编译调度和寄存器分配仍可能变化。因此 CPU 证明不能替代下一设备门。

## 文件身份与已执行 CPU 检查

| 文件 / 派生内容 | SHA256 |
|---|---|
| `patches/framework/biv150_mm_cta_group.py` | `06c7cd9216907886e7d66a81d4fd5d9f78edef9daac2380ca263ce8c1770b8e1` |
| `scripts/remote/validate_mm_cta_group.py` | `b216a49a02c90234f7cdfc12db990b2759771d5129169a237824fa9cddd12d91` |
| 运行时生成 `mm_baseline.py` | `73d5cf8f080fa53ab17023b228d0215fcf71efc6a17ee9b7294e194c38f61faa` |
| 运行时生成 `mm_group8.py` | `30d0f046071fc4cf122d43af0d087259abc082ad10ec36f69b73ad6a22b343ab` |
| `analysis/source/mm-cta-group/cpu-check.json` | `3172fa8087a2ca37a6b9c98c4209780e2155f226b942d23c48e24a807689b5c7` |

一次必要 stdlib 合同已通过：原 baseline JIT AST 相同；group8 将 PID 块逆换后逐字节回 baseline；两份派生源码可 compile；原源码漂移会拒绝；6 个 CPU coverage 用例包含实际 R8、末组 R9/R10/R17、R1，以及 partial M/N，均无遗漏/重复。原始输出保存在上表 JSON。这里只检查 tile 映射，并未扩大设备 scope。两个文件 py_compile、门 `--help` 及 policy pin 对照通过；没有运行 Torch/Triton 设备代码。

systems_innovation 已独立读审 policy06c7 和门草稿，确认配置、末组映射、26 参数热接口、布局、哨兵、RNG、事件和单卡清理无当前阻断。最终门相对草稿只固定 policy pin，并在初次 JIT 之后把有效输出置 NaN，确保下一热调用必须真实写入，不能误用首调结果；systems 已实际读核最终门4b44b930…，确认此两处差异无阻断；未重跑suite或设备工作，可交root串行排门。

## 最短设备门与可执行命令

仅 root 确认设备空闲后执行。控制器复用既有 `framework-device.lock`、9031 双栈及单卡至少 30000 MiB 空闲检查；唯一 child 拥有 CUDA，300 秒 timeout，按自己创建的 process group 清理，保存 pre/postflight、manifest、命令、源码、worker log 和 GPU samples。

Child 只读精确 MiniCPM5-2B config，校验原模型 config SHA `59613157e5357d62bcb121e04cb90f2170b43d789b142380c12c3d4277d95180`，使用合成 BF16 A 与 `[N,K].T` 权重 view，不加载权重、vLLM runner 或服务。实际 installed mm4c2e、libentry414e 与 Triton init `df3092178f70be89b50d22905cedae5bac414cc38677053616fc56802c91af30` 再核一遍并归档；派生源只写新 run/source，不写已安装 FlagGems。

每形状检查完整 int16 输出 bits、有效输出 finite、两侧输出 guard row、整个 A/权重输入不变、CPU/CUDA RNG 不变；初次 JIT 之后先将有效 out 写 NaN，再执行 compiled 热 launcher，验证的是实际热接口。通过后仅两次 warm，预创建并 record 全部四对 timing Event、同步完成惰性初始化，然后一次 32-call ABBA；record/提交/final synchronize 都计入 wall，同时保存 Event 窗口。计时后再核输入、RNG、输出与哨兵。

不增加 tile/shape sweep、profiler、graph capture、整模型准确率或服务测量。成功也只表示两种固定 tile 的合成信号；小/零/负信号均保留，落噪声记未确认，没有百分比淘汰线。发生异常时保存 phase 与 traceback，不把计时基础设施失败等同数学错误。

将两个新文件放入已有远端 scripts 目录后，root 使用自己的 control launcher 保存外层 runner PID/stdout，并执行：

```bash
root=/workspace/experiments/minicpm-s2
stamp=$(date -u +%Y%m%dT%H%M%SZ)
timeout --signal=TERM --kill-after=15s 380s \
  python3 "$root/scripts/validate_mm_cta_group.py" \
  --run-dir "$root/framework/$stamp-mm-cta-group-gate" \
  --policy-path "$root/scripts/biv150_mm_cta_group.py" \
  --mm-source /usr/local/lib/python3.12/site-packages/flag_gems/runtime/backend/_iluvatar/ops/mm.py \
  --model /workspace/MiniCPM5-2B
```

控制器还需要远端既有 `validate_block_table_candidate.py` 和 `monitor_gpu.sh`；会将它们一并归档。所有 source SHA 遍历只处理 regular file，import 生成的 __pycache__ 目录不会破坏 manifest。

| 待 root 填写的设备结果 | 状态 |
|---|---|
| 首次 UTC run ID / control / 所有 source SHA | 173921；原 run 与 control 已本地保存，11份 source SHA 全匹配 |
| 首次 gate-up bits / inputs / RNG / guards | bits、finite、inputs、RNG true；guards false，门失败 |
| gate-up ABBA wall / Event 原始窗口 | 未执行；正确性失败后停止 |
| down bits / inputs / RNG / guards | 未执行；正确性失败后停止 |
| down ABBA wall / Event 原始窗口 | 未执行 |
| 首次 postflight / 是否进入服务短筛 | root 回执完整空闲32700MiB/68MiB/0%；不进入服务短筛 |
| guard 诊断 / 逐阶段原值 | 180033已采集：basic七阶段全正确未变，advanced初始化即异常；诊断exit0不是正式正确性通过 |
| 修正正式门的两shape / 原ABBA | b216已本地准备及互审；待root串行执行 |

## 独立小收益队列：prefix-mask

已有 policy87c6 / generated a6d / gate d3db 的121838设备门两 shape通过，单层 wall下降0.275858%、Event下降0.453959%。用户明确小收益也安排上卡，后续接 SQL+C3 的匹配热端到端 pair，不因小而跳过，也不与 CTA 混合。

拟在隔离 runner 的 SQL→C2→C3 footer 后、graph capture 前安装独立 proxy，维持3D C2回退；create(xb)需每PID独立派生路径及幂等，避免多进程文件冲突。匹配同热 DB/KV、shape、seed，编译预热在测量外且不用同一测量 prompt 预热 prefix cache。采用已有 warm16K32req1024out 最短 pair，实际 selected>0 才算生效；落噪声仍保留未确认。该服务installer/pair尚未实施，新增代码不能继承父基点103/105准确率；有服务信号后由root决定必要最终验证。

已完成的只读安装顺序审计可供下一API直接接续：固定协作库runner SHA `e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1`，`ModelRunnerFL.__init__:481–968`的直接self方法调用仅`_init_device_properties`和`_make_buffer`，没有load/capture；`worker.py:473`先构造runner，`:484`才load_model，`:745`才capture_model。因此可在exact e155的现有SQL/C2/C3 footer后追加独立安装器，包装构造函数，在原init返回后安装代理，先于graph capture。新installer/transformer仍未写，不能把此可行挂点当已经启用。

实施时只复制原policy87c6到隔离plugin package，不修改installed attention54c或现C3 a129；严格核模型BF16/2048/6144/42/16/2、单卡并行、无spec/LoRA/MM/连接器/KVsharing，核原C2对象和SQL→C2→C3顺序。`create`用`xb`写派生源，必须由`BIV150_MASK_SERVICE_ARTIFACTS=<本次run>/mask-artifacts`下每PID唯一目录承载；进程内重复构造只复用自有同一代理，不能再次嵌套。生成源a6d与policy/source hash全部存run，不覆盖固定源码。shutdown或首个真实execute后的轻量标记记录进程PID、selected/fallback计数；不依赖服务TERM时一定运行atexit。

启用证明须区分8-token greedy smoke、dummy/图预热和真实benchmark：原policy只计2D launch selected，partial query block仍可能没有可省tile。建议在真实`execute_model`按原scheduler CPU预算记录**单请求**最大scheduled query≥128且本步selected计数确实增加，打印一次FIRST_REAL_LARGE_SELECTED；不能拿整批token总和≥128或smoke selected当作实际省mask证明。保持原请求顺序、采样/RNG和真实token数，不加每层D2H或同步。

最短服务pair复用`run_framework_screen.py --context-long-screen --seed 721201`的16K/32req/1024out/concurrency64，固定现有原服务参数；不是官方分数。两端各用独立plugin source/run目录与相同热DB快照，归档DB before/after及实际选中C0、KV容量、源SHA、精确命令、token/完成数和每PID启用证据。已有driver仅8-token smoke，不等于新派生kernel和真实形状已热；需在测量外用不同seed预热同形状，并确认没有共享测量prompt prefix-cache。该小收益有真实层门信号，用户要求继续上卡；服务结果小或噪声也保存，不以未确认百分比删除候选，不与CTA新实现混合。
