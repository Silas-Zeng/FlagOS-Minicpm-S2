# hardware_innovation 工作记录

## 任务与边界

2026-10-21，由 root 委派：只读本地源码、原始证据及公开一手资料，探索最多两个新的高收益框架方向；独立审查 framework_innovation 将提供的 `biv150_mixed_token_bucket.py`。禁止 SSH、GPU、修改运行代码；允许写本研究文档。当前 GPU 官方吞吐作业由 root 独占，其他智能体不得启动设备任务。

已读 `AGENTS.md`、`CURRENT_WORK.md` 最新至 09:31Z，以及现有 hardware/decode-gap/SQL/bucket/prefill/memory 研究。已确认当前基点为原 SQL+C2+mixed，独立 accuracy 103/105 已过，完整 official 仍运行；不重复旧基线、不把旧 SQL profile 当修复后的残余预算。

## 当前来源

- `experiments/profiles/20261021T061506Z-host-gap/source/libentry.py`：实际安装的 LibEntry/LibTuner 路径，414e8a3f…；原诊断为未修 SQL 基点。
- `experiments/accuracy/20261021T090505Z-sql-mixed-level3/source/installed/flag_gems/utils/models/sql.py`：实际 SQL 模块，6dc19cb5…；运行时由候选替换单表反射。
- `tmp/remote-source/iluvatar_mm.py`：实际 Iluvatar MM 和 M/N/K 调优 key。
- `experiments/accuracy/20261021T090505Z-sql-mixed-level3/source/plugin/vllm_fl/worker/model_runner.py`：实际 runner，attention、动态索引、graph 和 pinned buffer 同步挂点。
- 既有 bucket 设计：`analysis/2026-10-21-mixed-token-bucket-plan.md` 与 `analysis/2026-10-21-mixed-token-bucket-source-review.md`。

## 已确认与反证

1. `ConfigCache.__contains__` 与 `__getitem__` 均发 SQL 查询，LibTuner 正命中分支查询两次；但 LibEntry 命中自己的 `kernel_cache` 后会绕过 LibTuner，不能假设每层每步都在查 SQL。因此“一次 get 去掉全模型热路径 SQL”的大收益主张不成立，除非新证据显示持续 entry miss。
2. SQL `get_sql_model` 创建新表时用 `self.sql_model_pool[name]` 写入，而读取使用 `short_name`，存在首次建表后的 pool key 不一致；下一次可反射并修复缓存。其主要影响是新表冷路径，不应单凭此扩成官方后三轮收益。
3. MM 的 M/N/K 作为 LibEntry 普通标量精确进 key；调优策略与 Entry key 是两层，单独粗化 config key 不会消掉 exact-M 的二进制 dispatch miss，且可能改变配置选择。必须区分新 mixed token bucket 实现与直接篡改 key。

## 未解问题和下一步

- 从公开固定 revision 源码核对可复用的 semantic runtime-argument specialization，严格判断可否不 padding 真实行、不改浮点算法地控制索引动态源码数量。
- 检查是否有模型外的高频 LibEntry Python dispatch 可以安全分离绑定参数计划，且在 official skip1 后仍有稳定价值；只提出有挂点和最短反证的两个方向。
- 等待新 bucket 模块后独立审查，所有意见落盘在本文件及最终研究报告。当前尚未收到代码，尚无代码审查结论。

## 10:09 UTC 研究产物与中间决定

已写 `analysis/2026-10-21-innovation-hardware.md`。只提出两项有源码挂点的条件方案，尚未实现：

1. runner 最终 BF16 hidden gather 使用真实 row-count runtime参数，避免每种完整 input-shape 生成新源码；与已验 int32 sampled-token融合不是同一挂点，可逐位验证、不padding模型。
2. 若另owner bucket证实暖后仍有收益，再研究保持真实 M 的 tile配置分组和动态M投影launch，避免42层额外逐行工作；涉及配置变化/新kernel实现，风险和成本更高，后备。

反证明确记录：SQL已修复；每步一次最终gather不等于旧8步13.95秒SQL预算；官方跳过首轮后冷shape收益可能消失。仅改tuner key不能消Entry exact-M miss，直接伪造传入M会改变bounds/modulo而不正确；必须真正实现 runtime边界。未将任何设想标为默认优化或已测收益。

实际已打开的一手URL：

- https://github.com/flagos-ai/FlagGems/blob/4df52d9168ac55c1c1061cefb4638c570292d896/src/flag_gems/utils/libentry.py
- https://triton-lang.org/main/python-api/generated/triton.jit.html
- https://moark.com/docs/compute/clusters_gpu/iluvatar/iluvatar_BI-V150_gpu
- https://docs.pytorch.org/docs/2.10/notes/cuda.html

固定revision的index/mm GitHub网页两次抓取cache miss；未将其当成功阅读。对这两项结论使用已归档actual本地源，不因网页失败重新SSH取源。现有实际四源码SHA已复算，完整值见研究报告。

已通知 root 研究结论，并向 framework_innovation 请求新bucket完成后提供路径/SHA。GPU仍由root独占，未做任何远端动作。

## 新 bucket 初稿独立审阅

已收到并阅读 `patches/framework/biv150_mixed_token_bucket.py` 初稿及 footer SHA `21074c950f7ebfec73215f8db746f13b6980779277b084cec6c79e27b706e620`；初次全文读取和作者写入发生交错，随后读取的 `d54a1b09684a49d92d933df4122240f294d9ace689853a448806ad29fbf2c1f0` 已含严格footer守卫。尚未收到定稿SHA，不将本段等同最终集成批准。

依次对照 frozen runner e155、backend1219和新持久实际writer `analysis/source/mixed-token-bucket/triton_reshape_and_cache_flash.py` SHA `f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb`：

- ContextVar状态只在真实 `execute_model` 调用期间建立；`finally:reset(token)`在正常/异常/嵌套调用后恢复上一状态。dummy/profile/capture单独调用determine没有授权context。没有删原 managed inference wrapper。
- 原determine先执行；候选只在mode NONE且无uniform/cascade/DP/ubatch等条件修改descriptor.num_tokens；真实scheduler、num_reqs和query_start_loc均不变。
- `execute_model` 的 pad_attn仍仅FULL时true，因此元数据仍以真实M构造；separate KV update只扩大slot mapping到B，原_get_slot_mappings(M:B).fill_(-1)仍执行。actual writer在任何K/V load前对负slot返回。
- 原_preprocess已经清positions尾，候选只补input IDs合法0；执行仍在 `synchronize_input_prep`的原作用域内，原prepare event不会在尾清0之前记录完成，没有新增host全卡sync。
- 最终gather/logits/sampler仍原N行；当前mixed实现形状检查为>=真实M，并按真实M切片，padding不直接关闭split。改GEMM形状仍可能改真实行浮点结果，所以独立准确率必须重新跑。
- 只行内运算的模型结构使未写attention尾部不会数学上进入真实行，但这不是实际compiled/device正确性证明；后继真实最短门须验KV哨兵、logits行数、有效行finite与padding/实际形状，随后实际性能。

已回报作者和root的两项建议：

1. 当前eligibility也含纯prefill尾步：nonuniform在原逻辑中是not uniform-decode，不能把marker/报告写成严格已有decode+prefill混合。应如实写prefill/mixed或明确排除。
2. 最早全文中的 `_require_runner_source`初稿仅hash boundary前，suffix任意内容仍可能通过；建议要求精确安装footer，从而不能通过footer之后改方法却声称exact guard。**已解决**：重读d54版确认 `EXPECTED_FOOTER_SHA256` 和 `raw[len(original):]`精确hash，作者将补扰动拒绝小检查。本owner不修改其代码避免竞争。

初稿未发现正常所限配置下的行为阻断。当前审阅是CPU源码结论；未运行GPU、未证明bitwise/accuracy/性能。

独立运行 `python analysis/source/mixed-token-bucket/check_contract.py`，exit0，七项合同通过：259→384和952→1024、stats、ID/positions尾、正常context恢复，以及uniform/FULL/容量不足/force_eager/out-of-execute回退。此脚本以fake Buffer、固定 `_eligible=True` 验证wrapper，**没有证明真实配置guard或Tensor/KV/RNG**；不冒充实际设备测试。异常/嵌套cleanup已源码审核但当前脚本没有专门覆盖，若作者补最小检查可一起核对，不为此扩测试框架。

## 10:18 UTC 最终独立审阅与交接

复读最终模块 SHA `86b24f729cbb078cdd285e6b5aeccd503df190837e898883434f01915ada999d`。scope 已准确改为 `prefill/mixed NONE`；footer仍为21074c…且完整suffix/冻结前缀都必须匹配。与先前阅读的行为实现一致，两项建议均已处理。

作者轻量检查新增 actual frozen prefix+exact footer通过和两类扰动拒绝；当前 `analysis/source/mixed-token-bucket/check_contract.py` SHA `a3a954d89cc68aeb2f7aecd9d6c20210d7351d6a704cff467c11ef54a2b0dfe1`。本owner再次执行同一命令，**8项全部通过、exit0**。此次复跑有明确理由：填补前一版未覆盖的源码守卫；不继续重复已过检查。

**独立审阅结论：在限定scope及冻结source的前提下，未发现阻断最短真实设备门的问题。** 可以在新隔离source中显式opt-in，不能覆盖当前官方测量源、不能直接选为提交默认。真实M/B gate须验原真实Attention长度、N采样行数、KV哨兵、污染tail隔离、回退/graph replay和显存。改M选择新GEMM配置，故无bitwise/准确率/性能承诺，已有103/105不能继承。

本轮产物仅研究报告和本交接文档。未改其他owner运行代码、未改官方参数、未SSH/GPU、未开第二设备任务。两个新后备方向未实现；当前首要设备工作仍是root持有的官方吞吐，完成并释放后才由root决定最短bucket门与基线先后。最终消息给root的所有要点均已保存于本文及研究报告。

## 后继委派：实际实现 BF16 hidden gather 低风险备选

root 新委派仅本地CPU实现方向一：独立新copy kernel与exact080656两挂点transformer；最必要CPU source合同和无权重GPU gate。不得SSH/GPU、不改冻结source/default/当前官方测量。前文“两个方向未实现”仅描述10:18状态，当前以下新任务继续。

先确认 bucket 最终 `d2620ff750beb3fab97f372d64a1ec0e5550ee133cc6ca33adb8ba3f43de4605` 相对86b24只增加 `and not runner.shared_kv_cache_layers`。actual runner 866初始化dict、7346建立alias；这项排除跨层共享的补强正确，不影响当前空dict，原审阅结论延续到d262。没有为单一guard再重复全部CPU门。

已新增：

- `patches/framework/biv150_hidden_row_gather.py`：Triton BF16 load/store新实现，真实rows/count `do_not_specialize`，固定width2048/w2s1、无调优/浮点运算/RNG/padding。候选helper只接受严格MiniCPM、单卡BF16/pure text/no spec/LoRA等scope，GPU contiguous二维hidden/int32或int64一维indices、device/stride/alignment/storage alias守卫，不匹配返回None。
- `patches/framework/biv150_hidden_row_gather_source.py`：full e155 SHA exact byte transformer，只改变两处`hidden_states[logits_indices]`，unsupported仍在原if/else分支执行原表达式，采样行数和顺序不变。没有把它接入任何远端source/default。
- `analysis/source/hidden-row-gather/check_contract.py`：无torch/vLLM导入，source两挂点/回退逆变换/语法、变动源拒绝，原CPU正query lengths和query_start_loc证明non-spec ends-1合法边界，kernel runtime形状注释校验。
- `scripts/remote/validate_hidden_row_gather.py`：仅准备、未上卡。controller无GPU导入，持同device lock、pre/postflight原ixsmi、唯一GPU child PID/owned process group清理、5分钟界限、source/manifest/原stdout/GPU样本。worker无权重，不启动服务。

索引边界决定：不对GPU indices做`.item()`或D2H同步。精确runner的non-spec `_prepare_inputs`固定由`query_start_loc[1:]-1`生成，helper复核其原CPU正lengths、CPU前缀和与hidden rows上限。此为**特定挂点的来源证明，不是任意GPU index值验证器**。private kernel支持合法负索引/重复/乱序copy，public helper仍仅接受来自该审计挂点的non-spec query ends；不能对外宣传通用index。

CPU命令 `python analysis/source/hidden-row-gather/check_contract.py`通过，stdout已保存同目录cpu-contract.log，transformed runner SHA `e68d6886d788a2f56d470fccaee62558d4622545eede2a59fbeb083a5264016e`。三个新.py的py_compile和gate --help通过。尚未导入运行本地torch/Triton或执行任何GPU。

中间纠错：最初gate草稿误按输出路径/采样间隔传monitor_gpu.sh；查看actual脚本确认参数实际为watch PID/output，已在未运行前改为worker PID+输出，且从归档source启动worker。源检查、清理和观测脚本在source归档，不依赖未记录的临时文件。未产生设备失败或比较结果。

framework_innovation已只读初审runtime/transformer无阻断，提醒必须用int16 bitview验证NaN/signedzero；gate已采用全部BF16 payload的int16 golden，不用torch.equal(BF16 NaN)误判。其最终审阅待文件/最终SHA。

## BF16 备选最终交接

实现说明和完整命令/局限已落 `analysis/2026-10-21-hidden-row-gather-implementation.md`，不要仅凭聊天接入。runtime SHA `109905b3d276d6e4ff6cc74a7b97dfe6e8ee31a517b0ac7c4fdb163cc37ad8fd`；transformer `881f2cf209da11842577aab01cca3830e985ad7c9030554156757a5de7e791f2`；生成runner `e68d6886d788a2f56d470fccaee62558d4622545eede2a59fbeb083a5264016e`；CPU checker `670636a9aea1642afb289ef868239040c7c6aa4320643b373488104b3cc10547`。

framework_innovation已终审runtime/transformer和gate主要控制/worker逻辑，独立CPU合同/语法/help过，无明显阻断。gate最终 `93fd88ae797fe2f377bed7beb244279889881847df0497d7e347ef32e3079dd1` 在其审阅后补版本指纹以及其提出的cache能力区别：copy正确但cache不可读仍完成其余门，最终inconclusive_specialization/exit2；可读且新增entry为reject_specialization/exit1；不当成copy数学失败。修改已回报对方/root，py_compile通过；不再重复已过CPU合同。

额外只读快审另一owner `validate_mixed_token_bucket.py` 的metadata/slot/后继cache布局：初始kv_len1023与next1024均64blocks，slot mapping长度使next padded key/value只写前32，paddingNaN不入真实cache，实际metadata M和后继output尾保持。未发现阻断；没有运行该GPU gate或重做其CPU检查。

本轮所有命令均CPU本地；无SSH/GPU、无远端source、当前官方run/default变动。新候选未被选中或声称准确率/性能通过。下一条可执行操作：root确认唯一设备作业完成并释放后，按实现说明进行无权重copy门；若通过再决定热态短pair，保留小收益但不扩通用算子框架。重大结论、已纠正的未执行草稿错误和最终回复要点均在本文。

## 后续新研究与 gate 基础修复

root新委派CPU-only只选一项比小gather更有上限的新框架线索：当前唯一GPU为110149 fresh16Klong基点，growth后继；bucket105930有效Attention/整KV/nextdecode两case逐位已过，但不等于整模型。新研究不得SSH/GPU、修改运行器/候选；当前正在读取官方日志、actual scheduler/KV/Attention路径，避免重复growth、graphpool、external-event和旧微测。

root在GPU启动前发现hidden-gather gate存在确定性基础错误：`load(source/transform.py)`产生`source/__pycache__`，随后source_sha256遍历目录未过滤，必在worker之前IsADirectoryError。**已立即最小修复**为`for path in source.iterdir() if path.is_file()`；未改runtime/数学/worker。搜索本gate其他iterdir/rglob/digest，只有这一处集合遍历，其余为显式文件路径。py_compile通过。

gate最新SHA **`65cb8affd4ae08af877ccb4b4cfca6822eec5ba3f83770f39999ee677c546863`**，覆盖前述93fd版本。此为未执行前修正，尚无GPU失败/性能负结果；root负责更新上传。该错误本应在包装审阅中发现，已明确记录，不把py_compile/help或source AST合同当作controller归档路径执行证明。

## 新研究最终收敛：mixed 两段 Attention 的 stream 重叠

仅新增 `analysis/2026-10-21-mixed-attention-stream-overlap.md`，未改任何runtime/driver。没有列一串空泛路线，也没有重复growth准入、global graphpool、external events或重新扫描旧tile。此前BF16 gate基础修复是root单独明确要求，独立于本研究只读范围。

一项最有源码证据的候选：a129 C3目前自然prefix decode与prefill同stream顺序调用原forward；actual1219 decoder forward只读已更新KV，54c unified 2D不触3D scratch。可以在同层保留原两段/kernel，将decode3D+reducer放side、prefill2D留current，current join side后再原整批O/MLP。保留所有真实顺序/M/N/RNG和kernel配置，作用42层而非一次最终gather。新方案未实现、未GPU验证。

上界为每层min(D,P)减额外依赖开销；16SM寄存器/HBM争用或CoreX实际compute串行是明确反证。没有用“stream不同”当并发证据，没有用旧微测时间乘42预报收益。必须校验scratch/输出不交叉写、显式readiness/record_stream与下一层复用顺序，capture/puredecode原路，不能任一段launch后异常再fallback重复写。

公开一手已实际打开：

- https://docs.pytorch.org/docs/2.10/notes/cuda.html#cuda-streams
- https://pytorch.org/blog/flash-decoding/
- https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/ops/triton_unified_attention.py

准确actual源路径/SHA/挂点、最小实现边界和最短上卡方案均见新报告。下一条可执行操作由root决定：现队列完成后，一个真实mixed层顺序/两stream对照，bitwise+连续不同Q/scratch复用+完整warm host wall AB/BA；负面立即停止，正面才接最短16K服务pair。无需空kernel能力门/新profiler。没有SSH/GPU、没有当前任务源或参数变动。

## root后继授权后的 overlap 单层实现与终审

root明确允许本地CPU创建独立最短single-layer gate/runtime，先获得显著正信号再考虑服务集成。本owner新增 `patches/framework/biv150_mixed_attention_overlap.py` SHA **93c3124ccab9311cb98f319d9f786f7aae571f9c1d976d1a9f1d623adca378db**、`scripts/remote/validate_mixed_attention_overlap.py` SHA **914f7eb3abee25f05af8cb1a7a78eb96ede7b8c88aaf427014e16b3f745ae291**。未改a129、冻结源或任何现运行driver。

runtime是显式候选对象、不install服务类。exact source/binding guards后取原serial和其base，原scope/plan与output/scratch alias满足才双stream；actual KV先写后main ready event→side decode+reducer done→main prefill后wait done。pending强ref和recordside保证对象/allocator，done.query再release。若输入/currentstream/refs不匹配，原serial；发生partial launch异常不fallback重复写。

重大边界：完整42层异步调用可能积累强ref，puredecode graph不回Python collect，**全模型retention峰值未设计**。本runtime只给单层gate，不能跳过局部信号直接接服务。没有偷偷用host sync清队列或造buffer池/回调线程；是否值得追加设计由真实局部收益决定。

gate只一代表形状，两个不同Q连续调用、原KV先写、整output/sentinel/KV/RNG bitwise与no-plan fallback；ABBA四组各4calls，regular event和完整wall同时落盘，不使用external事件或profiler。timing event能力失败单列，真实callback/同步失败不吞；sync后pending须0。单独GPU child/lock/pre-postflight/300s/owned cleanup/来源指纹均保留，source hash两处均regular-file过滤。

最小CPU包装源check `analysis/source/mixed-attention-overlap/check_source.py` SHA **35244e5c225f8ece00ceeb75d4dd3083b6fe76ba725630f6eedf949a364e91fb** 实际通过，工具stdout记录在cpu-check.log。它真实导入新runtime但不载torch/Triton，核源码SHA/语法及两个实际source-hash comprehension在__pycache__目录下仍正确，不是CUDA模拟。py_compile/help通过。framework_innovation复读最终93c312/914f7两SHA，确认KV/ready、2D不写3D scratch、disjoint out、done/join、生命周期、wall/event和能力失败边界无single-layer阻断；没有重跑旧tests，没有SSH/GPU。

完整实现表/依赖/示意CLI已补在 `analysis/2026-10-21-mixed-attention-stream-overlap.md` 最后。下一条root操作：当前短队列后，若愿试只上传这一单层gate；exit0本身不表明正收益，检查原ABBA数据/事件能力/bitwise及pending。负面停止，不承诺硬件并发或官方提升。本最终回报要点均已落盘。

## 实际113727门与最小长窗口计时修正

root报告并下载113727后，本owner已CPU只读实际results/manifest/exit-code。correctness/output bits/整KV/RNG/no-plan均true、pending0、exit0；原gate914/runtime93c身份正确。wall表面下降2.497974%，但event慢约0.77405%，不能立即服务集成。独立算术发现serial/overlap每组wall-event差异约1.671911ms，足以解释全部表面wall优势；未定位具体构造/record/驱动/sync哪一项为根因。

root只授权最小gate修正，已保存旧914 byte副本 `analysis/source/mixed-attention-overlap/validate_mixed_attention_overlap_914f7eb3.py`，hash仍914，原run原件未修改。当前gate **ab1cd95e2f0582e1efa1deb1321887a041a88a068c655627360bb6eee4817eba** 新增可选`--timing-loops {4,32,64}`默认4，controller→worker/result/manifest/exact argv贯通；Event对象创建移wall begin前，record/submit/collect/sync仍计入，方法显式v2。runtime93c、kernel/形状/正确性suite完全不改。

查阅直接一手 https://docs.pytorch.org/docs/2.10/generated/torch.cuda.Event.html ：底层event首次record才惰性初始化，所以提前Python构造并不证明已消除驱动初始化；32或64calls的摊销验证仍有必要。只建议root任选其一新run一次ABBA，不追加形状、旧测试或并发GPU。

具体原始数值、算术分解、新方法与判断条件落 `analysis/2026-10-21-overlap-timing-review.md`。实际CPU py_compile/--help和旧914→新diff审阅已过，framework owner快审已请求；待回执即可上传新ab1版本。没有SSH/GPU，无原件回写。

framework_innovation已独立核定最终ab1 SHA及完整diff：CLI/default→controller manifest/worker argv→worker/result→每ABBA timed_batch均贯通；对象构造排除而record/submit/collect/final sync仍计时；旧914保留，runtime/correctness/形状不动，无阻断。无需新增测试或精度门，可由root按原队列只补一次32或64窗口。此为CPU审阅结论，不是新的上卡或性能确认。

## 64loop反证与下一CPU委派：prefill剩余空间

root完成114553/ab1/64calls实际overlap门，本owner已只读本地原results/exit-code/source SHA。全部correctness true、pending0/peak9；wall中位12.460649258→12.417108094（仅0.349429%），event12.409186363→12.414135933（慢0.039886%）。wall-event的组间差异仍足以解释微小wall差，首轮2.50%不算可重复收益。**不服务集成、不再扩窗口/shape/准确率大测**；没有证明CoreX硬件不支持并发。完整原数字和判断补到 `analysis/2026-10-21-overlap-timing-review.md`，两个run原件不改。

root后继委派：CPU-only复核保留prefill BM128/T64/w8/s1的原调参和actual54c，最多2项未测且有硬件依据的候选；不SSH/GPU、不写sweep/实现、不外推C2三维w2、不重测已有点。正在运行的root基点/growthV2保持其唯一设备所有权，本owner不连接。

本轮逐行读a4四CSV，42行共17独特配置；BM128/T64/w4、w8/s2/s3、T128和BM256均已有负证据。actual54c和helper59d校SHA；GQA已合并8heads，Q2048虚拟CTA仅1/129早退，不是大收益来源。没有实际register/spill/occupancy资料，不能凭warp64编造资源瓶颈。

新分析 `analysis/2026-10-21-prefill-unmeasured-candidates.md` 精确列全部已测配置/历史三shape数字/挂点/两个有界未测差异：

1. 优先实现点：普通causal完整qblock的全可见历史tile省mask，masked尾保持原实现，固定BM/T/w8/s1和原dot/softmax顺序。Q2048/KV16K有30656/30784=99.584% tile原mask全部true；真实P2019/16K在保留最后3-query整块原路后仍30177/30590=98.650%。该百分比是可删mask的tile比例，**不是性能收益**。不接任何特殊mask/量化/TD/3D；建议仅一actual P2019真实层bitwise/KV/RNG+32callsABBA门，明确速度才继续，当前未实现。
2. 低优先单点：BM128/T64/w16/s1确未测；同2D历史w4→w8约36%改善支持小心核寄存器分配，而非由C2推导。本地FlagGems有bmm/mm16warp但attention仅4/8，是能力与反证都要记录的事实。缺实际资源数据，不称高置信大收益，不建议盲扫；如root愿试仅该一点，同shape编译资源失败立即停。

公开一手实际打开： https://github.com/flagos-ai/FlagTree/blob/main/third_party/iluvatar/backend/compiler.py （warp64/default及capability映射）； https://triton-lang.org/main/getting-started/tutorials/06-fused-attention.html （完整历史/对角区只后者mask的原理，不搬其数值/后端）。尝试FlagGems v5.3.5线上yaml返回cache miss，相关16warp证据实际来自本地 `tmp/src/FlagGems-clean/FlagGems-5.3.5/src/flag_gems/runtime/backend/_iluvatar/tune_configs.yaml`，未把失败网页当证据。

收益上界仅能给Amdahl：f为当前E2E该2D份额，m为其可省mask成本，理想时间节省<=f*m；无当前phase/资源测量不编百分比。两个候选没有改模型/参数、没有路由现有后端、没有升级框架，仍需独立owner review与准确率/复现后才能提交。当前只新增分析及修改本handoff/原计时review，没有运行代码、driver、远端源、原始证据变更。此节和新报告保存了本轮重要决策、反证、未解点与下一步，最终聊天要点均在盘。

## root明确授权后：只实现full-visible prefix候选

root允许独立实现首选mask specialization，不做w16/扫描；当前唯一设备115247 growthV2由root持有，本owner仍禁SSH/GPU。授权范围是新隔离runtime/source和两shape最短actual层门，不能安装到当前source/default。

已新增 `patches/framework/biv150_prefill_visible_prefix.py` SHA **148a33ec56494fadd44965469f7cb231edd0970841d83c875dc0b16389c46626**，exact54c/helper59d输入、backend1219/C2e5守卫；派生整源 `analysis/source/prefill-visible-prefix/triton_unified_attention_visible_prefix.py` SHA **a6d3604aaf3896dce150b8ef56253a3d0fa12dd89095740bb1ec99ce975ddaa2**。`create`只写新指定file/load/返回proxy，**不install任何moduleglobal/class/default**；GPU门才临时切proxy并finally恢复。

实现有意采用最小单loop内uniform scalar分支：只在j>=full_visible_tiles时构造和应用原mask；没有复制两套dot/softmax循环，tile遍历、所有浮点表达式和K/V地址/加载mask不动。整数mask构造在选中路径移动到原where前；仅full16query且ctx>=0启用prefix，partial/invalidqblock cutoff0始终mask，原virtualCTA earlyreturn不动。全部特性开关双层runtime+kernel static_assert guard，3D/C2/未知特性走原对象，无硬件warp/阶段改变。

独立framework owner已初审148a/a6d36无数学mask边界阻断：fullblock保证128行有效，cutoff证明最后key<=最早query<=seq_len-1，非对齐cachedprefix成立；C3子metadata自算ctx不是mixed2048；单loop和原dot/softmax/PV保持。其门/最终SHA审阅尚在进行。bitwise仍需实际编译/设备门；Triton可能改变控制流布局，不能只凭数学identity许诺逐位。

最小CPU source合同 `analysis/source/prefill-visible-prefix/check_source.py` 实际exit0，cpu-check.log保存stdout：exact pin/reject扰动、非kernel AST完全不变、原signature仅新False constexpr、浮点call AST相同、单loop/earlyreturn、完整/partial/invalid及不齐prefix整数不等式过。不是Torch/Triton模拟，不证明设备编译。runtime/gate语法和--help过。

`scripts/remote/validate_prefill_visible_prefix.py` 草稿已备好：原actual builder/Impl/KVwriter+C2/C3，两shape D29+P2019和Q2048/KV16K，物理页随机、P2019共享16个旧prefix页、NaN padding与slot-1，逐位out/整KV/RNG/selection/fallback。只有P2019做32calls一次ABBA；所有timing Events预record并sync排除惰性初始化，再record/提交/finalsync计入wall。child隔离/单GPU lock/pre-postflight/超时清理/文件SHA过滤保留，未运行。后续独立审阅和最终文档/命令完成后才交root决定何时上卡。

### prefix候选最终交接，覆盖旧148a/c1a草稿SHA

最终runtime **87c6a31075939c551402d7007b491546a215584a58ec82caddc08fc7249998d6**；generated source仍 **a6d3604aaf3896dce150b8ef56253a3d0fa12dd89095740bb1ec99ce975ddaa2**；gate **d3dbf65a9a711360c92ca7c6a01a4ec23046926ee753cd37f836ad33a3bf1996**；CPU checker **9710528f41d93633020d2a1d3874586fbdf6434412cc40ebe97eaa8265df0654**。148a→87c6只把q/out/KV/table的stride guard收窄到不重叠原布局，actual interleaved KV stride8192可过；c1a→d3db只改policy SHA pin，kernel不变。最后两文件py_compile过，不为此重跑已过全部source算术检查。

完整证明、fallback表、Triton控制流可能改变布局的bitwise风险、两shape合成scope、单P2019计时方法和root下一可执行命令已写 `analysis/2026-10-21-prefill-visible-prefix-implementation.md`。source hash的regular-file过滤已逐处确认，没有旧目录归档bug。未执行过GPU失败；还没有CUDA compile/bitwise/速度/accuracy结论。

framework_innovation独立终审 **87c6/a6d/d3db** 无最短actual层门阻断，检查了随机page与共享旧prefix不会被新slot写、真实C3 P2019/cu2、partial和非对齐两maskedtiles、selection/fallback计数、int16整out/KV/RNG以及timed_case strongrefs、events预record/sync与finally恢复。其只对最终窄化guard/pin做最后diff复核，没有新suite/模拟或GPU。初稿pin占位已经补齐，root只能上传此最终身份。

本轮没有改现source/default/C2/C3/官方参数，不路由既有替代后端，不升级框架/改模型。候选只是独立mask实现，框架主线growthV2仍归root独占设备推进。下一步由root释放当前设备作业后执行报告中的一个唯一UTC gate；无清晰event/wall共同信号即归档停止，bitwise或compile失败也原样保留，不硬扩新架构。最终聊天回报的路径、SHA、边界、审阅和未验证内容均已保存于本节和实现报告。

## 121838省mask实际设备门回执：小信号保留，暂不集成

root设备owner报告 `framework/20261021T121838Z-prefill-visible-prefix-gate` exit0，policy87c6/gate d3db/generated a6d为终审exact身份。两case（C3 D29+P2019、Q2048/KV16K）bitwise、整KV、RNG、padding、2D selected与3D C2 fallback均true。只计P2019的预record Event/32calls单次ABBA：wall中位 **12.594359734375→12.559617125ms，0.275858%**；event中位 **12.491010189→12.434306145ms，0.453959%**。

结论是**小合成单层信号，保留prototype，不服务集成、不扩大accuracy**；不是官方性能/E2E，不使用mask比例或旧4calls数字放大结论。原始run/control由root下载，当前本owner本地查询该run尚未到盘；本节按可信owner回执先保存，**不冒充已独立读raw**。root12:25:01确认fullpost `68/0closed`，该旧门已关闭。新结果已同步到实现说明及原“未测候选”报告顶部，历史CPU/未测状态保留但明确被本节覆盖。

当前唯一GPU为root `official/20261021T122607Z-original-baseline`，runner166637，pristine13eb/source091033，完整两档四轮原benchmark。root+systems在空闲锁内备份并将54c反变换恢复至与a4 `.orig`逐byte一致的 **bab2** installed attention后启动baseline。**baseline期间绝对禁止import任何retained/C3平台/远端代码**：a0c retained runtime可能自动把site-packages改回54c，破坏原始基线。本owner仍只本地CPU文档操作、无SSH/GPU/远端import、不改runtime/gate/source，不新增方案或测试。旧080656门命令只作历史复现，当前不能执行。

本次任务已完成三份文档状态更新，等待root下载原件通知后仅做本地证据核对；不擅自开第二GPU或追加服务/accuracy门。此为下一API应读取的最新状态，覆盖前文“尚无设备结果/待排门”。

## SQL+C3完整补丁独立CPU包装快审（root经framework委派）

只读审阅 `analysis/2026-10-21-sql-mixed-full-package.md`、复建脚本 `analysis/source/sql-mixed-full/rebuild_full_patch.py`、原manifest及full patch；没有导入任何Torch/Triton/vLLM/retained平台，没有SSH/GPU。scope只验artifact包装等价，不重审旧数学实现、不新增suite，不把包装通过当性能通过。root original13eb official122607仍独占设备，远端retained import禁令保持。

身份实读：full patch **4aba147aa0bd3ec8dd1c12b6ae94bf39537a4cbad449e68e2fcdbfbdc0f8def6**；复建脚本 **7b0acbcd3c7805342f69b85d2222a27a3c6db372f97c633a4ad9cc84e2068349**；原manifest **911a1b08913f6d3603182c7592449fb0254b4562476fa022bcb364fa1aa58dbe**。脚本只stdlib+本地Git：reference读HEAD/objects，新tmp clone内apply/index，原reference不checkout/reset/config写入；`--verify-existing`不覆盖交付patch或原manifest。

本owner实际执行**一次** `python analysis/source/sql-mixed-full/rebuild_full_patch.py --verify-existing`，exit0，3.69秒。独立新scratch **`tmp/patch-check/sql-mixed-full-20261021T124556037704Z`**，原始精确命令/对象与模式hash结果保存在该目录的 `rebuild-manifest.json`。检查输出确认：

- base exact13eb，原6e8d9fa…performance + 4b3e2e52…joint delta复建；full patch bytes与此次重新生成完全一致。
- 全部212个归档内repo文件逐byte/SHA一致；092944 manifest明确source_dir仍为080656远端source，另核原080656全部六核心SHA。没有假称080656 screen本身含完整源码树；base-revision.txt另核d60仅为archive provenance，不入patch。
- 一步full apply与两patch stacked的完整Git index blobs/modes及tree完全相同，candidate tree **5c14cfb8d3a452e97a67758873bf18039e1bf989**；reverse精确回原13eb tree **649161e62191e81a4b367e0e19dc37e32e745099**。
- MoE JSON alias仍Git **120000**，原link target及blob SHA **c978f595e8954c76a7ff515540ae748e21f1e3c1b23d01d2373182f9c020f3f4**不变；归档copytree的解引用JSON bytes按目标内容比较，不把Windows placeholder/解引用误当mode改动。

独立 `git apply --numstat/--summary` 读full patch：仅预期9个Python路径，**988新增/0删除**，新文件均100644，无JSON/config或symlink diff。另核default仍6e8d9fa631b7e2f9aa0a848443e602c224c1bbd1f0787b417f78dd3b9f51e99b，joint delta仍4b3e2e52b01d04a0f0477ae4e9b8dc3fed3c1f721360af3bbe6b01014572bbba。full patch搜索bucket/growth/hidden_row/overlap/visible_prefix/121838无命中；该rg exit1是预期“无命中”，不是验证失败。

**独立包装结论：未发现交付阻断**。full patch可作为原13eb一步apply的既有080656 fallback候选；不覆盖默认，不加入未选创新，不声称比原13eb的总体增益已成立。原103/105/092944证据仍属既有候选，包装没有新增准确率/设备数据。无需再开测试，回执发framework/root即可完成本轮包装；本owner只新增此handoff记录和验证工具自行创建的新tmp scratch，作者patch/script/manifest/说明均未改。

## 最后一轮prefill机制核对与用户冻结：仅证据/草案交接

root先委派只读审一条剩余较大机制，后允许CPU固定tile MM grouping候选/门草案；用户随后明确“停止探索，现有工作收尾保留后去GitHub协作”，补充“把已经开始的做完”。root最终限定：只完成已开工产物，尚未开始的实现不扩大。**中断前未写MM grouping runtime/transformer或GPU门代码，因此停在证据/设计文档，不再补新实现或测试。** 已向root和framework说明实际进度，不能把计划称为prototype已实现。

实际最终产物：

- `analysis/2026-10-21-mlp-cta-grouping-evidence.md` SHA **f815344972eec96744476b0e224de6e89551b2aedb0b356e3fd09fd40b4de213**：新证据、负面、精确两shape当前C0、group8末组数学、未执行最短门草案、冻结/恢复步骤。
- `analysis/source/mlp-cta-grouping/evidence.json` SHA **875f2662e1fc9045ce9d4116ab9deea41a7ad758a8fbe5af58c9fc8fd256e320**：原trace SHA、实际shape/kernel资源与时间聚合、immutableDB六个既有best rows、121838原件核对。
- `analysis/source/mlp-cta-grouping/iluvatar_mm_original.py` SHA **4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090**：持久保存actual installed原件，未修改。

目录实查只有evidence.json与原件；`patches/framework/biv150_mlp_cta_grouping.py` 和 `scripts/remote/validate_mlp_cta_grouping.py` 均不存在。没有GPU/SSH/远端模型导入，没有已执行CPU bijection/新suite，没有服务集成或默认变更。

实证：旧16K prefill raw gzip SHA1a7f511d…，948kernels区间并集3720.346239ms/首末span3757.450509ms，内部空隙约0.99%；RMSNorm/SiLU/RoPE已融合，RoPE相关pointwise+KVwriter仅9.258466ms；原metadata按group一次build并分给各layer，GQA已经每KVhead复用8Qheads。没有据此复活重复launch/metadata或8倍GQA虚高主张，也没有把旧窗口比例外推SQL后/当前E2E。

唯一尚留机制是旧gemm研究已有而未实施的grouping后备，本轮新增真实prefill数据佐证：actual4c2e的GROUP_M=8映射被注释，N索引最快；M2048 gate-up/down各84次/117.804835与60.900605ms，两MLP178.705440ms约为上面小融合基数19.3倍。当前115950-control/db-after snapshot SHA29fb47…，best表对应gate-up **BM256/BN256/BK32/w16/s2/SK1**、down **BM256/BN128/BK32/w8/s2/SK1**，grid384/128与trace1024/512threads匹配。未从grid单独猜tile；旧trace未携带同一mm源码/DB manifest，只能交叉佐证，不冒称当前compiled实例身份/时间份额。

设计草案仅改CTA枚举，全部tile/warps/stages/FP32acc/K顺序/输出mask保持；group8尾组用实际h，u=pid-gW，(row,col)=(8g+u%h,u//h)，不是硬写h=8。SPLIT_K1保证没有跨CTA浮点归约；仍须bitwise。B权重48/24MiB均大于实际16MiB L2，复用距离可缩短但A缓存竞争/compute-bound是反证。门草案只两M2048投影原枚举对group8，未来一次partial-tail CPUbijection及32calls预recordevent ABBA；**全部未执行、没有门脚本**，不新增w16/packing/fusion/其它group扫描。

同时修正前文121838“等raw下载”的过时状态：原件现已到盘，本owner实际读本地results/manifest并逐项核15 source SHA全真，正确性/0.275858%wall和0.453959%event小信号与回执一致。此核对保存于上述evidence.json，两个prefill报告也已从owner-only改成raw已读；仍保留prototype、不服务/accuracy扩测。

公开一手实际打开并直接引用： https://triton-lang.org/main/getting-started/tutorials/03-matrix-multiplication.html （grouped program order/L2机制，未引用A100数字预测本卡）； https://github.com/flagos-ai/FlagGems/blob/v5.3.5/src/flag_gems/runtime/backend/_iluvatar/ops/mm.py （源码对照，actual4c2e才是身份）。没有合并新分支/后端。

恢复边界：用户未明确恢复前停止此线。无grouping运行代码需要回滚；现有mask/gather/overlap/bucket等产物保留未集成状态不变。root原official122607仍唯一GPU、installed bab2，绝对不import会自动写回54c的retained/C3远端模块。以后若用户恢复，再核live源码和实际best config是否仍同，先读上述证据/草案再决定是否实现，不能直接执行不存在的gate。当前只等framework一次只读证据/映射收尾回执落盘后结束，不继续研究。

**收尾回执已收到，任务到此结束。** framework_innovation一次只读核f815全文/evidence875f/source4c2e及目录确实仅两文件，固定M2048两配置的grid384/128、warp64线程1024/512与原摘要一致；旧trace/新DB非同manifest因果边界准确。tail公式u=pid-gW、实际h=min(8,R-8g)在u∈[0,hC)静态数学上一一覆盖，无文档交接阻断。对方没有重算raw/DB、执行CPU bijection或GPU，审阅不冒充实现通过。

最终向root报告：证据/草案已完成交接；MM grouping无runtime/transformer/GPU门脚本、所有门未执行，已有冻结候选无变动；不再新增探索、实现、变体或测试。用户停止探索指令保持，下一阶段GitHub协作由root处理。本owner停止本线，全部最终状态与产物身份已在本文落盘供后续API读取。


## 分析文档中文化完成：不恢复性能探索

根据 root 转达的用户授权，只完成已确认的 analysis 顶层英文叙述文档中文化；性能探索仍冻结。本轮没有 SSH、GPU、远端模型或 retained/C3 导入，没有修改 runtime、补丁、默认候选、analysis/source 或实验原始证据，也未执行历史文档中的待办实验。root 负责在途原版 baseline 与 GitHub 协作。

本轮恰好修改下表的 16 份分析文档，翻译标题、正文、表头和结论。命令、源码路径、哈希、URL、技术专有名词和原始数值保持；历史状态、旧候选计划和未解决问题均显式标为历史，不伪造当前通过结论，不把诊断结果改写成官方分数。

每份新增相同的平台范围说明：本地实测与源码适配仅覆盖天数 BI-V150；沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。只有实验/分析库 FlagOS-S2-Minicpm-throughput 按平台记录；私有框架库 FlagOS-S2-vllm-plugin-FL 和 FlagGems 是团队共用代码库，本轮未要求或创建平台目录/分支拆分，也未修改保留的公开 fork。

校验方法与结果：翻译前将这 16 份的全文和 token 清单保存为本地临时快照 tmp/translation-analysis-english-before.json；以文本读取统一换行后，仅排除本轮新增的精确平台范围段落，逐文件比较行内代码、完整 fenced code block、URL 和数字标记的多重集合。最终全部通过：217 个行内代码片段、15 个 URL、7 个完整代码块、1,288 个数字标记一致；所有文档均只有一份平台范围说明，未含 Unicode replacement character。曾发现原文 0 failures 译作“零失败”，已改回显式 0 后重核通过。最终本地检查结果保存在 tmp/translation-analysis-validation.json；该临时文件不是新增实验数据或交付源码。

| 中文化文档 | 最终 SHA256 |
|---|---|
| analysis/README.md | 6779cf8daf62d807f71e25fed9c7fb3f54ac9754e6cdae5d839bf426c9e28187 |
| analysis/source-map.md | 9515a042c20c234bc8ab8fb8adec5483a32740685e1b6a8b824a3a700fe12abc |
| analysis/bottleneck-hypotheses.md | 4e251687ab859950e9c7060d2748dbd66b5c6617b8ca7b8de93f40e777f8744a |
| analysis/baseline-2026-10-21-in-progress.md | 786f6b1da91f3a65c511aca613e3bc067368f98cf87fbd05fc224ba58f542861 |
| analysis/baseline-4k-clean.md | 29669104f9b46703fa27de75e35f1acc062887b0bb1745b5d9e2b7d640d48d5f |
| analysis/2026-10-21-16k-baseline-preliminary.md | 9b43501858ddcc4a56e3218592b8eb2aeb5d2b9ff3dbf78ac7222ee67725963a |
| analysis/2026-10-21-4k-baseline.md | 0bdab0f2dc6e6ab33b8842b05aeccec5e96142569206b2a9de639159555e4e84 |
| analysis/2026-10-21-baseline-preliminary.md | 2ee107a4bf859faad14c18f504b02a79d4c21a0c3af27c38a2c010cd9ec4ae1c |
| analysis/2026-10-21-attention-hypotheses.md | 1a1c299c785f23d801771744d6491fe5e6601694b92a5df65222ef033eaf330f |
| analysis/2026-10-21-attention-top-p-candidates.md | 8030a9273b2325ce06fc7ef320783872abe238c3392ee1d4ead72086920ab816 |
| analysis/2026-10-21-biv150-hardware-adaptation.md | 9cb1a5c1bc89064df75c6808f494537db5fcba613de2b438c6631b0a86c34cb1 |
| analysis/2026-10-21-bottleneck-profile.md | 22aa3bc3466d44e60f06495eb019a28dbee80b6123cb2d3563cb4f530a862513 |
| analysis/2026-10-21-direct-decode-launch-review.md | ddf4d142d32cc8f76cf89acf4d7c079aafee938b47354fa16cb1866cf9b99389 |
| analysis/2026-10-21-external-evidence.md | 15d93e58c7d9fe33dc5df80e60dcf4a0f05b42005b78f55711f412fb83cabf34 |
| analysis/2026-10-21-framework-review.md | 9dd1b728278da55fa29f2534f6588c84d6e2e6a264496265fae0f9ad44fe1e4a |
| analysis/2026-10-21-framework-smoke-differential.md | 10a31fdb6845405e90b6e1a190c53be2146383fbe8d3f750e0d05b2b42a790d2 |

交接已完成：root 可将上述文档作为中文分析材料纳入团队实验库。本轮未改技术事实、既有实验结论或精度门禁状态；不追加测试、变体或研究。下一个 API 读取本节及项目工作记录即可确认文档范围与冻结边界。


## FlagGems 私有协作副本准备完成（仅本地文档提交）

root 授权只整理 collaboration/FlagGems，本任务没有网络 push、SSH、GPU、模型导入或源码实现变更。该离线完整 clone 的初始状态为干净、detached HEAD，官方 tag v5.3.5 精确指向 4df52d9168ac55c1c1061cefb4638c570292d896；未改其他参考源码副本。

在本地创建 codex/team-collaboration 分支，将上游原 README.md 的 Git blob 精确保存为 README.upstream.md；README.md 改为自然中文协作首页，链接原 README_cn.md、保留的上游说明、官方 FlagGems、团队实验库及私有 vLLM 插件库。首页明确：固定上游版本；当前未直接修改 FlagGems 源码，候选通过 vLLM 插件按运行时条件接入，保留候选不等于全部默认启用；团队共用算子代码库不按平台拆分；实测仅 BI-V150，C500 由队友验证，不能外推团队总分；许可证原样。未把实验报告复制到代码库，未修改原源码、原 docs、README_cn.md 或许可证。

本地 remote 配置：origin 为 https://github.com/Silas-Zeng/FlagGems.git；upstream fetch 为 https://github.com/flagos-ai/FlagGems.git，upstream push URL 设为 DISABLED，避免误推上游。所有 remote 修改都是本地配置，没有执行 fetch 或 push，没有改变 GitHub 可见性/分支。

最终身份：

- 本地提交：6ddb4c4cd12790cfc7b1203bdca2ed7a131f7dd6
- 提交说明：docs: 添加团队中文协作首页并保留上游说明
- Git tree：e8ba50863b7bfabc725cc6aaff97d3548d7daf0f
- 唯一 parent：4df52d9168ac55c1c1061cefb4638c570292d896
- README.md blob：d2a2497461b5f8da8cd2157d0ad3e19eab398f6f，SHA256：3107e51e763335c80f7e3177fa3d19120bcfc9d423ae71dd8462924de3738ad2
- README.upstream.md blob：b0b354447c77bb2b33bf30ec2eb21eaa794bf1fc，SHA256：85c387d7b6a3442265142eb13db35b04d7409324e294fec258747cbee5062125

验证已经完成：递归比较 base 与提交的完整 Git tree，原有 4,768 项中仅 README.md 改变；其余 4,767 项的 blob/type/mode 全相同，唯一新增为 README.upstream.md，且 mode/blob 与原 README.md 完全相同。LICENSE blob 仍为 f433b1a53f5b830a205fd2df78e2b34974656c7b；README_cn.md blob 仍为 f660ccb7a14bcf5cf934496e60eb1bb685f3d78d。暂存及提交后 diff --check 通过，本地工作树含未跟踪项检查为空。只做必要的文档链接存在性和 Git 对象校验，未运行算子测试或改变源码格式。

交接：本地副本与以上 commit/tree 已准备好，root 可据此通过 API 上传到授权的私有 FlagGems 协作库。本任务不负责网络上传，不将本地提交误报为远端已发布；性能探索继续冻结。


## 两个私有代码库已发布与离线 bundle 收尾

root 回执已完成两个 private main 的 API 上传与核验：FlagGems main 为 d7e5cef98344cd068df2e425748f849c94681048，tree e8ba50863b7bfabc725cc6aaff97d3548d7daf0f、4,769 项；插件 main 为 d5e2e3a54b48dcb1b50f575d2420979591fb3e1c，tree 82e37f8f263eeb09563a4790359ec95a0de1ca17、410 项。这是可信主负责人发布回执，本 owner 没有联网复核或 push。API 以远端初始化 README 为 parent 发布完整 snapshot，因此 remote commit 与本地 6ddb4c4c/70d04f38 不同，而 tree 完全相同。此次离线 bundle 不含该远端初始化和发布 commit 对象。

按 root 授权，新增以下材料，没有覆盖旧 experiment-history.bundle 或 plugin-base.bundle，没有改两个代码副本的工作树、refs 或源码：

| 新 bundle | 大小（bytes） | SHA256 |
|---|---:|---|
| flaggems-team.bundle | 24176530 | 57726da42df72e2fc2b5cbd41a9ac006aff26f85aa9f0b41d338bcfb2329cd09 |
| plugin-team.bundle | 654765 | 18f7e05b56b85b4c8157f51dd252c8bf49a4156e9c06b98d152f3343c7e6c6f5 |

**补正前文“完整 clone”的含义：完整工作树不等于完整上游历史。实际两个本地代码副本都是 shallow。** FlagGems boundary 为 0db588057a4aac1a35b3cde44d1fc7f5159fc3d0（原 shallow 文件重复两次，原字节保留），全部 refs 可达 3,298 commits、HEAD 可达 52，含 HEAD 的 30 refs；插件 boundary 为 13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0，全部/HEAD 均可达 2 commits，含 HEAD 的 2 refs。配套原 shallow 文件分别保存为 flaggems-team-shallow-boundary.txt（SHA256 dfbc66cbb2e18b103f1375722fa35b49d415ac494dec54668d0592096028b8ae）和 plugin-team-shallow-boundary.txt（SHA256 e07d95dcfbe88f3ae741dbc788bb59b7bbb248515f5dec6b727f3f52588e20af），不能丢弃或把 tags 数量误称完整历史。

两份 bundle 均使用 git bundle create <新路径> --all HEAD。实际最短恢复记录为 recovery/git/offline-team-code-bundles-check.json（SHA256 99b4e1ecbb826ce95eba2d18ab0124eb58b4a9ca4a2952be271306f9b578a9a3），UTC run 标识 20261021T162858Z，新 scratch 为 tmp/team-code-bundle-restore-20261021T162858Z。先在源库 bundle verify/list-heads 对照全部 refs，然后各建全新目录，先复制浅库边界，再 unbundle、逐项 update-ref 并恢复 HEAD 指向，核对全部 refs、HEAD/tree、all/HEAD commit count，bundle verify 与 fsck --no-reflogs 全部 exit0。没有 checkout 工作文件或执行代码/设备实验，验证的是 Git 对象可读与 refs/历史边界正确。源工作树和 refs 前后逐项相同。旧 root/base bundle 的 SHA256 前后不变，分别 dbfdc6659cde22163c7baa3a3c0c87acf7552f06e039f4b8b4768bc9cc82e721 与 924c19e96acec38d12bbdf1e2b574c0d707d65ae3f68a18a536b8d2d2f9937cd。

本轮两个指定维护文件已更新：

- scripts/save_git_handoff_state.py，SHA256 29afeecc45822348ee6062de4ae898d72305451ebab8c35cb1f094baa7533eb6：扩展两个团队 repo；每次 Git 子进程只为当前明确 repo 设置进程内 safe.directory，无通配信任/全局配置；记录 HEAD tree 和可达提交数，通过 Git 自身解析 shallow 路径。py_compile 和完整运行均通过；manifest 现含四库，新增两库所有状态文件哈希/字节/HEAD/tree/空 status 与 bundle SHA 均复核一致。
- docs/offline-recovery.md，SHA256 44f8d7ba9675faff70bdb2b55f3e1f08a70c6a9a3742402103867ad6d8140a6a：说明 local/remote commit 差异、上游历史保留范围、先恢复 shallow 再 unbundle 的步骤，以及 unbundle 不自动安装 refs；保留旧参考浅库的恢复证据，明确 root bundle 最终更新由主负责人负责。

一次初始 PowerShell 只读查询未给 HEAD^{tree} 加引号而被当 ScriptBlock，已改用 subprocess 参数数组后正确读取，不是设备或实验失败。整个任务无网络 push、SSH、GPU、远端导入，没有生成最终 ZIP。root 仍需在最终提交完成后刷新 root bundle 并重跑状态保存；本 owner 已完成新增两库 bundle 与验证，不恢复性能探索。
