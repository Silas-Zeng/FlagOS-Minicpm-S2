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


## 2026-10-22 恢复探索：MM group8 及独立小收益队列

用户最新授权持续探索优化，并明确小收益也要最短上卡实测、保留结果，覆盖此前阶段性冻结。root 先要求归档写锁期间全只读；本 owner 已遵守，没有在锁内写文件或运行设备。归档锁现已解除，root 授权本地准备固定 tile MLP CTA group8 候选及最短 GPU gate，设备仍只能由 root 串行执行；本 owner 没有 SSH/GPU、远端模块导入或 GitHub 修改权限。

只读阶段新增核实：已验收 SQL+C3 092944 的 actual mm source pin 仍为4c2e23da…；其 database-before/snapshot.sqlite SHA dc6a07db6d31ab210aede0ae92dce0378440729e7c91a0183c269111b3c0ad5e、database-after/snapshot.sqlite SHA e90b666d97547ef35ebc5e2a01d24d56a5d16a38d49fcb3908ddb7fc62cad342，按 mode=ro&immutable=1 只读核到 best 表7ea0…两 M2048 配置完全相同：gate-up BM256/BN256/BK32/w16/s2/SK1，down BM256/BN128/BK32/w8/s2/SK1。未把 benchmark rows 当 best rows；没有用旧 trace 的占比外推 SQL+C3 当前服务占比。actual libentry SHA414e8a3f74e2522e40659e7fccd84e301f4517220837a87af0311f050bbf3025 与固定协作库一致，:1682 entry miss 才进入 tuner，:1742 热命中直接 compiled kernel，反对泛称“每层仍重复SQL”的新假设。

资料重新实际打开：Triton 官方 https://triton-lang.org/main/getting-started/tutorials/03-matrix-multiplication.html 说明 program reordering 的L2复用机制与正确末组局部取模；固定官方源码 https://github.com/flagos-ai/FlagGems/blob/v5.3.5/src/flag_gems/runtime/backend/_iluvatar/ops/mm.py 中 grouped mapping 仍被注释。FlagTree https://github.com/flagos-ai/FlagTree/blob/main/third_party/iluvatar/backend/compiler.py 仅作 warp64/编译机制一手参考，不升级当前编译器，也不外推其新硬件特性。此方向未实测，A缓存竞争/已compute-bound/CTA物理调度均可导致负结果。

root本轮授权文件：patches/framework/biv150_mm_cta_group.py、scripts/remote/validate_mm_cta_group.py、analysis/2026-10-22-mm-cta-group.md。只改变两种真实投影 M2048 的 CTA 枚举，固定全部已有 tile/warp/stage/SK1/FP32acc/K遍历；先做必要末组 CPU coverage，再由 root 排两shape逐位/输入/RNG门与一次32call预record ABBA。不改已安装FlagGems，不autotune，不与 prefix-mask 混合。

独立小收益队列仍保留 prefix-mask policy87c6/generateda6d/gated3db 已有两shape设备通过、局部wall0.275858%/event0.453959%信号。后续服务 pair 拟在隔离SQL→C2→C3 runner footer之后安装proxy，必须在capture前、每PID独立派生路径且幂等，避免create(xb)多进程文件冲突；必须有实际selected>0证明生效。相同热DB/KV/shape/seed的warm16K32req1024out最短pair由root另排，不因小跳过，不与CTA合并；落噪声也保留为未确认，不冒称E2E收益或继承准确率。此服务installer尚未写，本轮优先准备CTA门。


### async-token 接续 SQL+C3 的独立包装快审

root 在 CTA 准备期间委派只读审 patches/framework/biv150_async_token_update_sql_mixed_source.py。我实际仅用 stdlib 比较源码/AST，没有导入其 Torch/Triton runtime、没有新设备门或修改 root 文件。新 transformer SHA cfd378a494c0ccbb5aece861527cdf59ccd148afbe53ac229a09bb43162bdb6f；ORIGINAL/REPLACEMENT 与旧 transformer 逐 byte 相同，runtime 仍为受测 1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc。

e155 runner 确实以旧 446f12c0… runner 为完整原始前缀，新增 SQL/C2/C3 footer 不改变 ID seam。旧、新变换前的 _prepare_input_ids AST 完全同一；旧、新变换后的该方法 AST 也同一；逆向移除替换和新增 import 后完整 bytes 精确回 e155。新输出 f0d0bada4222038b69ed139d804622e27acd6aa4e19a37ff089b0ca35f393f41，旧输出 ce1860c89760c851c2f6b3bb4c35dd334e01e7927844c5460ec35f407633fdbc，语法通过。C3 的 Attention metadata/forward 包装未改变 _prepare_input_ids producer/consumer 或原 stream 保护。

独立结论：无新增审阅阻断，同意复用063353的12case整数逐位门作为该seam证据，不重跑同一微门，root可排匹配4K64req128out最短服务pair并核FIRST_SELECTED/selected计数。该局部门不是新SQL+C3+async整模型accuracy通过，父基点103/105不自动覆盖新增实现；有服务正信号后再决定必要最终准确率。已将此边界发送root，没有替root上卡或改文件。


### MM CTA group8 本地候选与最短门已完成，等待 root 上卡

实际实现仅新文件，不修改已安装/固定 FlagGems 或已验收 SQL+C3。最终产物：

| 文件 | SHA256 |
|---|---|
| patches/framework/biv150_mm_cta_group.py | 06c7cd9216907886e7d66a81d4fd5d9f78edef9daac2380ca263ce8c1770b8e1 |
| scripts/remote/validate_mm_cta_group.py | 4b44b930aad534301c1545d5748a6dae2a85e2345d7a446185a46d5082d71cd9 |
| analysis/2026-10-22-mm-cta-group.md | 766c07c6d704521f1affff3a3bfb05ddc519e0537af64e9ab1b6ab73afbd7995 |
| analysis/source/mm-cta-group/cpu-check.json | 3172fa8087a2ca37a6b9c98c4209780e2155f226b942d23c48e24a807689b5c7 |

运行时 pin official actual mm4c2e，全文件拒绝漂移，精确提取原 @triton.jit mm_kernel；baseline的JIT AST与原件一致，candidate仅换整数PID块。派生baseline SHA73d5cf8f080fa53ab17023b228d0215fcf71efc6a17ee9b7294e194c38f61faa；group8 SHA30d0f046071fc4cf122d43af0d087259abc082ad10ec36f69b73ad6a22b343ab。没有把旧注释全局pid取模直接启用，使用组内u和实际末组h；全部K循环、FP32acc、tl.dot、BF16、precision/fast_accum及launch C0不变，固定SPLIT_K1。

严格scope仅M2048、gate-up N12288/K2048（BM256 BN256 BK32 w16 s2）和down N2048/K6144（BM256 BN128 BK32 w8 s2），同GPU BF16与真实linear转置weight stride(1,K)，A和out连续、storage分离，设备BI-V150/16SM。非匹配直接拒绝，不调用替代后端，不构造通用算子框架；服务集成没有实现。

必要CPU合同已实际执行一次、保留cpu-check.json：baseline函数AST对原件相同，grouped逆换唯一mapping bytes完整回baseline，原源码扰动拒绝，派生源码compile过；6个coverage用例覆盖实际R8、末组R9/R10/R17及partialM/N、R1，tile一一覆盖。CPU合同没有导入Torch/Triton。runtime/gate py_compile、--help与最终policy pin比较过。没有GPU数据或已执行设备失败，设备结果表保持未执行，不把数学证明当GPU bitwise。

GPU门只两形状、每形状一次32call预record Event的ABBA，不扫tile或autotune。首JIT编译在窗外，热launcher复用actual LibEntry3.6:1777的CompiledKernel[grid](*all26args)；门同时pin actual libentry414e/Tritoninit df309与模型config596，保存原源码与编译资源。初次JIT后poison有效out为NaN再真实热launch，完整输出int16 bits/finite、两边guard row、整A/weight输入、CPU/CUDA RNG前后比较。原始wall/Event窗口与计时后正确性均保存；失败记录phase/traceback。单层合成信号不等于服务或accuracy，小/零/负也保留，落噪声待确认不按百分比丢弃。

控制器CPU-only、唯一framework-device.lock，沿用9031双栈/ixsmi单卡>=30000MiB空闲检查，只有自己child拥有CUDA，300秒timeout与owned process group清理，原日志/命令/source/GPU采样/prepostflight落唯一UTC run。source hash只遍历regularfile，避开此前__pycache__目录错误。门需要既有validate_block_table_candidate.py与monitor_gpu.sh，exact命令在analysis文档。未写新launcher、未加载模型权重/runner，禁止本owner执行设备命令。

systems_innovation独立全文快审06c7+门草稿：固定C0/源算术/末组、26参数interface、transpose layout、guard/RNG/inputs、预record计时与单child清理均无当前阻断。随后实际核最终4b44门的两项delta（pin06c7、首JIT后有效out.fill_NaN）也无阻断，不新增suite或设备验证。该回执可用于进入root最短设备门，不等于GPU通过。此最终状态与原件SHA已发root，root173003 coverage作业期间绝不并发设备。

独立prefix-mask服务pair计划继续保存于同analysis最后一节，未与CTA混合，也未实现其服务installer。用户已明确小收益也上卡并保留；root另排匹配热端到端pair，必须实际selected证明命中，有新代码不能继承父基点accuracy。


### CTA 173921 真实失败保留与最短 guard 诊断

root已上卡173921，policy06c7/gate4b44；本owner读本地experiments/framework/20261021T173921Z-mm-cta-group-gate/results.json及worker.log，独立核11source SHA全匹配。gate-up all_output_bits_equal/valid_output_finite/inputs_unchanged/rng_unchanged均true，guard_rows_untouched为false；exit1停在correctness，无timing/down。两compiled kernel均97regs/0spills/shared65536，baseline hash3639b8c9…、grouped08afb545…；不能把局部bits相等当门通过。root完整postflight已idle32700free/68MiB/0%。原run/source/gate4b44和所有失败原件未改。

原guard唯一判据是storage[[0,-1]]高级索引加GPU比较，baseline/candidate未分开保存原值。源码静态写范围仅有效M行；若热C完全丢storageoffset，最后有效out应仍NaN、finite应false，这与实录不合，但不排除真实越界。高级index负数读、GPU比较或out.fill_NaN的view偏移均只能列待证伪解释，不可直接归咎基础库或删guard。

root授权准备最短分阶段诊断。当前scripts/remote/validate_mm_cta_group.py SHA ee263763948421193fc7a323a13ca20e184d7ef074812ac5486f5eee5fe60213新增--guard-diagnostic；policy06c7/数学/原normal guard不变。仅gate-up、无timing/down；分别保存full初始化/各JIT/各out poison/各compiled后，两个storage的正数basic row0/last全量CPU int16原值.i16及SHA、异常数、头尾值，并保留旧advanced raw/GPU predicate/CPU比较和读是否改storage。记录out指针/基址/offset字节、闭包真正all_args[2] C对象；阶段变化相对真实初始化bits比较。诊断status明确not_a_correctness_pass，完成exit0不等于数学成功。pycompile/help过，交systems快审；本owner没有上卡/远端导入。

analysis/2026-10-22-mm-cta-group.md已前置本失败与诊断边界，旧实现说明仍作为历史，prefix-mask准备暂被此问题打断但原任务保留；root另在跑metadata/async独立服务pair，无人授权我GPU。

root已独立读完ee263诊断增量，回执positive basic D2H、CPU bits、完整guard bytes、compiled_C指针、保留旧advanced对照及非pass状态无当前阻断；仍等待systems独立回执，文件未再改。analysis结果表已按173921实际失败更新，避免旧“待执行”占位掩盖已经发生的失败；新诊断仍明确未执行。

随后systems_innovation独立只读快审ee263回执无阻断，并已直接发root：正数basic0/last行完整CPU int16 bits/SHA为oracle，advanced仅旁证且再次basic回读检查storage；view offset与闭包all_args[2]真C对象identity齐备，七阶段、gate-up-only/no timing/down与非pass状态边界正确。没有重复suite/GPU。本owner据此将最终ee263交root独占设备队列；不重写旧4b44失败或提前声明诊断通过。

root随后实际执行180033最短诊断，原件和control均已本地保存。本owner实读results与manifest并重核全部source SHA：status为guard_diagnostic_complete_not_a_correctness_pass，18:00:33.650193Z→18:00:42.910097Z、exit0、前后9031free/32700MiB free。七phase两storage的basic first/last异常数全0且SHA不变；advanced在初始化尚未JIT时已经matches_basic=false、12288异常，各阶段一致，advanced读取后basic storage仍未变。compiled_C为原out对象，offset12288 BF16元素/24576字节均真。仅证实旧高级索引oracle读值异常，不能定位Torch/FlagGems具体责任；保留173921原失败、不改写成通过，也没有down/timing数据。

root授权修正式门oracle，当前scripts/remote/validate_mm_cta_group.py SHA b216a49a02c90234f7cdfc12db990b2759771d5129169a237824fa9cddd12d91；policy仍06c7，不改两个派生kernel/C0/math/shape/32call预recordABBA。复用完整guard_snapshot，新增纯CPU metadata判据：positive basic row0/last全int16必须期望-17 bits相同且SHA等实际初始化，初始化本身也需正确；advanced raw/GPU predicate仅诊断，advanced读取后CPU basic回读仍须storage不变。每shape初始化/各JIT/poison/hot后即时检查，计时后再查，所有采集在窗口外。仅py_compile/--help通过；systems已只读审b216无阻断并直接发root，没有新suite/GPU。root可按原正式命令串行重跑两shape，不加--guard-diagnostic；本owner不执行设备。

### mapped singleton decode 设计的只读交叉意见

framework owner 暂停strict-greedy重排设备队列：actual benchmark不传temperature，MiniCPM generation_config为temperature1/top_p0.95，因此官方random会fallback，不能用修改采样参数制造性能命中。其新mapped设计尚未kernel实现，本owner仅读actual54c统一源码并发CPU地址审阅，不替owner实现或上卡。

actual :287–355/:596–620/:686–745支持区分三种行号：req_idx=map[d]仅用于seq_lens/block_table/按请求feature；真实token t=cu[req]用于Q与最终out；compact d用于三份segment scratch。BM16/GQA8下query_pos=offs_m//8仍有第二个无效token，scratch需使用d+query_pos且保留query_mask0，不能把query_offset0全局改成d以免破坏Q/因果位置/store；:608 store_segm_reduce_scalars同样必须接compact向量。Reducer读scratch=d、写out=t。建议MAPPED仅IS_3D、所有USE_TD/TD_QO等未知feature回原路；2D先保持原resolve和virtualCTA earlyreturn，再跳过querylen1，map必须覆盖每个singleton恰一次以免漏写/双写；map/cu需producer readiness与record_stream生命周期保护。

关键验证边界已指出：原C3非prefix singleton原本走2D，新mapped改3D即改变浮点归约顺序，已有C3准确率不能自动继承。地址门宜先对相同3D配置的serial split oracle逐位，若服务正信号再必要整模型accuracy。既有coverage只证明原plan，不证明impl guard或实际launch；不得把planned prefix比例当真实launch覆盖。等其设计文档/数学coverage产物后再只读终审，未新增实现或测试。

随后实际读framework设计文档1124f5b34e65791feb43f0d6049fcc4d0d4e86386c3c313cf6960cc3a87f471c第5–6节与proof4c4fe093f2f7e4b2c38c4025d404ce8931d1cb1c84f4a044c87afbdd89dd4a0c，核哈希一致、没有重跑suite。proof按actual cu//BQ+req虚拟起点和upperbound grid/earlyreturn检查集合，map唯一含全部singleton，2D/mapped不交不漏、scratch上界及N/D边界数学无阻断；它是整数模型，不是Triton执行证明。派生JIT不自动继承原C2代理，必须显式BM16/T16/w2s1/S16、旧FIRST_SELECTED不能作新路径证据，文档已加入。仍建议正式handoff补map pinned H2D strongref、producer→forward stream wait/record_stream、跨步复用与capture/未知feature/KVsharing回退，已发owner/root，未修改其文件。

prefix-mask服务准备仍无runtime/transformer写入，root要求先集中CTA guard。已把只读挂点审计与最短pair方案补入analysis/2026-10-22-mm-cta-group.md最后一节：exact e155 init481–968不load/capture，worker473构造/484load/745capture，适合原init返回后且footer已SQL/C2/C3安装时装独立proxy；每PID新目录避免create(xb)冲突，真实单请求scheduled≥128加selected增量才证大query省mask，不能拿smoke或总M证明。热DB/实际C0/KV匹配、不同seed预热真实形状、原16K32req1024out服务pair、所有小/噪声结果保留边界均已落盘。没有开始分散的新实现或GPU。

### 180646正式CTA门完成；仅gate-up服务入口已交接

root实际执行experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate，10秒exit0；本owner读本地results并核全部source SHA，两个shape bits/finite/inputs/RNG、8phase basic guard、after_timing全true。gate-up wall1.4179341875→1.1885717656249999ms（快16.1758158%），Event1.4043543934822083→1.174988865852356ms（快16.3324535%）；down wall0.735825265625→0.763840109375ms（慢3.8072685%），Event0.7219997048377991→0.7500479817390442ms（慢3.8848045%）。原173921失败、180033异常oracle诊断、down负结果全部保留，不覆盖、不把单次合成ABBA当服务或accuracy。

root授权只实现精确gate-up服务，不启down。已完成且systems独立全文审无阻断：

| 文件 | SHA256 |
|---|---|
| patches/framework/biv150_mm_cta_group_service.py | 44fc8e5c887340f245332635a245690946de38f201678b07212137d4c8a716f7 |
| patches/framework/biv150_mm_cta_group_service_source.py | 4ab31a9cb864af75be8ad891902b1433cf1bb007a05e18bbbc4310b6aa37016d |
| scripts/remote/prepare_mm_cta_group_source.py | e007cccf21f20ac3130cf1c0f414189ad4ea45687bac7167e3f8a29e68ff4a2c |
| 复用prepare_innovation_source.py helper（未改） | 0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca |
| 派生runner（原e155完整prefix+新footer） | 787665d3cf6dabc1afc2bdf7069fab4802fd5f6bfb0baedd119229b5b8ce1775 |

实际入口从fg.mm.__module__找到真实alias模块，验证mm/mm_out globals及FULL_CONFIG/实际mm注册，再仅装mm_kernel代理；注册函数本身不改，不另import未被dispatcher使用的canonical别名。严格MiniCPM原config596/BF16/2048/6144/42/16/2/单卡、无量化specLoRAMM连接器共享KV，ContextVar只在该runner execute/_dummy_run开，exception finally reset，capture/其它模型与作用域原路。只有M2048/N12288/K2048、A(2048,1)/B(1,2048)/C(12288,1)、同device0 BF16、指针16align/storage分离且actual LibEntry热entry的完整BM256BN256BK32SK1/w16s2ctas1/EVENtrue/UPfalse/无hook完全一致才走group8；cachemiss先原调用，让原DB与autotuner选择，entry变化/其它C0全回退。newcompiled cache不持A/B/C，每call用当前26实参；真实改PID实现，不是切换已有backend。

必要CPU合同仅一次：service-cpu-check.json保存原prefix完整/漂移拒绝/compile、提取actual LibEntry.key的fake pointer双调用当前A/B/C、C0变化/cachemiss/capture/无scope/tuplegrid fallback和ContextVar恢复；没有import Torch或设备，不能当模型/FP证明。service-package-check.json保存一次真实归档213文件（含归档base-revision额外一项）复制到215，只runner footer变化+policy/runtime两个新增，其它SHA全同、现有output拒绝。builder锁原080656路径、5核心和3素材/helper SHA，纯stdlib copy/compile，不覆盖原code/协作库/installed/default。pycompile/--help过；systems既审44fc/4ab也审e007，未跑suite/GPU。

中文analysis/2026-10-22-mm-cta-group-service.md保存完整证据、文件身份、挂点、恢复与root命令。root纯CPU build需原policy06c7+runtime44fc+source4ab+buildere007+helper0ecf；输出runner7876。短service建议原context-screen16K32req128out/seed721201匹配热DB/当前C0/KV，原服务参数不改。外层launcher必须export BIV150_MM_CTA_ARTIFACTS="$control/mm-cta-artifacts"，driver --require-log-marker BIV150_MM_CTA_GROUP_READY；每PID存源/C0/resources，必须benchmark真实execute中REAL_SELECTED，不能仅dummy FIRST。新kernel需测量前已编译，否则测外warm或冷窗口另记。shutdown/atexit不一定TERM执行，首次status不能当最终总计。全部已发root串行上卡，本owner不GPU；当前此新服务入口未上卡、无accuracy继承。

### mapped运行时初审与一条明确纠正

已只读mapped source0433a8de/派生67a983与当时磁盘runtimefab3c673；地址3种行号、compact scratch、base_forward一次经context代理分两unified、异常finally不重试、producer wait/record_stream及plan强ref无明显阻断，仍等待其最终runtime/gate审阅。原C3 build仍先执行，prefix非空时旧suffix_cu准备会保留，不能在性能说明中当作已消除。

**纠正本人聊天中的错误推断：base_forward不含KV写，也不能推测mapped少一次KV writer launch。** framework owner指出后，本人实读actual1219 forward结尾及do_kv_cache_update:724–768：writer独立于forward，forward只读cache并调用unified_attention。该“少writer”推断已撤回，已发owner，未来报告不能继承它。本轮没有修改mapped文件或运行其设备门。

最终mapped交叉只读审阅已完成，四文件均实际核hash：runtime7bf4e1337b0afe7a425204a4424ff76e05ebd143feed9d00d809daf9c5d61d47、source0433a8de0d1e42962d8c8c1ef671f2937107dfb5ae144447cd5f13df9b10811e、derived67a9830eaa976e79d9d21f5f34ec4bbfe0215d3082d6571d415c1c8f33a85f47、gatec2ded9b854608aedb15b6279d5c84195f0a0698b49117d2b05d155216b4e98bd。基于实际codefile/unwrap身份、C3 prefix/threshold64、d/r/t/compact scratch/N-D边界/显式C2配置和scope，未发现进入root最短correctness设备门的阻断。plan保持CPU/GPU map强引用，consumer wait生产流并record_stream；ContextVar finally reset、已选路径错误不原路重试。

gate全文核4shape D29非prefix/D1尾/D1中/D64N65：原2D全batch加独立compact原C2按t回填作oracle；actual writer整KV期望、slot-1/NaN尾、全out bits/skip sentinel/prefill三FP32行/KV/RNG；同cache真追加16384→16385后的纯decodefallback、跨流释放map+churn、mixedcapture原2D回退。optional timing确实含原C3 builder保留的unused suffix_cu和新map H2D、32call预recordABBA；默认不加--timing，root先正确性。未重跑owner源合同或任何suite/GPU，不把CPU审阅当设备通过、完整模型准确率或性能结论。已发framework owner与root，最终包装由owner负责。

本轮最终交接已完成：CTA gateup服务runtime44fc/source4ab/builder e007及短service要求已发root，systems双重互审完成；独立mapped实现/门也只读审完。尚待root串行的CTA服务实测与mapped设备门，本owner无设备作业/PID。prefix-mask仍明确下项计划而未写runtime，继续保留用户“小收益也上卡并保留”的要求，不与本次CTA或mapped混测。

### 182916 CTA 实际模型命中与原 compiled hash 取证完成

本节覆盖上一节“未服务”的历史状态。root已完成 `20261021T182916Z-mm-cta-group-context16k`，原run/control包SHA256为 `96074323f386817d460bdefd0982c44ba5f58c3f760c07c0e81604364215ccac`。root回执32/0、118.41752643秒、KV容量521840、DB三项SHA不变。本owner本地逐项核control的413份源SHA、5份每PID文件和日志：group8 compiled08afb545…与180646门相同，实际模型REAL_SELECTED delta42、total2048、requests1。首个真实命中刷出的status只证明当时selected/real计数，不能当TERM后最终总量；此处不从单个时长声称服务因果收益，匹配pair由root持有。

服务原compiled23d5fd…与门原3639b8…不同，root授权先列精确cache/source路径，设备结束后一次只读取证。root实际归档 `experiments/source-audits/20261021T183920Z-compiler-cache`，包SHA256 `eb19121a54593fa3e52b37ec41900487c656f7398a65e09ddb061f23ac9587c6`，实际collector SHA为 `685e6d107f8d96fe5bd5e4f67bb15b5313ec4ee946a2e6a63ea89b17992b892b`（归档collector.py为准）。我在其执行前后衔接期间将本地collector增加了非敏感env白名单，当前本地02187d04…不是本次实际执行版本；已承认该交付版本协调错误并告root，**后续已交付脚本不得不经root协调再覆写；旧run原件和SHA保持原样**。0218只作为未执行补充，不把它写进旧记录。

新增一次纯stdlib取证复核 `analysis/source/mm-cta-group/review_compile_cache.py`，SHA `8d9a7b9d17da7996e084fa6f53a224998b3db717455d6f2f4a50585dc5a220d5`，结果 `compile-cache-review.json` SHA `0324315287afd29e112690aec6f8ae5a0e048bda7504b6c3a7a55b41046fe960`。32份已归档source/cache SHA全符；metadata仅hash不同，其余全部compiler options相同（use_sme7）；原完整函数体byte同，三MLIR阶段只删调试loc定义后同，LLVM只删源码调试定义后同。自行解析ELF64表，全部SHF_ALLOC段payload/type/flags/size相同，8,016B `.text` SHA同为 `e29f72a3564ca0df74e94467a37cddae274641914f3655a1bda65385a4425210`；整个cubin只.debug_info/.debug_line两段不同。实际spec JIT :503 inspect起始行、:549把starting_line_number纳入cache key，原源码decorator50/def78 vs提取20/21与调试身份差异一致。只证明这些exact条目/配置机器码相同，不泛化所有hash差异，不新编译/GPU/模型accuracy。

完整中文报告 `analysis/2026-10-22-mm-cta-compile-cache.md`，CTA service说明同步真实状态。公开Triton v3.6.0 jit/compiler/cache仅机制一手参考，本机结论以actual spec SHA66a168ae…及本次cache为准。已先将结论发root，没有测量期间扫cache，也未SSH。

### mapped 编译失败根因、最小修复与隔离服务包装终审

183421旧mapped门失败发生在首case结果前：派生skip2D fresh compile将68954357763（0x100e000003）传给SME pass而超32bit。与framework owner共同核actual spec `get_corex_sme:31–68` 和freshcompile :761：该选择器按非constexpr operand位置，为满足布局的多维BF16等tensor置bit；旧derived在MAPPED=False时把新增decode-map dummy设为二维BF16 out，位于第36个operand，恰增加2^36。原attention/prefix mask为234881027（0x0e000003），broken精确变68954357763。不是推断backend默认0或猜测环境；actual JIT会计算并传mask。

framework最小两行修复只是两个未使用dummy从out改为现有一维int32 cu_seqlens_q，真map仍为一维int32；没有关闭/覆盖SME或改选项/FP。本人对旧归档source与新件独立diff及核hash：transformer `919e80abf5b95c55ea63aa8619fa3202cd78b0c4cc0e303df7b4197bf1898316`，derived `72713a90584bc6567706fb881188afa04335230afc13e021c10f862f88d054a1`；runtime仅pin变为 `d085ad6dcc0fd5dc26188d3e0f5801b8e394dc07a79c05a376192ec9e1e95b4b`；gate三pin变为 `ede4519424d467bb4f47f52cb57429c5e489ee2324070c482225cc0499b0dc2f`。owner的actual selector AST+CPU stub复算精确匹配数值，我未重跑旧suite或设备。原失败source/raw不改，复核后支持root最短修正版门。owner回执184809四case通过、185023单层timing wall13.31%/event12.76%信号；此处明确是owner回执而非我独立读取全部新raw，更不等于E2E。

当前已全文终审 `scripts/remote/prepare_mapped_decode_source.py` SHA `a41c3858ac5d19ffbb385d9ad075635b560fb272af2c2d6b5c490f04713d2459` 和root新 `launch_mapped_decode_screen.sh` SHA `3455b8d1620305be1af6faa7336e4e785820af01d394ad187c0154e0277cdce0`：owner0ecf完整source_files/内部regular alias规则、原080656七core及五BIV精确集合、修正四件pins、仅runtime/source/derived三文件入包、派生runner3566099b2f336f3e7ae768adeca5b0da169748324fec26fc00b150b26b246a73、全新直接目录/全输入输出SHA，无当前阻断。launcher固定buildera41c/driverbc51、原context16K/seed721201/服务参数、无新env，idle和双栈9031预检后由原driver flock。INSTALLED是启动门，仍需真实 FIRST_SELECTED real_execute=1；不把purpose字段当实际命中。已先通知root可串行上卡，root当前185627是唯一设备作业。未重跑owner打包检查或GPU。

### prefix-mask 小收益独立服务入口已冻结，尚待 root 上卡

本节覆盖旧“尚未实现”计划，落实用户“小收益也要上卡并保留”。保持原受测policy `87c6a31075939c551402d7007b491546a215584a58ec82caddc08fc7249998d6` 和generated `a6d3604aaf3896dce150b8ef56253a3d0fa12dd89095740bb1ec99ce975ddaa2`，原121838两shapebits/KV/RNG/padding/3DC2回退通过、小层wall0.275858%/Event0.453959%信号，不新增数学实现、不重跑旧门。

冻结文件：runtime `patches/framework/biv150_visible_prefix_service.py` SHA `7258ad7929ad22676201fec045184f0038be4689f2eef3a51b21e30c658029da`；transformer `biv150_visible_prefix_service_source.py` SHA `464b9ea73f6961097c1cde2c92d97bdf9ed50909e9da1ecbb65f1dd437bccaba`；builder `scripts/remote/prepare_visible_prefix_source.py` SHA `a4e978770e98aa3c5a245de96470916aae570ef63a55083534465309ceaf615f`；复用helper0ecf未改；输出runner `4467ac262bb22edca90c106ae2361efe5e8917ec7115d51c07d4d3e35245703a`。新服务只在exact e155完整前缀的SQL→C2→C3后追加footer；原ctor返回后装proxy，先load/capture，strict原模型/单卡/BF16/no未知features/安全KV，ContextVar finally、capture/3D/未知路原C2。每PID唯一实验目录下create(xb)生成a6d，保存所有source hash；不改installed、稳定源或default，不叠CTA/mapped/metadata/async。

新增一次最必要CPU wrapper/source合同 `analysis/source/prefill-visible-prefix/service-cpu-check.json`：exactprefix/逆回、漂移拒绝、原87c6生成a6d、fakeinner dummy/real_large分离、小query不当免mask证明、capture/unsafeKV/outsidecontext fallback、原return与exception finally；无Torch/Triton导入，不等FP/stream证明。`service-package-check.json` 记录真实归档213→215文件，只有runner与policy/runtime两个新增变化、其它SHA全同、旧output拒绝。语法/--help通过；framework全文两轮独立只读审7258/464b/a4e无scope/C3顺序/capture/计数/包装阻断，没有重复suite。已有Scoped proxy复用仅instanceof的非阻断建议保留，exact新副本不叠其它候选，未为此扩大实现。

中文 `analysis/2026-10-22-visible-prefix-service.md` 完整记录命令、source与范围。env是 `BIV150_VISIBLE_PREFIX_ARTIFACTS=$control/prefix-artifacts`（替代早期计划的MASK变量名），原driver启动门READY，测后必须 `BIV150_VISIBLE_PREFIX_REAL_LARGE_SELECTED`：真实execute selected增量>0且单请求maxquery>=128，不能拿批token和、dummy或8token smoke代替。此标记仅几何机会而非GPU省mask计数。FIRST按compiled hash记录首次时机，测量期新variant编译需按冷窗口另记；TERM未flush时旧status不当最终数。

最短先匹配原080656 context-screen16K/32req/128out/concurrency64、seed721201、原服务参数/热DB三SHA/KV容量；代替旧优先1024out建议。不同seed测外预热避免APC共享测量prompt；是否追加1024out由root按结果决定。独立小/零/负/噪声均保留，不报未经证实E2E，不继承父基点103/105accuracy。最终代码SHA与全部要求已发root及framework并冻结；root优先当前mapped服务，此新prefix入口未设备执行。本owner无设备PID、SSH、GPU、远端导入或GitHub改动。

### KV page-copy 成本门的独立只读审阅

systems owner提交 `patches/framework/biv150_kv_page_copy.py` SHA `c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c` 与 `scripts/remote/validate_kv_page_copy.py` SHA `b86a3017373aca15f4e757ee5c2c616b91b49464c43f3ad312be3ac16db06513`。我全文只读审两文件，并核 `20261021T184108Z-kv-copy` actual backend1219 shape/stride及reshape helpera351：normal42每层16KiB页、packed42同一raw中offset=i*PAGE、block_stride42*PAGE，均是该helper支持的NHD构造；不把构造写成实际服务layout观测。初次误到170854目录查新helper未找到，随后按rg定位184108正确原件，没有改原source。

无当前阻断：coalesced runs保逻辑次序，source/dest映射一一覆盖、不排序、不分配GPU pack临时；compute生产record ready→transfer等待保存→end_save.synchronize后才读pinned并毒化源；poisoned事件后恢复→compute等待end_restore→42层actualviews clone消费者→consumed同步。raw、host、golden、views和consumer均持强引用，跨流操作完成前不会释放；返回completion_ack=false未谎称copy提交即完成。正数basic CPU全byte、guard/non-target poison判据避免此前负advanced索引oracle问题。

4个计时Event预record排初始化，timed pass的生产/poison同步在copy窗外，单方向wall计submit+完成同步，Event计copy区间，allocation/consumer/CPU校验排除；只是每构造1warm样本，不能称稳定带宽/E2E。cgroup字段准确写observation_not_peak，初步聊天的“host峰值”不可进入结果结论。控制器同锁、68/0双栈pre/post、单child/timeout进程组清理、source仅is_file符合设备owner规。已发systems和root可串行最短门；我没有重复CPU合同、suite或GPU，也没有改对方文件。此门不实现服务allocator/取消/请求restore协议，不是模型accuracy或KV容量收益证明。

### KV 门最终 d841 单点增量终审

root实读gate已变 `d841a1abbfee94a68fddc1afec8bd236b91e2831102217577fa90bd03605f8a3`，要求版本确认前不上KV；此时prefix190206是root唯一GPU。本人本地只读当前gate，内存将唯一新行 `tensor.narrow(0, 1, POOL - 2).fill_(165)` 逆换为旧的整raw fill165及两guard重写90三行，精确重建已审 `b86a3017373aca15f4e757ee5c2c616b91b49464c43f3ad312be3ac16db06513`，证明没有其它delta。policy仍c95f原件不变。

该修正只强化oracle：guard在初始reference复制后完全不再写，避免poison时重写90掩盖前序意外改动；interior 1…POOL-2仍全部毒化165，guard检查保持正数basic CPU。poison仍在计时窗外，copy实现/四构造case/布局/映射/event/强引用/计时与控制器均不变，无当前阻断。已发root和systems支持按最终d841串行最短门；没有重复CPU合同、suite或设备，原b86a审阅回执保留，当前门最终身份以d841为准。

### KV191017 包装失败保留与93eb模块改名终审

root实际191017 gate d841在任何case之前exit1，results.cases=[]。我已本地直接读其results/manifest：归档source/copy.py（policyc95f）被dataclasses的 `import copy` 误当stdlib copy，递归触发partially initialized dataclasses错误，未产生复制正确性或计时结果。**此Python归档命名遮蔽是本人初审漏项**，已明确告root，不能把这次包装失败当KV机制负面。旧run/source/d841原件保留。

systems按root授权仅将gate的4处字面量 `"copy.py"` 改成 `"biv150_kv_page_copy.py"`，policyc95f不动。本人实读新gate并与 `analysis/source/kv-page-copy/validate_kv_page_copy.d841.py` 逐byte核：恰该4处替换，无其它delta；最终gate `93eb02c7dbdaac3ec982fbf5b0dd0f24e29ebf74e73a5b48c7dc820ae0dab56d`。launcher `scripts/remote/launch_kv_page_copy_gate.sh` 全文核，SHA `ba3336e186b9f62c32b6dd053e55a4b990c17912f3c15d88cbbc2bddebf38836`，pin93eb/c95f/owner6072/monitoraf90与source184108命令对应，未增加参数或设备并发。

已读owner `analysis/source/kv-page-copy/source-load-check.json` 及两侧实际scratch源码SHA：每侧为真实source子目录、新Python进程，先断言stdlib copy尚未加载，旧归档精确重现循环导入，新归档成功且copy指向stdlib、run映射正确、无torch/numpy/vllm。此检查能排除父进程已装copy而掩盖bug的假通过；首轮Windows stderr编码收集问题和显式-Xutf8重复必要加载检查由owner保留，不是额外设备实验。我未重跑suite、旧合同或设备；已发root/systems支持按最终93eb最短重试。当前93eb覆盖d841的门版本回执，旧失败绝不覆盖。

### prefix190206 完整原件验收：同容量首次短筛负面，不集成

root完成 `20261021T190206Z-visible-prefix-context16k`，原件run/control已本地，tgz SHA `5f79f583a41af027c4c5c7a51de968657465353d1127c1300555a8ef7425662c` 本人重算相同。未改任何runtime/driver/原run；独立分析JSON为 `analysis/source/prefill-visible-prefix/190206-service-review.json`，保存原result路径/SHA、逐项条件、marker行号、shutdown记录和百分比计算。

直接核两base183543/184244的410/410份source与候选413份实际文件SHA、集合全符，candidate相对base仅runner4467+policy87c6+service7258+创新manifest；原完整prefix保留，perPID七源/派生a6d全符。三run同driverbc51/server参数/seed721201/包版本/installed/model/generation SHA、CPU6核quota、KV521936；各DB before=after且跨run三SHA完全相同，实际六份snapshot文件重算一致（1593d60c…，schemaa0a59008…，logical90e9a868…）。preemptions/APC hit均0，三端完成32/0、524288输入/4096输出token。post候选19:10:00Z为68/0、双栈关闭、413源无漂移。

原始duration/TPS/meanTTFT：base183543 `120.48498157598078 / 4385.476040985142 / 60874.43063224782`，base184244 `120.7632626676932 / 4375.370359560136 / 61145.73857927462`；prefix190206 `123.55798832001165 / 4276.4050077563625 / 63199.166325692204`。相对两base各指标算术均值duration+2.432238%、TPS-2.374615%、TTFT+3.588065%；相对单baseTPS分别-2.487097%/-2.261874%。明确负结果保留，暂不集成，不能把小层+0.45%写成服务正收益。

READY/REAL_LARGE真实delta42/maxquery2048成立，但第一条REAL_LARGE也可能来自bench初始单prompt test，不能单凭它证明主计时段；FIRST的num_seqs2/query_rows2047及16/2048则证明多请求主负载实际用了新kernel。三个FIRST为8query烟测ef393b84…、2/2047的cac38024…、16/2048的15bda8ff…，均101regs/0spill/shared65536；status selected5713等是第三hash初见快照非最终总数，不是GPU免mask次数。原客户端num_warmups0，两变体负载内才首次选中，没有全形状测外预热证明；FIRST不等cache miss/编译时长，既不能归因全为冷编译，也不能把负面归因完全预热后稳态退化。此轮准确表述为**首次接入服务短筛负面，热稳态未被本轮隔离证明**，不追加测试/新方案。

三端首次shutdown前无ERROR，candidate结束阶段forcekill与8行EngineDeadError/traceback完整保留；benchmark32/0、exit0与post空闲分别成立，不写全日志无error。完整中文 `analysis/2026-10-22-visible-prefix-service.md` 已更新真实结果与边界。此前“尚未上卡”历史由本节覆盖；保留受测policy/prototype，准确率未测、不继承父基点103/105。本owner全程CPU本地，无SSH/GPU/设备PID，root唯一设备owner继续其它已授权队列。

### KV191545 成本/计时限制审计完成，本批暂停写入

root已完成修正版93eb/c95f的 `20261021T191545Z-kv-page-copy-gate`，19:16:59Z exit0，原件到本地。本owner独立重算tgz SHA `7b491c525759e3320ecac8cd385d31fd1f434784ade63eef16bb2ab02a554316`，实际8source SHA全符manifest/results，无copy.py残留；四构造八pass共40项全byte/guard/未选页/事件42view消费者检查true，四RNGtrue，每向704643072B，实际calls42/336/1/8。actualhelper两布局描述与pageoffset匹配；ownerpost19:18:05Z为68/0、两栈关闭、8源无漂移。没有运行新设备或修改runtime/driver/gate。

原始savewall/restorewall/roundtripwall ms：normal连续25.946121/196.106984/222.053105；normal8run27.699296/207.570993/235.270289；packed连续24.943508/95.012686/119.956194；packed8run25.027936/95.688994/120.716930。对应saveEvent/restoreEvent ms依次24.756731/26.488735、25.073376/194.106018、24.734741/26.496109、24.747791/26.758972。normal连续restore wall比Event多169.618249ms，packed多约68.5–68.9ms，normal8run连Event也异常升高。不能略去异常后只取26ms当稳定带宽，不能从单次normal/packed差异报因果服务收益。

静态窗口核对：timed ready/poison同步和4 Event预record在窗外；wall覆盖上下文/wait/record/全部主机copy提交和end事件同步返回，Event仅括两record。save后restore前有672MiB CPU torch.equal检查，虽在窗外却不会重置cgroup quota周期，poison GPU同步也不重置；若主机延迟在begin前/end后则wall高Event低，在多个copy中间则Event也可能含等待提交间隙。CPU6核quota在同实例服务证据/root回执有依据，但**本门缺逐window cpu.stat/实际Torch线程数/调度与CPU时间**，不能确认本次差额由多少节流造成，host API/线程池/驻留/设备runtime因素未分离。该边界与systems独立raw终审一致。

实际浏览一手文档仅作语义佐证：PyTorch2.10 Event https://docs.pytorch.org/docs/2.10/generated/torch.cuda.Event.html 、CPU线程 https://docs.pytorch.org/docs/2.10/generated/torch.set_num_threads.html 、Linux CFS https://docs.kernel.org/scheduler/sched-bwc.html 。未把标准CUDA文档当BI-V150实测；事件正确性不等于计时无混杂，memory cgroup只是离散观测非host峰值，GPU峰值含测试consumerclone，不外推生产KV容量。

新增中文 `analysis/2026-10-22-kv-page-copy-timing-review.md` 与独立 `analysis/source/kv-page-copy/191545-cost-review.json` 保存全部数值、源/原件SHA、窗口可知/未知与归档恢复入口。结论为构造byte/event复制门通过、成本单样本且归因未知、真实服务layout/allocator/取消/restore协议未测；不新写runtime或追加GPU。

**本批完成后按root要求暂停本owner文件写入。** 当前prefix190206负结果已保留、KV191017失败/93eb修正/191545成功和计时限制均持久化。root可进行checkpoint、私有实验库同步与完整离线包；下一API先读本节及对应analysis恢复，不恢复新实验或文件编辑，直至root/用户另行授权。本owner无设备PID/SSH/GPU/远端模型导入/GitHub写入。

### 归档锁解除后的KV一手研究与实例预算

root已明确解除上一节写锁，继续用户持续探索goal；本轮仍只CPU/公开一手资料/审阅，无SSH/GPU/远端模型导入或共享repo写入。新增中文 `analysis/2026-10-22-kv-save-restore-hardware-evidence.md`，包含逐事实来源、反例、actual源码、host预算、事件先后与最短descriptor→单事务路线。

实际查询天数官方 https://developer.iluvatar.com/ 及其文档中心，找到门户/指南目录但本次未取得CoreX pinned/stream/event API正文，不断言不存在，不用NVIDIA语义补成CoreX保证。实际读PyTorch pinned/non_blocking教程 https://docs.pytorch.org/tutorials/intermediate/pinmem_nonblock.html ，其中pinned源异步H2D后改写、D2H未完成即CPU读均是反例；CUDA API同步说明 https://docs.nvidia.com/cuda/archive/13.1.0/cuda-runtime-api/api-sync-behavior.html 仅作Async也可阻塞的设计参考，不推CoreX引擎数量。真实支持证据仍是191545单例byte/event门，不称稳定带宽或硬件并行。

vLLM官方 https://vllm.ai/blog/2026-01-08-kv-offloading-connector 的H100/500GB/8CPU结果不能外推；其preemption/race修复是有用反例。公开v0.24 worker源码 https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/distributed/kv_transfer/kv_connector/v1/offloading/worker.py 和cpu/gpu_worker.py 明确compute依赖、store延到nextstep/jobs_to_flush、完成回报和资源持有，但不等本机安装实现。PR https://github.com/vllm-project/vllm/pull/29870 修被抢占旧store处理，不能只保存bytes后修改computed绕过allocator。PagedAttention论文 https://arxiv.org/html/2309.06180v1 第4.5与共享/COW语义作设计依据，不沿用早期scheduler策略或其他硬件收益。

actual184108 manifest报告PCIe16GT/s×16/NUMA0、host cgroup20GiB、当时usage2267643904B；不是整板64GiB/宿主500GB、独占链路或服务峰值。MiniCPM BF16真实42层×2KV×2heads×128×2=43008B/token，逻辑16token页全层688128B；16K672MiB，16K+1024out714MiB，KV521936总payload22447423488B=20.905792236328125GiB，**超过整个20GiB host限制**。故不能按官方通用指南全GPU KV镜像到CPU，应只极少victim slot、预留硬预算/在途和取消引用、动态余量不足原recompute；既有fixture成本不是事务可靠上下界，也不拿13758 exposure×token速度造收益。

进一步实证反例：本地稳定platform.py与183543归档同SHA `e6f231af2c90f93116ebed7a8a2ce640bcc2d4c31ba5fde2e0fa0cbd8236ea36`，81–89对iluvatar明确is_cuda_alike=False；公开v0.24 CPUOffloadingSpec要求CUDA-alike/XPU。不能由torch设备名cuda推现成native支持，亦不声称未取回的本机offload实现已测试失败；不启现成后端或改官方服务参数来代替实现。

actual scheduler df780761:1116先free、1120computed0；deferfree默认False且仅connector+多inflight消费者开启，现无connector不能借该fence。worker mixin无kvtransfer即uniformFalse，不能把packed门推真实layout；e155新页zero后才可restore。研究提出保存producer→D2H→真实ACK→free，实际新页分配→原zero→H2D→消费者等待/真实ACK→发布，资源/epoch强持有；缺budget可原路，但提交后取消需settle再回收，发布后不静默retry。CPUquota及真实布局/通道是先决证据，最短先descriptor smoke，不重跑copy四几何或扫新参数。

### actual KV descriptor三阶段独立审阅与launcher终审

framework初稿runtime3cf13981和builder已全文只读审：defaultinstall(False)不导框架，只隔离general-init footer显式True且需run目录；_dict直接对象链不RPC/proxy getattr，plain Tensor只shape/stride/dtype/device/storageoffset/nbytes/内部alias pointer，不读值、不GPU sync/stream查询/大buffer分配/调度改变。WorkerFL原initialize_from_config成功返回后一次观察；Core实际27b:110先load_general_plugins、:221才绑定step_fn，类step/step_with_batch_queue包装时序成立。保原return/异常，WeakSet once，观测失败仅诊断不截原执行；INSTALLED不等worker42/coreJSON成功。owner必要CPU合同源码/result已读，actual Worker方法AST ensure→init→observe/return/异常、once/失败原路、42fakealias、213→215完整copy/base不变/双transform与已有output拒绝覆盖必要范围，我未重跑suite。

历史已审fdf2c812 runtime/14a206 builder只加actual worker_base SHA7da443和current_stream明确unobserved；内存逆去两行精确回3cf。随后root协调hold旧pin，当前最终runtime `0c892ad02fbfe663d3f7c8f668cdd000c0c1fc7860ff915db8bce5949cae0667`、builder `936c9260724f97b02dc1e69da2f4f0da7cdfaf7fdcb0e8ab866c26d9c028c59e`；派生init `90fe0b381fd53ec5273c623d91b806a0fc21f5b84165beba0b015a1e07d53e74`不变。最新仅missing/None/Tensor三分支，内存逆换块精确回fdf2无其它delta，无当前阻断；合同finalpin对应。**事实更正已告两owner：exact e155 __init__:587/588已初始化cross_layers/backend=None，三分是未知对象的保守说明，不是已证normal缺attr。**

root `scripts/remote/launch_kv_runtime_descriptor.sh` SHA `78414492a1b053b1c88ce1f9e461bd66b0b053da33009f2cdb362a40fcab4a84` 全文终审无阻断：pin0c89/936c/helper0ecf/driverbc51/snapshot0f2a，原080656新副本/source/control/DBbefore、双栈/68,0预检+原driverflock，正确positional run_dir、原smoke-only/seed721201；env仅run/kv-descriptors。INSTALLED仅预检，purpose要求封存后worker42 complete/core firststep两个JSON；不报性能/accuracy。均已发root可唯一设备串行；**尚未收到本轮actual观测原件**，不写真实normal/packed/Executor结论。

### 私有插件本地三文件抽查与CPU事务接口互审

root仅本地分支codex/kv-save-restore（基70d04）新增c95f模块和实验文档、README历史身份说明，未push。本人只读核新增copy模块SHAexact `c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c`，文档191545/4case×2pass/每向672MiB/包7b491c/四roundtrip/计时限制/未protocol或C500均与原件一致；README区分5c14稳定历史tree及新分支，不冒称新增工具已默认启用，未改原入口。本owner未修改该repo、无重复测试。

systems独立CPU事务初稿2656及测试a993全文已读，后继当前 `patches/framework/biv150_kv_transaction.py` SHA `aeea9ff44274f6b0a982861e3d14dcb3100ccaa64ea230184dba79b3cf52f791`、必要合同 `49753260c91151c3e9bc9323f45a699935adbc0117ef5cb85a71ea8357b28ae7` 只增fresh-zero split helper，内存移去精确重建2656。Key(session/req/incarnation/attempt)+HostSlot全生命周期serial拒旧ACK，完整Operation页/bytes/epoch校验，cancel在真实settled前不放在途资源，ZERO→RESTORE→publish、发布后不私有rollback均无当前CPU接口阻断。我未重跑suite或GPU。

actual schedule先running分配523、waiting874，末1047才drain全zero集合，因此helper只保原before顺序、仅本事务独占dest尾段，真实zero ACK后才应用，避免drain别人的fresh页/后续zero擦恢复内容，必要且保守。适配器仍必须让SAVE ACK的producer fence覆盖所有将整体free旧页的在途写，不仅保存prefix bytes；旧frame原update成功后restore，实际source/privatefree成功才commit；新slot重建需新session/保持serial。当前无allocator/RPC/服务入口，CPU审通过不等GPU ACK真实或生产协议成立。关键边界已发送root和systems，研究文档一起保留。

### 195012后转实际adapter，预算采用固定护栏而非调参

root回执195012 descriptor已完成、原件在framework目录，framework负责完整独立验收，要求本owner不重复已证normal42，转助审actualadapter和预算。本人只读 `kv-descriptors` 两JSON中的cgroup用于预算：worker usage4373532672B、Core usage4636340224B、limit21474836480B，CPU quota600000/period100000。启动快照不是峰值；不把metadata当copy完成。research文档相应把旧“尚无原件”明确标成当时历史，未代做全原件布局结论。

给root和systems的可执行初版建议为：单victim/单slot，1GiB **pinned payload** cap，不改模型或比赛启动参数。页688128B→cap最多1560整页/24960token，余262144B不凑跨页。当前aeea接口先用真实issued−全部queued scheduled与known−1/真实页数求完整R，B=R*43008，超cap原路；目标16K+1024out最大714MiB，本批无须新cap搜索或通用partial-R API，不谎改输入证据。动态门按实际limit-current，初版可另留固定1GiB headroom guard：lazy分配前H≥B+guard、后H≥guard；若预分pool已计current不要双减。读失败、预算已占/不足或分配失败submit前fallback；pending/cancel至真ACK仍占slot。此guard仅保守拒绝阈值，不称已测服务峰值/生产OOM保证，不扫描最佳值；CPU maps等其它内存也不假称被payload cap约束。

平台is_cuda_alike=False只反对把上游native开关当已可用路径；**不否定本项目c95f自行实现且191545已GPU证明的copy**，这一边界已写中文研究。原report包括确切一手URL、20GiB无法全镜像20.90579GiB GPU KV、事件ACK/释放/恢复/采样和当前observer/CPU事务互审。此阶段继续只CPU，无新genericproof、无GPU请求，待systems具体adapter代码做所有权定向审。

### actual FullAttention 纠正、worker与调度协议只读互审

root新取actual7e3c接口确认needs_kv_cache_zeroing仅has_mamba，本模型False。此前文档的“原新页zero后restore”和aeea helper建议只属当时设计，被本节覆盖；不修改历史原件。原df7801046–1049不drain，manager22e列表为累计历史，不能当pendingzero；e155有zero分支不等真实执行。已告systems原草稿eligible要求True会永不激活，当前已改False、显式worker ZERO、不改历史列表。

本owner实际核SHA并全文只读审 `biv150_kv_worker.py` **31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf**、`biv150_kv_protocol.py` **592d383c9dc9d87a631ad0dd94ac53d0339e6252400e9bca717f46e1999fac60**、`biv150_kv_transaction.py` **616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13**。后继如改pin需只审delta，不能沿用这三件身份。没有本人运行CPU suite/设备，没有改作者代码或官方参数。

worker SAVE前整个device同步，覆盖将被原preempt整体free的全部已提交旧writer；strict实际UniProc在non_block RPC内先run_method再造future，无其它后台模型提交器的外推。slot/raw/pinned/event/单层核验buffer保持强引用，未settle failclosed，stale/异key不改当前slot；DROP nbytes0/pages[]与adapter匹配。显式私有页ZERO→同映射RESTORE，各真实event完成才ACK；诊断env1首个成功RESTORE42层逐页D2H/CPUuint8全字节核后ACK，单层buffer额外计预算，默认无核验，不称所有后继均已核验。

adapter default-off/exact-source、内存单waiting切口，不改installed；实际R来自issued减真实queued spans并保留末token。SAVEACK后原preempt一次，原FIFO/update成功后清各旧frame；private ref1/unhashed+本次append尾段证明，needsFalse下完全不drain/修改历史list。ZERO/RESTOREACK后暂设R，原schedule无work时原free并回滚0，有work才原cached-resume转换/发布/drop；已发布不私有回滚。592完整ACKJSON及原_update_states后cached/generator对象、输出tokens/fullblocks/CPU R检查是必要启用证据，不是准确率或全局RNG分配证明。未见最短诊断服务阻断，已发root和systems；仍待实际事务/恢复/accuracy，不能继承103/105。

**最终末次pin覆盖上段592历史：protocol `50375e899acbdcee15d3cdec2ecd77875fb355c56ccbfa663271509982ddc19a`，txn616040、worker31cc均不变。** 唯一delta为reserve_full_isl硬True→type(...) is bool，实际内存逆向精确重建592d全SHA；真实值原样传allocator，False下后继原分配失败/no-work有未发布回滚，算法不依赖True。定向终审无阻断已明确回复root，未改运行代码/重复suite。已只读owner最终adapter CPU JSON（actual f281 DTO、完整V2→cached/源切口逆回/defaultFalse/50375-616 pins）及worker31cc CPU JSON（DROP/预算/异epoch/无框架导入），不把CPU合同当GPU完成。root准备唯一context-long+VERIFY1实际诊断；本owner仅等待原件独立审，不预报恢复或吞吐成功。

### 历史new_block_ids小候选：仅记队列，不抢当前主线

按root任务查已归档actual与plugin的全部直接命名消费者：22e init75、extend276/309、take312–316；free383–410/默认new_step535无清理。2e91 take605–610只汇总，reset_prefix_cache不清；df7801046–1049唯一已归档原调用且当前False不走。CachedRequestData/runner/connector utils同名字段属另一对象；本轮协议新增读取历史作尾段证明。未取回的完整vLLM/反射访问不冒称穷尽。

历史长度随累计分配A增长，页释放复用仍追加，不受物理pool32621限制，且单manager跨42层不乘42。无重算32×(16K+128)条件估33024项，64位槽位约258KiB+list预留，非实测len/RSS；追加已有block_id的int引用，不误按每项另造int估。长期服务无固定上限；当前协议tuple/前缀证明还增加O(A)扫描，仅少数恢复发生。详细证据、反例、条件上界与未来最短稀疏观测入口已追加 `analysis/2026-10-22-kv-save-restore-hardware-evidence.md`。尚无新实现/默认修改/GPU，不能直接clear破坏当前协议尾段证据；root允许后续有限小收益候选，本轮优先worker/protocol。
