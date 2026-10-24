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

### 200957实际SAVE输入/host预算专项验收：不等恢复通过

按root委派只CPU读真实 `20261021T200957Z-kv-protocol-context16k-long{,-control}`。worker31cc/proto50375/txn616/copyc95f实际control源SHA全与受审一致；未重做全source/DB/official验收。新增独立 JSON `analysis/source/kv-transaction/200957-save-hardware-review.json` SHA `43567cb1d9377efa109d435e9af6d0cd7f5f8a81e63cb6f2887243d06b963c72` 保log5a532c9f/实际assets/页run/预算计算/局限，研究报告末节中文保存。没有新代码、设备、微测或GPU请求。

真实SAVE1044唯一正页/16704token/718405632B=685.125MiB，submitted=transferred=nbytes且ACK successful/completedTrue；SAVE_ACK_FREE后DROP completedTrue/hostheldFalse。无ZERO/RESTORE/发布/回读，VERIFY requestedTrue不当核验通过。restore_skips1没有reason，明确未知，不猜具体DROP分支。

原序24段=37/757/126/104四大段1024页+20单页；实际42×24=1008copycalls吻合，较逐页43848次少43.5倍。尾20页仅13.125MiB/1.9157% bytes却840/1008=83.333%调用，页号差31只记事实，不推调度因果。旧191545672MiB连续/8run不代表此次685.125MiB/24run，未测RPC独立wall/event/pin/producer成本，不能从完整221.1178秒拆出成本。

单层verify16.3125MiB，两者701.4375MiB；cap尚余338.875MiB；beforeheadroom15878356992B≥需1809252352B，pin后余14429618176B>1GiBguard。整体cgroup usage涨1381.625MiB，比显式额外680.1875MiB，无法归因或当峰值。预算允许SAVE是实证，但CPU长期余量/恢复成本/accuracy仍未证。root当前优先systems最小暂态保留修复，待新SHA定向交叉审；本owner不动50375受测原件。

### root新授权的后继候选：按段/调用预算选前缀，仅设计

新中文 `analysis/2026-10-22-kv-fragment-aware-prefix-plan.md` 只记录一个可证伪方向，不实现、不混入当前暂态修复。已实际浏览一手v0.24 guide https://docs.vllm.ai/en/v0.24.0/features/kv_offloading_usage/ 及CacheOPT v1 https://arxiv.org/html/2503.13773v1 第3.5：只借同硬件/模型的swap与重算成本权衡，不搬A100/OPT交点、排序、预测或nativebackend。

先用真实plan_snapshot得到R0，再按原source_pages逻辑前缀k选择：Csave(k)=42×(1+物理不连续次数)，B(k)=688128k；给定调用/bytes预算O(m)找最大k，保同Key/全部pendingframes/真实knownIDs的短digest，不伪造issued或固定16K。200957的第4段末恰1024页，才有少保320token/13.125MiB、SAVE1008→168几何；J未有计时依据不指定推荐值，恢复目的碎片未知不能许诺H2D同省840calls。额外320是长上下文已知后缀重算，不是320次decode；收益必须实证省pin/提交/搬运/zero大于多算和调度代价，保负结果与新accuracy边界。当前优先新protocol修复互审，之后才由root决定独立实现/服务门；不追加copy微测或GPU请求。

### 200957后暂态保留 a1b691 定向终审完成

实际核 protocol `a1b691f52f3724b95bbcb11f5702611a17103161001bb929096c71ab4fa74751`，与 `analysis/source/kv-transaction/biv150_kv_protocol.50375.py` 完整diff，旧文件SHA精确50375。新runtime仅暂态保留/释放及稀疏诊断；worker31cc、txn616、footer不动，不混新前缀选择。pending/placeholders/budget/allocateNone保HOST并走原FCFS；原新output对rid真实scheduled>0普通work才DROP，不能只按RUNNING猜；identity/terminal/epoch/state/digest失效即丢，未settle资源围栏不变。单次reason/cheapfree明确未观测allocator_required，未引额外GPU工作。

只读唯一新CPU合同tests/test_biv150_kv_protocol_defer.py，验证原update后frame清理/暂态无work持有/普通work释放/失效释放，不模拟GPU。本owner无重跑suite或设备，未见增量阻断，已给root/systems明确终审回执，可由root串行新run；200957为何DROP仍未知，不能拿新reason倒推旧现场。研究报告同步，等待真实新版本原件；不提前写恢复成功、accuracy或E2E收益。

### 202526目的页实证与root选择的唯一映射候选（未实现）

root完成真实 `20261021T202526Z-kv-retain-context16k-long`，原件run/control本地，包430d2f7c…。本owner仅专项CPU页图/source核对：control实际31cc/a1b691/616/c95f全符；ZERO与RESTORE1044唯一正页完全同序，43848/43848calls，全42层718405632B回读43848calls passedTrue，6runnerchecks全True，原后继输出8token已消费。首defer allocation_none、free1030/placeholder0/pending0/reservefullTrue可确认；restore_skips454不是454项reason记录，不能臆断全部原因。32/0与240.929935357s仅诊断，root已报告DB516/19270→518/19337，不能作perf比较。

新增 `analysis/source/kv-transaction/202526-restore-page-order-review.json` SHA `ce5328d89cb161bcc70f2a769e73dbcb7a97e7486bced22d57254058bc3eb0d0` 保log7ace8be0、源pins/原序hash/步差/升序和反转66段。实际原序+1runs1044、相邻−1共978对、−1runs66；原序整体反转+1runs66；升序也66，含237..1027(791)、30959..30995(37)、31000..31152(153)三大段+63单页，是同已选集合最少正向段数。每42层理论43848→2772，少93.678%操作提交，**不是实测速度**。

root授权只设计后选systems实现唯一protocol私有映射升序。新中文 `analysis/2026-10-22-kv-owned-page-order-plan.md` 记录actual22e/9dd/2e91/3fc挂点与约束：actualowned[0]须是req_to_blocks[rid]同list，private ref1/unhashed/非null/唯一/num_cached0、HOST未bind无pending，无已发布alias；allocator先选/evict原集合，随后原地排序block对象，ID及对象集守恒、历史new_block_ids完全不改。排序后destination/tx/ZERO/RESTORE/readback/原get_blocks/runner表同逻辑序，host行i仍原逻辑token页i，不能只排序copy提交却声称合段。无需改worker31cc/c95f，无packing/改R/块大小/请求FCFS或其它变体。

actual coordinator get_blocks346–353返回真实list引用，manager get_block_ids另建IDs，cache_blocks353以后按该list逻辑位置赋hash，说明只未发布新页可改；已有KV/共享/已hash不可sort。free原reversed(req_to_blocks)→pool prepend/append有次序语义，**未来freequeue和可能的后继物理eviction轨迹会变**；只保证同次已选/本次evict集合不变，不隐瞒这一边界。root/sys/framework已获明确审点；我不改runtime、不上卡、不加微测，待系统owner必要单合同/冻结SHA再终审。

framework还独立审了前一fragment前缀设计无数学阻断；已把“暂无selector需新Snapshot/保持prompt-output-allIDs-count-generator/async真实输入accuracy”及APC ref0命中仍占free的条件化反例补入该文档，不把外部R分配一定更贵或200957DROP原因当已证。两设计均与a1b当前受测字节分开。

### 私有目的页排序0e2115最终定向互审完成

systems独立实现后root委派终审，实际runtime `patches/framework/biv150_kv_protocol.py` SHA **0e2115d0fbdedea64d1b911c0d6ae3b359f178004d844a8dd8088dfa4388fb86**。本人只读完整diff；删除唯一helper及bind前唯一call内存逐byte SHA精确回旧 `analysis/source/kv-transaction/biv150_kv_protocol.a1b691.py` 的a1b691，没有附带早退/截R等改动。worker31cc、txn616、copyc95f实际SHA均未变。原件/旧分析JSON的SHA不覆盖。

新guard完整核真实普通list别名/numcached0/HOST未bind无inflight-pending-cancel-closed/已sourcefree/完整R/ref1unhashed非null/正整数唯一ID及唯一block对象；不匹配False保原序。通过只原地sort，post检查list身份/对象集/精确升序，之后原流才取destination；history不改且fresh比较集合，tx/worker/原getblocks-payload映射统一。marker明确host逻辑内容不变、futurefree可能改变，不能当GPU计时。无当前阻断已发root/systems，可由root单卡新源同真实VERIFY门；没有本ownerGPU或运行代码更改。

已读owner唯一CPU合同 `tests/test_biv150_kv_private_order.py` SHA29deff8d…和 `analysis/source/kv-transaction/private-order-cpu-check.json`：1test0.001s，host逻辑行/真实事务命令/对象identity及拒绝guard覆盖必要范围；未重跑suite。首次逆向检查只是LF删除数错、修检查脚本后精确，runtime没变，该失败说明保留。新排序版尚无本人设备原件，不能拿构造4页或旧20252666段当实际新run成功/性能/accuracy。计划文档追加本终审覆盖先前“未实现”的历史状态，继续等待root原件。

### 204159实际排序几何/ACK专项独立验收完成

root完整run/control已本地，包58888697…。本owner只核实际control0e/31cc/616/c95f与页图/命中/ACK，不重复framework完整验收。新增 `analysis/source/kv-transaction/204159-private-order-hardware-review.json` SHA **0cafbe28c8200dae37ee5bd5edff66e3f7e2391837b5bb2b83f884e98a34020f**，保serverlog5c3932d2、全部66runs、实际ACK/消费。PRIVATE marker真实before1044/after66；ZERO/RESTORE命令1044正唯一页同序升序，独立66段=791/37/153+63单页。排序前完整数组未独立log，守恒依据0e postassert与实际marker，不假称读到同次两个完整数组。

SAVE1008不变；ZERO/RESTORE/readback均2772，718405632B全42层回读passedTrue、doneACK，6runnerchecks全True、原8token消费、DROP hostfalse。调用减少已实证，不是理论预测，仍不等GPU实际launch trace/阶段延迟。32/0、227.548345488秒/2448.077567TPS为VERIFY1诊断，root回执本轮DB518/19337三SHA不变，旧202526基点516→518有变；不跨轮报TPS收益、不把93.678%说成吞吐、无accuracy继承。方案文档追加真实状态，四件冻结不动。

root新CPU研究已先查旧fullreserve115950/terminal181041反证，未重做。候选收敛为“完整私有页H2D将覆盖全部bytes时，明确整页覆盖状态而消除显式ZERO阶段”，root同意先独立设计，不伪ZEROACK、不与当前页序performance pair混入，不新代码/上卡。PyTorch2.10官方copy_/empty/synchronize/Event与actual7e3c、31cc、c95f/writer依赖继续审；framework配对wrapper优先互审，等待最终SHA。

### 页序成对wrapper11917最终只读审通过

完整读c7baa初稿后，root指出baseline自身DB变化不能作共同起点，framework最终只加baseline before==after三SHA并记录目的证据。最终 `scripts/remote/launch_kv_pair_screen.py` SHA **11917a047c3c3f5fadebca3898b5720224e075e3ca93bb610c258a4ef70776ad**，内存逆去该增量SHA精确重建c7baa56a，无其它改动。本人一次临时逆校验脚本误用了含中文的bytes字面量、SyntaxError；改纯Unicode字符串逆换后完成，未改wrapper/主流程或原件。

独立实算204159 control固定source清单98a72844→innovation-source3b1343ab→stable410/candidate416、preparer4c8a信任链全符。wrapper只导pin纯stdlib源/SQLite辅助；冻结源live/control完整SHA/内部filealias规则、锁内双栈+68/0空闲、DBbefore；原bc51/contextlong/seed721201/原Serve/VERIFY0，拒继承profiler变量。匹配模式要求本wrapper正常stable/源live后态通过、baseline before==after三SHA且新candidate before==该after；否则不启动，不假共同cache。

准备锁释放后由原driver重新持同锁，root仍唯一deviceowner。测后candidate DBafter/fullpost、KV容量、CPU、参数/installed源与实际SAVE/RESTORE/PRIVATE命中由root/framework封存独立核；INSTALLED不够，DB同也不等所有编译cache热。已回root/framework无阻断；我未运行wrapper或重复suite/GPU。root回执唯一GPU现205219 stable/runner221074、VERIFY0，candidate须等这轮封存匹配；不追加设备请求。204159专项JSON0cafbe已完成且真实几何和诊断收益限制已落对应计划文档。

### 新KV框架方向：完整覆盖时省ZERO，仅独立设计

按root授权新增中文 `analysis/2026-10-22-kv-full-overwrite-no-zero-plan.md`，未实现/未改冻结0e/31cc/616/c95f，绝不混当前页序pair。已读旧full-outputreserve115950负与terminal181041无机会，没重做；systems做454defer必要下界早退、framework做pairwrapper，方向不冲突。

actual7e3c needszero仅has_mamba，MiniCPM FullAttentionFalse，原df780不drain/e155不zero，不能把本项目新增ZERO说成本模型原生强制。c95f raw uint8每页16384B全覆盖、42normal独立storage/整16token页/host源真D2HACK后不变/无consumer之前，全copy成功后初值不再可观察。204159仍有2772zero_calls和685.125MiB写入可尝试消除，只有工作量潜力，缺时间，不称大收益已成立。

浏览PyTorch2.10官方copy_/empty/synchronize/Event正文，URL见方案；空内存非零保证/异步提交非完成是反例，只作API语义不外推CoreX引擎。actual1219/f182 writer按slot有效位置写、负slot跳过，不能靠后继writer兜底旧prefix；RESTORE自己的deviceproducer fence必须保留，不能删ZERO顺带丢新目的页旧writer依赖。排partialR/head/dim/bytes、Mamba/shared/alias/未知layout/旧内容需保留；R之外普通partialtail不属于这次完整覆盖证明。

设计建议显式RESTORE_FULL新操作从ALLOCATED→真实RESTORE_DONE，worker在SAVED状态先真绑定新目的map/owner/key/serial/storage，再原fence/H2D/done/可选回读；不能假ZEROACK或把phase直接改ZERO_DONE。partial失败即不publish，真settle后原free私有回滚R0，不settle保全部引用failclosed；预算、FCFS、token、RNG调用不改但accuracy仍独立。下一步等当前pair/归档后root决定是否实现和必要真实门，本owner无新GPU请求。

framework已全文只读省ZERO设计6c4f版，无数学/生命周期设计阻断；仍要求实现时全R×42 plan、host强引用/不可改、异pages/签名和取消epoch再次审。已补方案末尾，仅设计不授权新代码/设备。root当前唯一GPU205219 baseline在途，页序candidate等其封存匹配，不混省ZERO。

### 新授权容量早退的必要下界预审（等待作者产物）

root已让systems在独立candidates路径实现最小便宜早退，不改0e；framework审Request生命周期，本owner审硬件/allocator必要性。仅源码证明：strict单FullAttention，R=16P、computed0且无owned页、本次external R/no local-computed输入时，22e external分配需P个不同块；3fc5 get_new_blocks只从freequeue取，故F<P必不能成功。F>=P不保证成功，fullISL/末token/watermark/reserve还可拒；不作为放宽准入或改FCFS。单组页跨42层，P不能乘42或用显存MiB代替；ref0 cache本在F中不重复加回。

早退若延后token digest，只能保HOST/预算并走原调度，不能恢复或publish；条件满足后仍要原digest/allocator，normalwork/terminal/epoch等释放边界保留。已发root/systems此证明，尚无作者最终路径/SHA，不能预批候选或称设备已省454次。无新套件/运行代码/设备；等新差异只读审。

systems初稿已到 `patches/framework/candidates/biv150_kv_capacity_protocol.py` SHA67e4c07566ee3e52f84d6a96a494b8976d858420dadd5f833e66c3291e32fb73；旧0e归档SHA精确，canonical仍0e不改。本人完整只读diff：只加可选Request06b1类/源/三个method身份guard、非resumable/streamingNone、O1长度先失效、无owned/cachedNone或int0/R整页不超maxlen/F<P早退、fast_rejects；guard外/F>=P保原digest/history/allocator。读取actual06b1确定num_tokens为len(_all_token_ids)，ConstantList all_token_ids同底层，append只追加；framework负责更全生命周期审。

allocator侧初审无阻断：实际22e FullAttention skip0，无owned且explicit externalR/no-local-hits使至少P新页必需，3fc5 freequeue count F就是可取块数（含ref0可evict cache，不另加）。完整ISL可能要P+1/水位等，所以条件仅拒不可能，不保证通过。未取回整个环境的反射修改不冒称支持；Request类未loaded/hash或方法不符只禁快路，不import框架/阻断旧协议。尚待owner唯一必要合同/最终pin，本owner不预批最终版本、不重复套件或GPU。

### 独立容量候选67e4最终allocator侧定向审通过

runtime最终仍 **67e4c07566ee3e52f84d6a96a494b8976d858420dadd5f833e66c3291e32fb73**，独立candidates路径；本人实际逆去新增sys/global Request guard/两个helper/唯一call/计数字段后，SHA逐byte精确回归档0e2115；canonical0e不改。实际唯一新 `tests/test_biv150_kv_capacity_protocol.py` SHA **e9c57108e0e0c859ea512a6be8b851cfee78a3a8b48e0e0c5a6da43681379730** 全文只读，owner回执1test0.021s通过，本owner不重跑。它exec actual06b1 Request/Status AST及源file守卫，检查F<P不触token复制/hash/history/allocator、F==P/owned/cached/stream/source异常均原链、identity/cancel/epoch/长度立即DROP以及原FCFS真实ordinary-work后清host，不模拟GPU。

严格必要下界推导：R=16P、computed0、无owned，local-computed输入为空且FullAttention skipped=0；external分配必须取得P个不同新块，或原完整ISL gate先以至少P（可能P+1等）检查。F是真实freequeue长度，ref0 cached页已在其中；所以F<P不能完成这次原请求，早退只省本来必败前的O(R) token复制/digest和O(A)历史tuple等准备。F>=P不放行、不保证成功，仍原hash/allocator；未知Request/stream/页状态也全部回旧链。P是单组跨42层的1044类逻辑页计数，不是42×P层页数，不读NVML/MiB作容量替代。

Request前缀摘要并非删除：仅容量不足且严格immutable输入范围延迟检查，HOST资源继续计预算；一旦条件足够仍原digest核验，或原FCFS发普通work/finish/epoch失效照旧DROP。当前无设备证据证明省了454次（旧run只有restore_skips总数），不报速度。allocator侧终审无阻断已发root/sys，framework负责Request生命周期另侧终审；运行代码没有本owner修改。

root最新回执205219 baseline已完成本地，VERIFY0/32/0、DB51819337三SHA不变、KV521936、410source/空闲后态；独立11917匹配门已启动唯一205819 page-order/runner222435。尚无本owner收到的候选结果，不比较VERIFY1诊断，不混容量或省ZERO。root新跨层布局研究备忘仅后继未实现，不另扩本owner工作。等待最终pair及归档写锁；所有本轮研究/审查已持久化，无新设备请求。

最终 `analysis/source/kv-transaction/capacity-cpu-check.json` 已读、67e4/e9c5/0e/31cc/616/c95f pins全符，明示future安装须复制到**新隔离source的vllm_fl/patches/biv150_kv_protocol.py**，不能直接作为candidates子包启用（相对依赖应在原patches包）。当前尚无容量builder/launcher或新设备激活证明，后续需root单独授权/包装并互审，不覆盖0e或冒充现pair已包含该候选。

### capacity新包装终审完成，未执行

systems获root后继授权准备新 `prepare_kv_capacity_source.py` SHA **a79b69d81115dd17ba77e09f5de690cda6a9cb5288f0c200f1868ee2f5d86eee**、`launch_kv_capacity.sh` SHA **0ae8ced5c97f2460a97ac046eb808d47aa84915e80867e12c219d3dad457a32b**。本人全文与旧4c8ae1/8d7bdd定向diff审，无阻断：新输入basename67e4只映射到全新source canonical协议名，五asset/核心/init791c、stdAST/compile/fullcopy哈希沿旧规则、manifest记录输入map；原0e资产/旧包装不改。新variant/路径/purpose fast_rejects>0，bc51原contextlong/seed721201/VERIFY1命令逐字不变，root唯一owner空闲串行。

实读capacity-wrapper-check.json仅compile/diff、无fullcopy/suite/shell/GPU，未重复执行。实际必须fast_rejects>0及SAVE/ZERO/RESTORE字节回读/runner/consumer同事务才认激活；安装不算。已给root/sys最终回执，无代码修改请求；本轮设备没有它，下一轮才由root决定上卡。

### 205819实际页图/VERIFY0与六块容量未知专项终审完成

完整run/control已本地，包5e087333…。本owner实际核四件0e/31cc/616/c95f，新增 `analysis/source/kv-transaction/205819-page-order-hardware-review.json` SHA **05905a3589997903e09425b1aebcef57c9d310a906a30f1e3c49dc03be332090**，保serverlog1e31c258、原命令/ACK/全66段及三启动source/log。此次R16688/1043页/717717504B=684.46875MiB，SAVE23段×42=966calls；PRIVATE1043→66，实际升序三大232..1027(796)、30959..30995(37)、31000..31146(147)+63单，ZERO/RESTORE同图2772calls。6runnerchecks/原16token消费/DROP释放通过。VERIFY0除了command env0，三ACK均diagnosticFalse/extraPin0、RESTORE无回读字段，不冒充本轮bitwise；此前1044/1008/8token诊断不能照抄。

root回执32/0、220.921083583秒/TPS2521.515787，KV521840、DB51819337→51919340；基线205219 KV521936、DB不变。完整source/DBtable归framework验收，我只专项，不报pair收益或退化、不拿VERIFY1代对照。研究计划已追加事实和限制。

新中文 `analysis/2026-10-22-kv-capacity-variance-audit.md` 保存原因审计：三control worker同a8de、platform同e6f231，util0.85/32GiB/原参数相同；六块×688128=4128768B=3.9375MiB仅KV池差额，不当某profile项恰差该值。启动三log只有最终KVsize，缺init/requested/nonTorch/peak/weights/实际available与取整余数，连INFO可用KV内存缺失原因也未知；没有直接因果来源。按固定PlatformFL is_cuda仅nvidia，iluvatar使该worker显式graphestimate分支不走（仅局部源推论，不排一切间接图影响）；VERIFY只SAVE时读且在sizing后，没env0直接前置分配差异证据。绝不猜cache/4MiBchunk/NCCL/其它进程，亦不改util/固定KV/假buffer凑容量。root若仅一次原参数stable复核仍须全留原件，不挑最好。

**本批所有专项/设计/互审已完成，按root要求现在暂停本owner文件写入，供一致发布与ZIP；等root明确解锁再写。** 当前root回执无GPU；本owner无SSH/GPU/新tests/共享库写入。省ZERO仍设计、容量67e4+新包装只CPU准备，未混现页序pair、无新accuracy或性能成绩。下一API先读本节/专项JSON和对应报告恢复，不能从旧“在途/尚无包装”历史覆盖当前事实。

### 归档后新轮：capacity实际机制与显式RESTORE_FULL交叉审

root已明确解除上节归档写锁。212106容量独立真实门已由root唯一设备owner启动，runner224783，隔离source `kv-capacity-20261021T212106Z`，固定67e4/a79b/0ae及VERIFY1；本owner尚未收到完整原件，不预称fast_reject命中、恢复成功或性能。待本地run/control到齐，只独立核实际容量必要下界分支、原分配回退、完整恢复ACK/消费与诊断身份，不重复owner完整源/DB套件，不进行SSH/GPU。

root另授权后继RESTORE_FULL独立副本实现，framework负责worker从31cc、systems负责事务从616和adapter从67e4，本owner交叉审三者。所有受测canonical与当前capacity源冻结，暂不新builder/设备，仅双方一项必要联合CPU合同。旧省ZERO文档“尚未授权实现”是此前历史状态；当前只有新独立副本被授权，仍没有新设备结果。

已全文只读worker初稿 `patches/framework/candidates/biv150_kv_full_restore_worker.py` SHA **5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477** 及冻结c95f。初审无当前覆盖/同步阻断：FULL资格由worker实际normal42/raw layout、42份整R pinned uint8 host、精确storage边界/唯一层storage及PagePlan全页一一对应验证，不仅信任客户端bool。SAVED入口先强持destination/fullplan并置BOUND，之后保原自身devicewide producer fence→H2D→真实event→可选42层回读。accepted后的异常进入FAILED并真settle，不能半写后降级执行旧ZERO/RESTORE；未settle保持host/raw/event/map引用。原ZERO/RESTORE路径保留。SAVE的五项capability仅用于提交前选择，不能当已执行FULL或完成凭据。

已将此初审发root/framework，等待systems事务/adapter初稿、唯一联合合同及最终三pin后定向终审；本owner未重跑suite、未改任何runtime、未请求新GPU。完整覆盖与性能收益仍须未来独立真实门，不能从省2772次zero_calls推算TPS。

### 212106容量实际机制专项验收与VERIFY0包装终审完成

完整run/control已本地，root包8e04b0b6、清单73e5d880。本owner实际核67e4/31cc/616/c95f和原log，新增中文 `analysis/2026-10-22-kv-capacity-mechanism-result.md` 与 `analysis/source/kv-transaction/212106-capacity-hardware-review.json`，后者SHA **e96487e14917020bceaef83e9467eab03e41c93e02816ea17360783a863b2a4f**。server.log SHA16d041a2，首capacity_lower_bound F1039<P1043；实际fast_rejects462==restore_skips462，未逐次记录F，不推广首读数。受测源码唯一增量证明462次严格快捷拒绝，不能变成CPU毫秒/TPS。

本轮R16688/1043页/717717504B，SAVE23段/966calls；真实目的升序66段=796/37/147三大段+63单页，ZERO/RESTORE同图各2772，VERIFY1全42层717717504B/2772回读通过。原Attention前6checks全True、原输出后16token消费、DROP完成hostfalse。真实ACK四命令serial1..4及key/页/bytes逐项核对；原件从未含新FULL，不能混用。32/0、227.191134395s/TPS2451.926663为诊断，不报收益；KV521840、post68/0/双栈closed/416源零失败。完整DB/源后态归root/framework，六块容量profile原因仍未知。

root新 `launch_kv_capacity_pair_screen.py` SHA **be934c108131fd754aea2468a555ad5852068a6a3d734a7df6aafbb7633ca93e** 已只读终审无阻断。只有reference212106/manifest73e5/protocol67e4/buildera79b/variant和输出名替换，内存逆换逐byte精确回11917。独算73e5→innovation包5bef5daf→stable410/candidate416完整链；原DBbefore==after三SHA及候选before匹配门/锁/bc51/VERIFY0不变。已发root可串行先baseline，本owner没有执行或新增suite/GPU；这是stable对累计capacity候选，不能单独归因早退，未来容量匹配仍待实际。

### RESTORE_FULL三方最终静态终审通过，CPU合同身份明确

最终实读SHA：新worker **5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477**；新txn **84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883**；新adapter **1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8**。均在独立candidates文件，原受测67e4/31cc/616/0e无改。已完整读相对基点diff与实际helper/状态实现，终审无当前最短真实VERIFY1门阻断，回执已发root/systems/framework。

覆盖资格由worker真实normal42/raw完整layout+42份整R pinned uint8 host/storage+全页PagePlan独立验证，非客户端bool。adapter只真实SAVE完成ACK取descriptor并核私有list/numcached0/未发布R×42bytes后选FULL，缺资格旧ZERO；txnALLOCATED→RESTORE_FULL_PENDING→真实同operation/bytes Receipt→RESTORE_DONE。workerSAVED入口先绑定map/BOUND再保原自身devicewide fence/H2D/event/回读，accepted后任何失败FAILED并真settle，不能半写后回旧路。缺proof/未settle保inflight与强引用不free不publish，settled失败原privatefree+DROP，cancel等真ACK后回滚；fullsuccess明确未ZERO/0calls/coverage/destbound。

唯一联合test **0035b97f5331083001409871165a66e364c3c1a8f956182e2080d53520e65a54** 及 `analysis/source/kv-transaction/full-restore-cpu-check.json` 全文只读，owner回执1test0.002s，本owner未重跑。合同调用实际parser/coverage helper/c95f Plan与proto/txn，但TensorDescriptor和RPC为CPU stub，不执行worker.rpc设备事件/字节，不能把它称真fence证明；本owner源码审只确认依赖保留。设计报告追加当前独立实现状态，旧未实现历史不改。目前没有FULL新builder/上卡/accuracy/吞吐结论；root后继独立门须真实FULL ACK、零ZERO、全42回读与消费者，不混当前容量VERIFY0 pair。

### FULL独立包装终审与一条调度硬件反证

root继续授权本owner只读审新包装。最终 builder **b4e04e504e0ffda195913a267ca39b87562c73f30bb71e8dbf304392de0ebbd3**、launcher **63947c7fc1c7bc423ceb41d99fb50bcd5b5560442609d76e597ccd5c5fd52bfe** 实读hash、全文与a79b/0ae diff，未见当前阻断，已发root/systems。三个独立full_restore输入84be/1aff/5d9a只映到全新source的canonical transaction/protocol/worker，原相对导入可解；helper0ecf/080656/e155/init791c/完整copy校验/新目录拒覆盖沿原规则。driverbc51/contextlong/seed721201/VERIFY1命令逐字相同，purpose必须同一事务SAVE capability→FULL真ACK/noZERO/0zero_calls/42字节回读/runner/consumer。旧0e/67e4/31cc/616与包装未改，当前213016 stable唯一GPU；本owner未运行shell/fullcopy/suite/GPU。上节“无builder”为此前历史，现仅CPU包装已准备，仍无FULL设备结论。

root另要一条硬件约束供framework研究prefill/decode节奏。新增中文 `analysis/2026-10-22-prefill-cadence-hardware-constraint.md`，只读primary Sarathi-Serve作者v3/USENIX与vLLM0.24官方文档，交叉actual54c/59d9/df780/C3。核心反证：54c已经BQ16独立querytile；若新chunk起点16对齐，ctx+localqpos守恒，helper longestprefix/loop_hi同原query分区，不能把Attention逻辑KV tile数按chunk数倍增，也不能把GPU实际HBM流量当已知。真正可能新增forward/metadata/MLP权重与CPU提交；16SM/6CPU配额、FULL_DECODE_ONLY和C3原分离Attention路径均不能套A100“小chunk decode免费”。无新策略/测试/扫描或设备请求。

framework owner正在做唯一精确整数tileloop模型，本owner明确未重复枚举；其指出M原2048若向下对齐反变2017..2048、增加MM shape diversity且BM256八tile未消失，留由其精确模型审计，不伪称本owner算过。primary检索曾arXiv v4404、旧本地报告路径误记，随后找到v3与真实文件，不改代码/原件。本文只提供成本反证，不承诺调度收益或恢复旧growth/terminal/overlap方向。

### 214400真实RESTORE_FULL专项独立验收通过

完整run/control已本地，包21ae6e30…。本owner独立实际核canonical三新pin1aff/84be/5d9a及c95f；新增 `analysis/source/kv-transaction/214400-full-restore-hardware-review.json` SHA **dd11ee70abb4f371951c6341eec123b34536f166ceba8d8044eb93055dd55450**，原log6f3a0eec/清单a67c717f/结果82428bec。R本次16704/1044页/718405632B，SAVE24段/1008calls；目的升序66段=791/37/153三大段+63单，FULL/42层回读各2772，覆盖/实际bytes/全部uint8回读True。

实际同key命令仅SAVE1→RESTORE_FULL2→DROP3，无ZERO RPC；真FULL ACK zero_stageFalse/zero_calls0/destbound/fullcoveragebytes齐，源码分支与真实完成/回读共同证明新模式已执行，不称全局模型无zero类kernel。首F1030<P1044、fast454，6runnerchecks全真，原消费8token，DROP hostfalse。32/0、226.79482779s/TPS2456.2112仅VERIFY1诊断；KV521936、root源416/DB51919340三SHA同/idle后态已报，不推省写TPS或accuracy。对应设计报告追加真实状态，旧“未上卡”段落为历史。

### 六块差异观察器：最终6a772a，单次原调用后恢复，无设备结果

root新授权追213016 stable521936对213616 capacity521840，再记录214400 FULL521936反例；所有profile组成仍未知。先发明确设计后获批准实现，初稿b092在general install直接import WorkerFL有提前加载风险，自查后未部署并按root同意收紧。最终 `patches/framework/biv150_kv_memory_observer.py` SHA **6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c**；无主动framework/设备import，sys.modules-only自然已加载父abstract4190武装，实际UniProc4625/Wrapper7da/已创建WorkerFL a8de/io6d8全验证后，在原RPC一次内临时包worker和CM。原返回list同对象/异常、managed包装、CM with抑制语义保持；finally worker/CM/父三处按identity恢复。缺资格NOT_ACTIVATED仍原调用一次，不干预调度/分配/池大小。

只持原CM现成profile_result的CPU snapshot/标量；无新Snapshot/CUDA/allocator/stats/sync/settrace，stdout sparseJSON记录原wrapper/__wrapped__/limitedcallchain与logger现态，不改logging或dump环境。原peak样本/graph扣减由已有值重构时明确derived；profile缺失unobserved，不填0。已查Core283→Executor146→UniProc→run_method503→Wrapper334→WorkerFL495完整链，以及init snapshot在分布式后、profile_run含dummy forward/sampler，未猜6块因果。

唯一 `tests/test_biv150_kv_memory_observer.py` SHA **0becd99b5de8c98926538a9e174ebe68b31476c3079a5c4703eea40f8dcd33d5** 最终1test0.002s。root要求生命周期收紧后更新同一合同，非新增suite；覆盖父/worker各一次、原list identity、同exception、原CM suppression、缺加载fallback、3hook finally恢复。CPU stub非真实WorkerFL/GPU。`analysis/source/kv-memory-observer/cpu-check.json` SHA **137d77ce9d4128f4f1d8471af39e49e3c59d0f2167388cfb1f26cf158928cb5e** 保存语法/禁用调用扫描/两init精确append。framework全文终审6a/0bec无阻断且未重跑，已可冻结。

新中文 `analysis/2026-10-22-kv-memory-startup-observer.md` 给精确接入：同asset分别附新隔离stable410/cap416，不动旧树；完整e043b→00e8def0、完整791c→39fb96f4，必须最后append观察footer，保SQL/C2/C3/协议顺序。新observer manifest另存完整final源/原基点，旧innovation-source原字节仅历史。root后继已授权systems准备两个只启动/smoke的包装，我已交fullSHA/签名/约束，待产物只读审，不自建远端builder/部署。ARMED不等完成，须同PID真DETERMINE_RETURN/profile_context1/原值齐/PARENT_RETURN三个restored真；新诊断仍可能有观察扰动，不反填旧因果，不改util或KV凑容量。本owner无SSH/GPU，当前无observer设备结果。

最终两个observer包装已实读hash/全文终审无阻断：builder **0ab0ce3ab3d8cde4a8e725d9fdfd3e62726fcf95613fbc1e55b850b3e48a9029**；launcher **5bdb67afe573d9ffc803e40bafcaee2e7e7fd85e8b831bb94137516e85c060fd**，参数stable/capacity。73e5/5bef完整输入链410/416→新412/418，只有init精确append与同6a observer，旧innovation保字节且新manifest记完整final图；原worker/runner/protocol/sourceguard都不动。原bc51 SERVER/seed721201/--smoke-only/VERIFY0命令，require真实DETERMINE_RETURN子串，purpose需samePID/profile1/原值齐/PARENT原list/3restored真。source/helper/asset pins与新目录拒覆盖齐。

owner wrapper-check仅compile/heredoc/两init与pins，双方未运行shell/fullcopy/suite/GPU。已回root/systems最终无阻断，仍需root另一职责审后串行实际启动及验收；不能把ARMED或两次未来诊断数值倒补旧因果。当前本owner受托实现/两包装审查与214400专项全部已留中文/JSON，等待root后继实际原件，不新增研究/设备。

### 215849 stable首次启动原值/恢复验收完成

root完整原件已本地，包f9e37bd5…。本owner独立核新412源a8de/e155/observer6a/init00e8，Engine231345唯一真DETERMINE/PARENT同PID、profile1、原int22447777996与父list单元素一致、三hook restored全True，无reject/incomplete。API231177仅ARMED正常，不当另一测量。新增 `analysis/source/kv-memory-observer/215849-stable-review.json` SHA **1ce267ebd0224f1f7d9f8f2b5a57ad9755f71e184c9b0d96cf0c57846cbedb0b**，log66241222/清单f0dfb675，报告已追加中文。

实际weights5101233152+nonTorch1000341504+peak656424960=nonKV6757999616；requested29205777612.8−nonKV=available22447777996.8→原int正确，graph0，nonTorch snapshot差一致。root WARNING30，worker/vllm_fl NOTSET无handler而propagate，前后不变，解释当前标准INFO/DEBUG静默；info_once链未解析、旧轮级别未观测，绝不倒补旧原因。derived peak5774530048仍仅重构。

最终KV521936/32621块；原返回除688128整数商32621，减池payload余354508B，仅算术一致不当实际floor实现已审。root后态412/68/0/双栈closed、DB51919340三SHA同。第一样本不能推六块因果或性能；root当前唯一220122 capacity startup，待其完整原件再比。本owner不SSH/GPU/新suite，observer全部原源与运行资产冻结。

### 220122第二样本/跨样本最终验收，进入保存窗口

root第二完整run/control已本地，包b2bab46a…。本owner实际核capacity原67e4/31cc/616/c95f、同observer6a/init39fb和a8de/e155，Engine231998唯一DETERMINE/PARENT同PID、profile1、原list/3restore全True，无reject/incomplete；418源/post68/0/双栈closed、DBroot回执51919340三SHA同。新增 `analysis/source/kv-memory-observer/220122-capacity-review.json` SHA **708079b2fdf6a9aec20ec2a5f99f8dd63d21336e6fbb4c214e5102e127de67e6**，log9caa6aa1/清单6254fa1f。

跨样本 `analysis/source/kv-memory-observer/startup-pair-review.json` SHA **0fc5509022de9d376996f11fcc8342800fc04c1410e11097a2ad9c1c4fff794a** 已保存精确递归比较：profile全部字节项、worker字段、4snapshot非时间值、derived、原返回/list及logger全部相同，KV也均521936；差异仅此范围内profile_time6.896814823→6.929859638与4timestamp。PID/源目录/variant及其路径不同是当然元数据，未假称整run只变时间。两份sourceguard actualloaded SHA相同，父/worker/CM三hook恢复与原公式都过；profile_time不是性能成绩。

结论：两次启动未复现6块容量差，历史直接原因仍未知。当前logger rootWARNING30只解释当次标准INFO/DEBUG过滤，不倒补旧现场；不因同数值归因observer/FULL/VERIFY/cache，不无限补启动样本。root下一计划把同observer纳入原参数VERIFY0对照以携带启动分项，尚未新增该包装/实验。本阶段对应中文观察器说明/容量审计已更新，受测runtime与原件不改。

**按root最新要求，本owner到此暂停文件写入，供一致发布/ZIP；目标仍active，仅为保存窗口。** 没有新研究、实验、SSH或GPU；后继待root明确解锁与新任务，不因旧“在途/无设备”历史段落重启已完成工作。


### 归档解锁后：仅研究原物理 APC 前缀复用，KVPR 的 GQA2 反证

root确认221629 ZIP完成后解除写锁，继续授权CPU研究及新共同观察器pair互审；没有恢复SSH/GPU权限，也未改受测runtime。新增中文 `analysis/2026-10-22-kv-surviving-prefix-reuse-plan.md` 与 `analysis/source/kv-surviving-prefix/geometry-evidence.json`（SHA **ff61858eac6eacf18a4ebdab60ff83494e95fed14346775d413cc5854fc74250**）。唯一后继机制是恢复前复用同victim仍存活且有原内容来源证明的APC物理前缀，只复制缺失后缀；目前只研究，没有实现、观察器或新测试，当前capacity/FULL pair不加计数器。

actual2e91/22e/9dd/3fc5已逐路径核源码：native allocator能先touch local再分external；当前1aff在native lookup前强分完整R，随后要求allprivate/unhashed。214400原SAVE206行与FULL215行数组重新计算交集218 ID、初始190 sourceID出现在destset，124.6875MiB/18.1992%只说明几何机会，**不等于H190有效缓存**；期间evict/重分配/同hash重算仍未知。严格未来proof需原hash/refcount/分配代际或真实完整42层回读，不拿ID/hash代替bitwise。ref0命中H会touch少free H、external少H，容量仍P，不能绕F<P早退；shared-ref>0不在首版。若真H为0或开销大，收敛，不做扫描。旧fragment-aware截短R方向与本方向不同、均未实现。

primary来源完整保存于研究doc：vLLM0.24官方APC设计、ACL2025 KVPR原PDF。KVPR Eq6假设MHA输入hidden与每K/V同宽；我们实际BF16 hidden2048每层4096B/token、2KVheads×128的K+V仅1024B/token，42层activation存取为KV四倍。替代比例f的H2D字节为C(1+3f)，额外投影/位置处理未计；R16704全层hidden需2873622528B/2.67627GiB，现1GiBslot与已有快照无此hidden。不能套论文吞吐，也不否定另种checkpoint/已驻GPU情形；当前不实现。

systems正准备新的 `prepare_kv_observed_pair_source.py` / `launch_kv_observed_pair_screen.py`，接续仅定向互审：capacity212106/FULL214400完整416原树、共同6a observer→418、FULL init791c已被原6a允许、不改受测6a字典/旧innovation；VERIFY0/原参数/DBbefore=after匹配/实际profile与KV后验。尚未收到最终资产，无新设备结果。


### capacity/FULL共同启动观察器VERIFY0包装：最终定向交叉审无阻断

最终builder `scripts/remote/prepare_kv_observed_pair_source.py` SHA **fc937baf735e5694ce9d75c99c200e43b26524b9c24db09ed6939fc408ca2467**；launcher `scripts/remote/launch_kv_observed_pair_screen.py` SHA **d768860b8f9d9491b6ea473ab1e0219cfb9a04351806e0cd67685b95fcdf981e**。已全文只读与原be934/0ab设计差异审，实读final没有后续delta，未发现阻断root最短串行设备对照的问题。

本owner独算原21210673e5/5bef、214400a67c/93375 manifest/innovation SHA、416条及三角色pin全真；两init均原791c，确由同6a原允许字典精确append→39fb，不给FULL另改观察器身份。builder完整source_files前后校验，保旧innovation原字节，新目录416→418，只新observer/manifest和原init末尾；worker a8de/runner e155与各自三协议模块不改。两run均原bc51 context-long/seed721201/服务参数与VERIFY0，不继承旧VERIFY1回读。

FULL必须用本launcher已完成capacity的control，同wrapper/完整418源/exit0/fullpost/双栈idle/owned PID停止与真实profile1、同PID父list、三hook恢复；DB实际重算before==after==FULL before三SHA，否则不启动。准备独占flock+idle后释放锁让原bc51重取，不自动起第二job。root另外从真实215849/220122日志运行抽出的observer_receipt通过，本owner未重复相同兼容检查或copy/CPU套件/设备。作者静态 `analysis/source/kv-memory-observer/observed-pair-wrapper-check.json`已只读，没有新增运行代码。

回执发root/systems。启动实际DETERMINE/profile值、KV容量、CPU、R/几何、真实SAVE-ZERO-RESTORE或SAVE-FULL、host释放/runner/消费者与最终DB仍需每run后验；共同观察器也有共同stdout/CPU扰动，不称无扰动。不同恢复机会/R或KV/DB失配不能把总差归因ZERO阶段。APC前缀新研究不混本pair。


### 共同observer原件验收入口与victim只读方案交叉审

` scripts/review_kv_observed_pair_run.py` 最终 **a5b7e2418a431c9e2e4907490f5f8605c94d8fe622066211448466741f545ee3** 已全文只读终审，无当前阻断；实际核其依赖2071bff3原脚本和inspect_raw单个416→418切口，保81f2原long validator，不调用旧FULL VERIFY1 inspect。418完整源集合/原footer/六a、两reference/pin/原SERVER/seed/VERIFY0、实际同PIDprofile1/加载身份/三恢复、动态R/容量4ACK或FULL3ACK、无诊断回读/几何/host释放/runner六检查/后继原consumer均有独立判定。compare逐项记录DB全链/KV/启动分项/原args/packages/CPU/显存匹配；失配保完成结果且收益字段null，匹配也仅描述总差，几何/等待差异单列，不归因独立ZERO。已回framework/root；本owner未运行raw/兼容合同或套件。

未来victim只读设计 `analysis/2026-10-22-preemption-victim-tail-review.md` **722aec0ed9cf17d1364222abbf671bc82e65c7ada379b411eeab4275f489254b** 全文审，无当前设计阻断。首次actual allocateNone、原victim选择前CPU快照必要，尚无实现或具体阈值；明确不能从聚合输入总数/请求ID猜每条长度和进展，尾部长等待与保护最早释放者存在冲突。硬件补充已发作者：实际可释放应数ref1非null blocks而非owned总数/不能乘42；不同victim真实R×43008还须1GiBslot可容纳，否则SAVE/重算成本路径不同。保原PRIORITY撤销语义、pending/FIFO/随机状态与新accuracy边界，赞同只有唯一快照先判可否定，不先造完整scheduler。

APC研究最后仅澄清容量公式是恢复R前缀下界，不是包括full-sequence/watermark/new-token的整体充分准入条件。新研究/runtime/当前pair未混，仍无任何本owner设备操作。


### 222731四MiB启动分项专项已独立通过，具体分配根因仍未知

root取回完整222731 capacity长轮后，本owner只跑一次独立内存原件核算，不运行framework全门/新suite。首轮静态取6a EXPECTED_LOADED采用literal_eval，因dict两Name引用ValueError且没有通过文件；同一问题framework独立发现并保旧a5b/first-attempt。随后本owner显式四loaded源SHA核完三份原log，JSON `analysis/source/kv-memory-observer/222731-four-mib-review.json` SHA **de35192db67a72681663f984e472e40e128d0a681fea730928ab0dff96de0574**，中文 `analysis/2026-10-22-kv-memory-four-mib-observation.md`。没有把失败当设备错误；先前只读审遗漏Name引用已向root说明。

222731 Engine233942第91/92行单次DETERMINE/PARENT、profile1、原int22443583692→父list、三hook恢复全真，6a/39fb/a8de/e155与自然loaded四源身份已实核。原log025144e6…/source-mapc9f240d9…；root包8ded4126…。比215849/220122，11项非时间差仅预期nonTorch residual/NonKV/available-return与before/after cuda/free的±4194304链；init/beforecreate、Torch reserved/peak、weights/peakIncrease/graph和logger不变。所有snapshot/worker原公式实算成立。profile阶段自身nonTorch增量三轮仍60817408B，因此4MiB在before_profile前已存在；只定位阶段/估计项，不定位具体库/进程allocation。

原returned22447777996→22443583692，/688128商32621→32615，对应KV521936→521840；6块4128768B、额外65536B使余354508→288972。installed池floor源码未新取得，记算术一致，不冒称新内部采样。nonTorch是(total−free)−Torch memory_reserved残差，绝不直接当某allocator分配trace。不能回填所有旧521840/归因long开关、protocol、VERIFY或cache。418源后态/68/0/双栈关闭子集独核，DB51919340三SHA同为root封存回执；完整链/性能由framework负责。原observer/variance报告只追加新状态，不重写前两轮未复现历史。

framework修正版validator **c0c80dcf81b2fc0727f06b43d166a61ad042916ee300511243c2aae42cb14c00** 对旧a5b只新增loaded_sources白名单解析EXPECTED_WORKER/IO、未知Name/非str拒绝、一调用替换。已只读精确diff终审无阻断回root/framework，未重跑其raw/套件，原runtime/source未改。下一FULL仍root唯一GPU/同观察器后验，不追加盲目startup或改KV参数。


### 后继victim纯观察互审职责（当前尚无待审首稿）

root在223613 FULL唯一GPU在途时正式授权framework实现默认关闭首次RUNNING allocation失败CPU快照，本owner为互审owner，不另写runtime/test。已核actual df780522–564与txn616 plan_snapshot79–98：安全R按issued减真实queued SchedulerOutput scheduled spans、再受lenknown−1上界取16整页；R<16/queue未知不能报eligible，placeholder不可替代queued。当前schedule已scheduled但尚未issued的locals不应再重复扣，单列更清楚。实际完整R须有对应逻辑页覆盖/非null；可释放容量只数ref1非null唯一物理block，不乘42。R×43008≤1GiB只是payload静态cap，不证明实际pinned内存/1GiBheadroom可用。读失败必须只记未观测、原pop/preempt/返回异常与CoreContextVar finally照旧，不改当前pair。上述审点已发framework/root；本条时新模块/builder尚未落首稿，等待作者给pin后只读审。


### 223613 FULL启动/无ZERO/同页几何专项完成

root完整223613原件到齐后，本owner只核新FULL与222731的必要差异，不重跑framework c0全门/旧suite，不算性能。新增 `analysis/source/kv-memory-observer/223613-full-memory-transfer-review.json` SHA **9f319d02d09a906916eca753862b4c90b8ea27062e5bef07d94418360f7272ca**，四MiB报告末尾追加本轮。FULL logd27de1b9…/source-map2748cb69…。Engine235489第91/92行单profile1/PARENT原list/三hook恢复成立，selected非时间profile/snapshot/worker/derived/logger/返回值与222731完全同、四loaded源同、KV同521840。更早两smoke无4MiB偏移、这两个long有偏移是观察事实，不归因long标志/allocator或回填历史。

真实命令链SAVE→RESTORE_FULL→DROP，无ZERO；真ACK zero_stageFalse/zero_calls0/fullcoverage/destinationbound，R16688/P1043/717717504B，SAVE23run966、目的66run2772。已独立逐数组比较，两轮实际SAVE源与RESTORE目的page_ids也完全相同，不只段数匹配。VERIFY0不回读，不能声称本轮42字节验证或accuracy。root/完整门负责DB/CPU/完整后态/总性能，本专项不把调用下降换吞吐。已回root，当前仍等待framework victim只观察模块首稿互审，无新runtime/SSH/GPU/额外套件。


### victim观察首稿/包装初审（非最终pin）

作者首runtime50d3b41c与中间7f83d8df、本owner已完整只读；新独立builder初稿5982a063亦完整只读。与actual a4de资格、Core27b队列tuple3、df780 None切口、txn616安全前缀交叉核，暂未见机制阻断。模块sys.modules-only、只导入纯scope helper不install旧probe，原schedule exact单callback逆回，CoreContextVar finally、一次attempt后不再遍历；元信息读取失败记incomplete回原pop/原异常，无future/GPU值/cache/predictor调用。所列payload cap/coverage是描述字段，save_success_predictedFalse，不把它们合成SAVE许可；已建议coverage可要求ref>=1，作者可收窄，无需扩大测试。

builder显式固定新增runtime与a4de两资产（实核stable410不含a4de），scope相对import闭环，完整复制/alias/newtarget/baseimmutability与原e043末尾append01c42→413新树，不叠capacity/FULL/6a。作者当前仍在唯一必要actual innerwhile合同/最终小修，**上述SHA是中间稿，不可用作设备最终pin**；本owner没有运行第二份测试或设备。最终稿/合同交付后再定向终审。


### victim纯观察最终三件交叉终审无阻断（替代中间稿pin）

最终实读：runtime `patches/framework/biv150_preemption_snapshot.py` **d38fd18e7a83aa03db43390746731c5caa0defd9b560da65f10e4454016a9124**；builder `scripts/remote/prepare_preemption_snapshot_source.py` **42958bd16759243667340e9575968a1f44e9a8553ce96c500403ad45e1720504**；launcher `scripts/remote/launch_preemption_snapshot.py` **78e21feafd029b5e04374f706703e86fe01802b32735194df282dba9595e1379**。已全文读新launcher/builder、runtime最终delta与前述机制交叉，无当前最短独立诊断阻断，回执发root/framework。旧50d3/7f83/5982仅首稿，不是device资产。

最终runtime较首稿收紧原allocate/_preempt方法身份，还把scope异常后的原Core调用移至except结束外，防给原异常附加观察异常__context__。原schedule exact87a文本仅None/break后pop前单callback、去插入逐byte/AST逆回，原locals直传；globals复制只添callback，不变原全局模块对象属性。snapshot只CPU metadata/真实queued SchedulerOutput counts与sourceFullAttention fastpath整数需求，不新allocator/cache query/future readiness/GPU值；首次attempt后不再遍历，读失败记incomplete原路，CoreContextVar finally复原。安全R留1known/扣queued/不重复扣本步未issued；ref1非null唯一页/1GiB静态cap/逻辑覆盖均单列且save_success_predictedFalse。coverage不合成SAVE许可，未来真正协议仍需worker proof/预算。

唯一合同 `tests/test_biv150_preemption_snapshot.py` **9f2ad5e399794e501dc44a2f145837672059d5bc10d67beca59584f2b97b2787**、`analysis/source/preemption-snapshot/cpu-check.json` **b172c5a1a52f78bed47b31f5a232c5f4917d9399bac5e6ee485993597893e771** 已只读。作者最后1test0.074s，真实actual innerwhile AST取出配CPU对象验证原allocate/pop/preempt/返回/同异常、禁future访问、Corefinally及scope异常context，不是完整scheduler/model/GPU模拟；本owner未重复。整copy/launcher/设备尚未执行，不能把语法/合同称已实际快照。

builder固定080656完整410，显式新增a4de纯scope模块+新runtime+manifest→413，原e043完整末尾append01c42，仅compile不import，原源码不改/新target拒覆盖。launcher固定原bc51 contextlong/seed/服务/VERIFY0与独占准备锁、DBbefore、双栈idle/control/source全hash；不叠6a或capacity/FULL，不install旧a4de探针。INSTALLED仅load前安装预检，真实failure在负载中才能产生，后验必须FIRST_CHECKED eligibleTrue + 恰一FIRST_RUNNING_FAILURE completeTrue/完整running数据及原输出/后态。没有victim选择实现、吞吐/accuracy声明或本ownerSSH/GPU操作。


### victim实际快照判读标准已准备；旧安装时序pin未部署hold

root在B2唯一上卡期间要本owner准备硬件/请求后验标准，不写策略收益。新增中文 `analysis/2026-10-22-preemption-snapshot-interpretation.md` 与 `analysis/source/preemption-snapshot/interpretation-schema.json`，schema明确actual_snapshot_observed=False，不是模拟器/新测试。按actual43008B/token/688128B块、16K672MiB、静态1GiB最多24960整页token、当前KV32615块解释长输入压力。32条恰16K无共享且同时驻留时需32768块，才有153块/105283584B条件缺口；不冒称真实已同时驻留32prompt。GQA2不消除16query头compute，16SM不能把请求数差线性换吞吐；6CPU/42storage提交与逐页诊断开销不当性能。

判读按真实event/scope/原tail索引/queued spans/R完整页/coverage先核，private_single_ref只是ref1可释放量（可hashed），不等protocol fresh私有unhashed；shared不单独释放，perrow owned不能相加当全局physical并集。F+U(v)>=N仅在failed请求保留等条件下的必要局部条件，不能作评分。当前快照不含page IDs/runs、APC有效命中、GPU completion、实际host余量/未来EOS/最终tail，全部列未观察，不追加本轮字段/套件去补。仅用primary PagedAttention4.5/7.3提供公平和小块提交维度，不重复旧TRAIL/CacheOPT/调度扫描。

随后root/framework在预部署发现Core general_plugin可能早于scheduler/Async自然加载，旧d38/429/78e三pin**未上传/未部署、现hold**；此前终审是静态语义/包装回执，不声称生命周期已实际激活。root批准最小延迟到Core首step核自然10模块/装schedule，general只包已存在Core。本owner已收新互审：ARMED与INSTALLED分开、原Core恰一次/原异常context、readerror原路/oneattempt、仅针对变更的原唯一合同，不重复旧suite。新finalpin尚待作者，不改当前A2/B2/已受测资产。


### victim首次step延迟安装最终交叉审与解读标准更新

最终新runtime **c6b3baa96db494e7c22d8c7a3f02980d06d3469c491bf850e9ebac77675204f6**、builder **ce4e9773900316c1c19c70acc2dfba5822da08bbdc9e32fa5945b76ab3a666ac**、launcher **6ec5d60bf606b8f6c9cee19a1dbce52517b086c65a4d89ad58bf55b37da10812** 已对归档旧三件逐delta只读终审，无当前阻断。实际Core27b110在__init__最前loadgeneral、137才选Scheduler、150才构造实例已核，不能假设general时Async已loaded。现在general只核自然Core/init/runner/helper并挂原Core→CORE_HOOKED；构造后首次step才sys.modules核10源/native methods/87a逆回安装schedule→SCHEDULE_ARMED。初始缺源/异常记录disabled不逐step重试，同Engine原Core在except结束外恰一调用，原异常__context__/return和ContextVarfinally保持，snapshot主体/R/页描述未变。

作者唯一合同 **014a9f6bd55609791386743ec39371b70dbdfd4fbeb255c1ca752b16751d8f5f** 已只读新分支：late arm一次、缺模块保持原异常/不重试；最后1test0.058s，本owner未重跑。新持久 `analysis/source/preemption-snapshot/late-arm-check.json` **c6aedb167f70860e89776ab8c0ac56cbf88fe798adb98bc8c3a11bd51810cf1c** 已读，含中途fixture self阴影AttributeError/仅改fixture参数的失败记录；旧b172/d38等原字节保历史，无部署。builder只pin、launcherpin+CORE_HOOKED预检/实际SCHEDULE_ARMED后验，完整新413/e043append01c42/原bc51/锁/DB/idle仍旧边界。未整copy/启动/设备，不把批准称已激活。

本owner判读报告和schema已同步新最终身份/CORE_HOOKED→SCHEDULE_ARMED→真FIRST_RUNNING_FAILURE，仍actual_snapshot_observedFalse；单位、条件容量、禁止按metadata打时间评分/无策略收益等不变。回执已发root/framework；当前A2/B2不受新观察器影响，继续只CPU互审。


### victim后验审计入口首稿只读复核（实际原件仍待）

作者新 `scripts/review_preemption_snapshot_run.py` **e0eaee2211286afe89cb2245a0aaf08ee61005e5343edbd53dd5ed79fc877266** 全文只读；未执行inspect/raw/suite。其2071通用long函数只416→413，不调用KV/VERIFY1门；固定c6/ce4/6ec/a4de/01c42、完整413集合/footer、原bc51/SERVER/seed/VERIFY0、无6a/协议/旧probe安装、EnginePID的SCHEDULE_ARMED/eligible/首次completeTrue及延迟事件链齐。逐row核queued/current/R/cap/confirmed/owned派生、failed/tail索引与derived N>F；不读Future/设备或算性能，policy_selectedNone且最小remaining明确只是合法上界。未发现上述实际门阻断。

已向作者/root指出一项条件候选语义小修：当前alternatives可能含failed_request自身，抢占它会令原循环退出该请求，不符合F+U>=N推导中“保留failed继续”的前提；应排除其ID或单列self-preemption，不能拿它证明同一种替代机会。只涉及后验解释，不改runtime/设备，也不要求新suite；最终审计SHA待作者回执。当前实际快照未产生，解读标准finaldoc583eedd5…/schema7cca85fd…仍actual_snapshot_observedFalse。


### victim后验入口最终6eb45终审完成，待实际230548原件解读

作者采纳failed自身语义小修并按root收紧同Engine四段次序。新 `scripts/review_preemption_snapshot_run.py` **6eb45eceb46405e448e1388940c238e6f1c008123e5566b158910ed4e05bdcf0** 对归档旧e0ea精确diff已只读终审无阻断：只排failed自身、解释保留failed继续的容量条件、CORE_HOOKED同Engine唯一和严格四事件顺序；原413/source/参数/逐row/raw门不动。旧e0ea字节已实核，不跑raw/suite。回执已发root/framework，后者负责唯一完整实际门，本owner只接硬件/请求专项，不重复。

判读标准与schema同步最终6eb45/同Engine事件，仍actual_snapshot_observedFalse，无策略/收益。root已自行独占230548新诊断，本owner没有SSH/GPU操作、增字段/测试或改默认。重点待读实际prompt长度而非客户端nominal16K，不能用R−16384猜confirmed输出；32条条件容量与APC/shared反例已有明确界定。


### 230548真实31running：独立硬件/请求专项完成，本批停写

root取回完整230548原件后，本owner直接读取server.log第206行Engine240315唯一completeTrue快照，逐行复算queued/R/字节与描述集合；没有运行framework6eb45完整raw门、额外suite、SSH/GPU或新runtime。原log SHA **38a2d12aa6150e122dec776b8efd847877ded5a51232312d7a1f8591ed167672**；root包 **abe046f03d462d01fbd91bb69ff506bb19149e7969416190a406d150bcfe8cc9**。framework唯一完整门另已exit0/1.465s，报告06c16d26…；本专项不重复其完整验收或性能计算。

实际31running，prompt全16384/maxoutput1024、confirmed327..569，全decode/nonstreaming。free0/derivedneed1，failedindex1；本schedule仅index0登记1token，旧queued一帧每条span1。ref1非null唯一页计数合计32620、shared/null引用全0；实际KV521936/16=32621槽，结合冻结3fc5保null1，32620+1+0精确对账。没有物理ID字段，不冒称新增全局ID并集证明；之前32615槽/32条条件缺口不能套本轮。

排未scheduled&非failed&非保护集合&index>failed，描述集合29条含tail；再要求比tail更有进展余28条index2..29。动态规则示例row2 confirmed552/remupper472/R16928/ref1页1059/728039424B，tail327/697/R16704/1045/718405632B。225已确认输出差不等于时间，R仅差224token、保存/可释放量同时多14页9633792B=9.1875MiB；物理runs/APC/主机余量未知。日志只直接采current_scheduled_tokens，未来实现仍须三当前容器实核。索引/ID不能作条件。

最强反证已给root/framework：31running未包含WAITING/已完成全列表，第32条可能决定真正makespan；抢占更有进展对象可能延后更早容量释放，合法remaining不预测EOS/完成时间；新SAVE更大/可能更碎，16SM与6CPU不提供线性收益模型。私有ref1可hashed只表示free容量，不等fresh unhashed恢复资格。建议只保framework唯一c3c11eaf设计作下一阶段受限机制门，本批没有策略实现/新测试/收益或accuracy声称。改变batch与采样行仍需新准确率门，不能继承旧accuracy。

实际专项JSON与中文解读已落盘，判读标准/schema更新为实际230548已观察（先验条件例继续保留为条件，旧d38未部署历史不改）。按root归档要求，下面SHA完成后**本owner暂停文件写入**，等待统一checkpoint/ZIP及后继解锁；goal没有停止，无新设备请求。

最终文件SHA：

- `analysis/source/preemption-snapshot/230548-hardware-request-review.json`：**74ed2f4ac3d57fa0951a12a11266c42d1a02ee90d7c1debed27aefbf4dfcffc1**。
- `analysis/2026-10-22-preemption-snapshot-230548-hardware.md`：**e59f673c1129ff26194dd91e6be18a57c6f30a552b6c01f53ab8928f0e53747a**。
- `analysis/2026-10-22-preemption-snapshot-interpretation.md`：**8f3a2247ff3845e1358360ed566615536a642ee1ab203f5280fdf4bf78eba5e5**。
- `analysis/source/preemption-snapshot/interpretation-schema.json`：**8a114ee716e5cc8bada7d5cdc685482f5025ba991936eab41457873469f94caa**。


### 新阶段：唯一进展victim候选的定向互审接续（尚待实现稿）

root已解除归档锁，授权framework从FULL1aff复制独立候选、systems做新隔离包装，本owner只CPU源码/唯一合同/包装互审，不写第二实现或套件。230548只作实际结构依据，不重跑观测/旧测试，不SSH/GPU/改冻结受测源。已直接协作作者；代码与合同finalpin尚待。

已复读actual df780522–568：allocate真实None后FCFS562直接pop，随后原_preempt/append/failed identity break；只准改变一次pop下标，j>failed使failed及先前索引不移动，且需三份本schedule容器均无选中对象。不能借用PRIORITY543–560的预算撤销。Base FULL保存队列R按旧queued spans及known−1，真实SAVE ACK方可free；选择资格ref1页可hashed，但恢复目的仍原fresh/unhashed/fullcoverage proof，两种“私有”含义不混。HostSlot实际空为key None且used_bytes0，不仅victim None；本轮worker5d9a/txn84be须原SHA不变。

重点审attempted在读取/打分前置True、guard或元信息异常原tail且无第二选择、同Request对象/生命周期/原异常context、旧排队帧不跳过。保generator身份不承诺全局采样结果不变，不称FCFS公平或收益。唯一新合同由作者执行，本owner不重复运行。最终审结论将追加本节后。


### 唯一进展victim候选72942与417隔离包装终审无阻断

最终runtime `patches/framework/candidates/biv150_kv_progress_victim_protocol.py` SHA **72942f1f0c284069492b8ee7e1ca1348743e3b9ee49e7da05b8cf9024ac610ef** 已全文只读终审；唯一新合同 `tests/test_biv150_kv_progress_victim.py` **b5a71507c742d49f34087035e50f6bd42667a847dc8ad71cb1921cd28333868f** 与作者结果 `progress-victim-cpu-check.json` **838546644dd1c11db64eccf6b9bb1e8384abd34e65fa8ad93422c6c5d888f137** 均已读。本owner没有运行合同、旧观测、validator或设备；作者唯一1test/0.092s首轮exit0，不是GPU/RPC/accuracy证明。

具体接受理由：exact87a原schedule只waiting恢复与FCFS真实None后pop两切口、删除逐byte逆回；仅变一次pop下标，不借用PRIORITY撤销。空victim且HostSlot keyNone/used0/type/maxcap通过后，在Request/queued/owned遍历前即记attempt，元数据或emit错回原tail、不第二选；guard外直接原tail，未进入计划不消费attempt。选中j>failed且不在三current容器，对象仍is scheduler.requests[rid]、actual Request/RUNNING/nonstreaming/decode，保护合法remaining最小/confirmed最大集合，动态进展tie取较后原index，无硬编码请求ID/230548下标。原pop/preempt在helper处理结束后执行，同异常对象/context；后续None仍可继续原tail，不能称总抢占=1。

queued读取真实三tuple SchedulerOutput CPU字段不触Future；R扣旧queued、保known−1，不用placeholder/本schedule重复扣。ref1非null唯一页可hashed，解释可释放容量；保存逻辑prefix资格不冒称host实际余量/SAVE成功。恢复目的仍原fresh/unhashed/完整42层proof。静态逐函数源码对照17个原FULL函数全byte同，仅_core/install接入改变；worker实hash5d9a/txn84be原SHA不变，原SAVE真ACK后free/旧FIFO帧/私有排序/FULL强引用与settle/发布/runner消费者链均保留。首段沿用“不重排请求”措辞仅按没有排序整个running理解；已提醒作者/交接，不声称victim、FCFS公平或全局采样输出不变，新accuracy仍待。

最终builder `scripts/remote/prepare_kv_progress_victim_source.py` **bbb49a069698d45dc0d4cd39c22d1e7254667ab5264da25b6cf98993b961f1e5**；launcher `scripts/remote/launch_kv_progress_victim_screen.py` **1f8a2f144ec43d21349398a31f268c174ca6de12996024539ec622679fafb996**。两草稿40d519/87230已全文读，final反替三pin实算逐byte回原草稿，无机制delta。固定214400完整416/a67c/93375输入，仅canonical协议替换+新manifest→417；旧innovation原字节保留且明确只是基点，当前全身份由新manifest/control映射给出。原init791c/worker5d9a/txn84be/e155/c95f均不改，不叠6a/c6。原bc51/SERVER/contextlong/seed721201/VERIFY1、准备独占锁/双idle/DBbefore/source/control齐，INSTALLED仅预检，root仍唯一设备owner。作者只静态compile/AST/map，没有整copy；本owner也未重复prepare/copy/suite。

新增后验入口 `scripts/review_kv_progress_victim_run.py` **f43b7c9703ba2349a4681ee0f545cfd62422ce551f68fc0ed01e67e1e18ad8bb** 全文只读，核原2071抽出的events→return合同体无丢失局部依赖；417完整map/不同tail真实选择与保护关系/选中同SAVE rid-R-bytes、真SAVE→FULL→DROP/42byte/runner+consumer均动态判定。DECISION先emit后增selected计数，因此选中该事件counter0、后续RPC1属正确时序，不按旧计数误判。原preempt只要求实际delta>=1，不强行1。尚未拿新run，本owner不产通过文件或新实测结论。

综合review JSON `analysis/source/preemption-snapshot/progress-victim-hardware-review.json` SHA **c4ae44c34636574aa707988e10e3bf1eaff6b18bb6586bfb259542f7722858fd**，列明接受理由/边界/所有finalpins。已把最终回执发root/framework/systems，无当前最短VERIFY1机制门阻断。全部只是本地CPU互审，没有新实现、参数、SSH/GPU或收益声明；等待root唯一真实门与后验原件。


### 015315在途：后验Windows路径修正接受；候选若收益小的唯一后继保留

root独占唯一015315真实VERIFY1（runner250079），本owner不SSH/GPU。systems/framework在实际后验执行前发现宿主Windows Path会把远端POSIX argv目录转为反斜杠，本owner先前全文静态审遗漏此点。旧f43完整字节保`analysis/source/preemption-snapshot/review_kv_progress_victim_run.f43b7c97.py`，未执行旧inspect，也不是设备失败。新入口 **b7ff996b5c94f85f4f9e3c8245ad30d568de8500a91a37c44a84f8710f04a2a1** 已极小diff实读：仅argv[2]比较换固定`/workspace/experiments/minicpm-s2/framework/`加合法runname，原argv==purpose/其它原参数门不动。旧新SHA及唯一delta与作者path-check证据核对，无当前后验阻断；runtime72942/builderbbb49/launcher1f8完全未变。本owner未运行新旧inspect/抽取/测试。汇总review JSON已更新新pin，SHA **9b10cb96c7c7b3b057424dea1a5cab09bff4ffcfc46061cce9bcc1a9eefc57c5**，旧f43审阅历史不抹去。

等待完整新原件后，只做独立硬件/动态R/页几何/收益边界专项，不重复完整门。不能把230548的R16928/示例row2强套实际015315；dynamic选择、SAVE同rid/R、完整42byte/FULL/消费须真实发生，VERIFY1耗时不报收益。

空闲仅读已有`analysis/2026-10-22-kv-fragment-aware-prefix-plan.md`及200957专项和actual84be plan_snapshot、1aff _try_restore（新72942此17函数全同），保留一个既有未实现的后继：按真实源页连续段预算选择R<=安全R0的完整前缀，普通重算已知后缀；不新增第二策略/计数器/测试/设备。历史200957前1024页为4runs/168SAVEcalls，后20单页13.125MiB却多840calls，42独立storage与6CPU quota使减提交工作有本地结构依据。它不是固定16K/截20页条件，015315页图还未知，不能套历史数字。

该方向若重评，须先拿本实例稀疏RPC阶段成本，不能从calls推毫秒。当前FULL已省ZERO，旧收益式不能再算省ZERO；16SM长上下文后缀重算可能更贵，static1GiB与20GiB主机限制不放松；原full_sequence_must_fit及随后已知suffix allocate可能仍需要原容量，不能宣称R减少立即突破F<P等待。保原token IDs/输出/Key/pendingframes/digest、原query位置/采样参数和真实FULL proof；较短R必须显式真Snapshot，不伪造issued/known或丢后缀。若成本无正证据继续仅设计，不为探索扩大GPU扫描。以上条件已发root，当前优先015315原件专项。


### 015315实际动态R/源碎片/FULL消费者专项完成

root015315完整run/control已本地后，本owner直接核server.log实际选择与ACK页数组，不执行systems唯一b7ff validator或旧suite。实际Engine250261/启动KV521936；原件包 **38c096b9b254ee9846364912503d197897f5357db357422813368adca493794b**。所选rid `cmpl-bench-30645957-3-0-af5095b5`（原index2/confirmed552）不同于tail index30/327和failedindex1，候选28。SAVE/FULL/runner/consumer均同Key/rid，dynamic R16928/1058完整页/728039424B=694.3125MiB；选中可释放owned1059并不意味着保存1059页，额外owned页不在安全R。

源原数组37runs/1554calls；目的排序原1058runs→65，FULL2730/回读2730，728039424B/42层真实bitwise校验pass，无ZERO。真SAVE→FULL→DROP serial1/2/3，host至DROP才释放，原runner六checks真，原update后consumer消费9个scheduledtoken（不称9个新增输出），fast/restore skip454。decision先emit故selectedcounter0、随后RPC1与设计一致。独立JSON `analysis/source/preemption-snapshot/015315-hardware-transfer-review.json` SHA **f0b949b826e44706b5926c632ba44327ccbf02da32fb8e4645d90a0a8c9d89f8**；中文 `analysis/2026-10-22-progress-victim-015315-hardware.md` SHA **1534e588bcb498ab079edeabff5ae2ee2d6ac071397139d86c305fe736c7cca9**。这些只证明机制，不推新公平/全局随机等价/accuracy或收益。

root追加要求的实际源分解已核并写JSON：前1024页3runs/126calls/672MiB，后34页34个单run/1428calls/22.3125MiB。尾字节占3.213610586%、calls占91.891891892%；没有阶段时间，不等于耗时占比或推荐截短544token。更新旧fragment-prefix条件依据，不再套旧200957尾20页/4头段，更不能硬编码16K或J。FULL已无ZERO，省ZERO不再算潜在收益；16SM后缀重算/后续完整allocate都可能抵消提交节省，当前不实现/新门。

DB manifests独核before519表19340行→after523表19474行，+4表/+134行，snapshot/schema/logical三SHA全变。root另做实体DBdiff/形状归属（M38/261等）负责解释，不能定位具体消费；本owner未重复SQLite全门。VERIFY1与首次DB学习/回读/log/页遍历混入耗时，本轮不与旧FULL作性能比较。最新用户撤回立即GitHub/PR，本owner没有任何外部写。

### 首个FULL1aff/进展72942共同6a VERIFY0包装交叉审完成

作者最终builder `scripts/remote/prepare_kv_progress_pair_source.py` **6ffb9da39f0901bc83d4c1e3a283df668f73e9c58a90b7fa565020103c36ce4b** 与launcher `scripts/remote/launch_kv_progress_pair_screen.py` **1aaf35e13d52e97742414bda4c9aaa18452f396555c373fc64b3a4ed2b4c3510** 已全文只读/实SHA核对无当前首个A/B阻断。共同214400完整416/a67c/93375基点，full原1aff/progress唯一canonical替72942；同6a原允许字典/完整791c之后append→39fb，新observer+progress-pair manifest得418，旧innovation明确仅基点且原字节保留。原worker5d9a/txn84be/e155/c95f不变，无c6/新计时器。

full先，progress强制同wrapper完成FULL control，完整418/control/live/post/双栈idle/真实observer profile1与父list/三hook恢复，再核DBFULL before=after=progress before三SHA；不满足不启动。仍原bc51/SERVER/long/seed721201/VERIFY0，准备锁退出后原driver重取，不自动重复或并发。实际R/几何/原consumer允许策略差异；KV/启动分项/DB/CPU等失配不能归因gain，VERIFY0也不能声称新42byte回读或accuracy。后验脚本请用POSIX比较避免之前f43问题，已通知作者。

汇总只读包装review `analysis/source/preemption-snapshot/progress-pair-hardware-review.json` SHA **c3bafa6acd3202b893720cf8e21df0845cb2c4883cf955d03a7e5c3545340436**。回执已发root/framework；本owner没有prepare/整copy/编译重跑/合同/原件validator/SSH/GPU/外部写。等待root首个A/B实际原件，已受测runtime保持原样。


### 020721 A在途：唯一VERIFY0性能入口3f1dc静态终审

root独占A020721/runner252046，本owner仅CPU审新 `scripts/review_kv_progress_pair_run.py` SHA **3f1dc20431272e424d7348e977a68bd1972e8ae0db3b414d51515913d15ad07f**；作者静态说明 `progress-pair-validator-static-check.json` **881ca55ec2c3c04370b299015be29f5f6896a09c5df4c0c8c014406d8f6c9dbd** 已读。全文并核固定c0实际helper返回字段/旧Name修复，未调用common/inspect/raw/旧validator/套件。无当前首个A/B实际后验阻断，回执已给root/systems。

接受边界：两侧都真3ACK SAVE→FULL→DROP/0ZERO、VERIFY0无诊断回读；A原FULL无decision、不访问不存在progress计数；B真一次不同tail且非failed/j>failed/未scheduled及保护集合关系、选择同真实SAVE rid-R-bytes/原consumer。原FULL的R/页/段/calls/fast/skips/consumer/preempt是各侧真实策略行为，不硬要求相等。比率门仅DB四端三SHA、KV、同6a非时间启动分项、原参数/包/installed、CPU与物理显存、源码只protocol+pairmanifest差；任何失配保完整原值且gain=null。即便匹配也只一次描述总差，不称稳定因果/纯copy或准确率。

固定POSIX argv和c0 loaded_sources两Name白名单已保留；无前f43 WindowsPath或旧a5b literal_eval错。汇总包装reviewJSON已附本入口与静态check，现SHA **10d2f56567a702f8e8340413262cd3d54a1862b7b881189e97fbe4b67eb51e31**。等待A完整本地原件后只独立看启动分项与几何，不重复systems唯一完整3f1dc验收；当前没有新实测通过文件/SSH/GPU/外部写。


### A020721共同6a原FULL：启动与几何专项完成，B021658在途

root取回A020721完整原件后，本owner独立直接解析memory/ACK页数组和DB manifests，不调用3f1dc/common/旧raw或suite。实际Engine252228第91/92行profile1、原worker int22447777996→父list、三hook恢复/四loaded源原身份/logger前后同（root有效30）。前端ARMED252059不是第二profile。weights5101233152、nonTorch1000341504、peakIncrease656424960、nonKV6757999616、requested29205777612.8、graph0；原available float22447777996.8/int22447777996，/688128商32621余354508，与实际KV521936算术一致。

snapshot实际cuda=total−free、nonTorch=cuda−reserved等原公式齐，before→after nonTorch仍60817408B。全部选定非时间分项逐项同215849/220122早smoke；比223613旧long低4MiB残差链。本轮回到低组不是定位long/FULL/protocol或某allocator的证据，历史6块差的具体分配根因继续未知，不用不同容量旧run算收益。

原FULL无progress decision，R16704/1044页/718405632B，SAVE24runs1008calls、目的66runs/FULL2772calls，0ZERO、VERIFY0无诊断回读，原consumer消费8scheduledtoken、fast/restore skip454、DROP释放host。DB before=after三SHA且523/19474；systems唯一完整3f1门另已通过，本owner不重跑。原件包73ca1a3d…，独立JSON `analysis/source/preemption-snapshot/020721-full-startup-geometry-review.json` SHA **ac17bfd30e2b72add3b471412346b19ef133bd083db165d6767a80d0d82e7d5d**，中文 `analysis/2026-10-22-progress-pair-startup-geometry.md` SHA **3161938bc8821eceb7cb53af339b157ad5ba8911acc4ece79a37d118ee1c9494**。

root现独占B021658/runner253641，仍6ffb/1aaf/418/VERIFY0，A before=after=B before三SHA门通过为root回执。完整B原件尚待本owner，只待独立同6a启动/动态selected几何及环境失配边界，不要求R/consumer/runs相同、不套01531516928。本owner没有SSH/GPU/新门/旧测试/外部写，受测源不改。


### B021658独立内存与动态几何完成：首对环境失配，本阶段停写收口

root已取回B021658完整run/control，包 **c6989051d9caa8e2dac548e88e85b155fab1d95c0bbacc32f4523eea97e46176**。本owner直接解析新server.log、真实ACK页数组与DB manifests，对照自己已核A020721；未运行systems唯一3f1dc完整validator/旧raw/suite，没有SSH/GPU/外部写。独立JSON `analysis/source/preemption-snapshot/021658-progress-startup-geometry-review.json` SHA **7a2469dd101bb9f335b64a710828615d4f048a57b8a6a81c02d6dea1b182a231**；A/B中文 `analysis/2026-10-22-progress-pair-startup-geometry.md` 当前最终SHA **b77cdb1d76ae08a73a76c733d8a2beaa60d85780dd51f2f1637961d4d6497413**（覆盖此前A段时的文档SHA，原A JSON不改）。

实际Engine253818第91/92行profile1/原int22443583692→父list/三hook恢复，四loaded源与A同、logger前后同。init/before_create、Torch reserved/peak/weights/graph均同A；before/after_profile的cuda及nonTorch残差均多4194304B，profile自身nonTorch增量仍60817408B，因此偏移在before_profile前已存在。nonTorch残差1000341504→1004535808、nonKV6757999616→6762193920、原available int22447777996→22443583692。/688128商32621→32615，实际KV521936→521840（6块/96token）；6块4128768B，另65536B令余354508→288972。仅阶段/残差分项链吻合，不定位具体库/allocator/进程或归因72942；不能将所有历史同容量原因回填。

本次动态选择不是旧015315 index2/R16928：failedindex20、selectedindex21（rid `cmpl-bench-1aa8c016-16-0-aa813076`）、tailindex30，候选9。selectedconfirmed392、tail319、max561，selectedremaining632/min463，真一次不同tail/非failed，后方未scheduled源码门与实际事件成立。选中ref1owned1049，但安全保存页数为1048（R16768）、payload721158144B；不能混旧015315 R16928的1058页。

真实SAVE26runs/1092calls、排序目的1048→66runs/FULL2772calls，无ZERO，VERIFY0无诊断回读；同selectedrid/Key串SAVE→FULL→DROP，host释放，runner六checks真、原update后consumer9scheduledtoken（不称新增9输出），fast/restore skip462。A对应R16704/1044/718405632B、24源run1008calls、66目的run2772、consumer8/fast454。这些策略行为允许不同，不应硬相等；同时容量已失配，不能把这些差异单独归因victim。

实际DB A before=after=B before=after三SHA全同，523表19474行；但KV与共同observer非时间启动分项必要环境门明确失败，**不计算正或负收益，gain=null**。不追容量、不改参数、不追加盲重跑；VERIFY0机制/同DB不补成accuracy/公平/全局采样或因果证明。root负责完整raw后态与本地checkpoint，用户已撤回立即GitHub/PR，本owner未做任何外部写。按root阶段收口要求，本条最终落盘后**暂停文件写入**等待统一保存或新指令，goal未终止。


### 唯一新CPU研究：实际正等差页段与2D异步API设计已落盘，等待检查点

root新授权只读研究“保留全部KV、按实际等差页号减少提交”，不是恢复截短R/改调度或现有runtime。先对analysis/docs/patches/scripts用memcpy2D/srcPitch/等差段等精确词检索，未发现已有同路线实现/实验；旧layout备忘是跨层布局、旧fragment-prefix是缩R重算。已读两旧doc区分，不重做其设备/套件。

015315与021658实际SAVE原数组各只取已有log，保2个长连续run，其余单页按原逻辑顺序左到右取最长正恒差段，逐段展开精确还原原数组、无sort/drop/recompute。得到37→11段/层（2线性+9二维）、42层当前copy_方法1554→假定显式每段提交462；26→6段/层（2线性+4二维）、1092→252。R分别仍16928/16768、全部728039424/721158144字节不变。最大step2049需spitch33570816B；各自最大等差尾确有step31×19页，本组不重叠左到右cover将首行归前段而使用末18行，不声称最优/所有最大区间。源ID/分段/重建证明与未知项见 `analysis/source/kv-pitched-copy/save-arithmetic-evidence.json` SHA **489f1468956ff96e86188feeb89933df0ab5d35458b8d184b6adbb2729497dbc**。只计算一次离线整数几何，不是运行时planner或测试suite。

中文 `analysis/2026-10-22-kv-positive-stride-2d-copy-design.md` SHA **2a1751157b5b513d14b4bcb748f83d7d1ca9f3b632e5af75a56393b2cff496e4** 保留NVIDIA官方runtime memory API与api-sync契约的直接链接、FlagOS Corex4.5清单与天数官方文档入口；NVIDIA约束不证明Corex可用/效率，公开检索未取得具体Corex pitch等完整限制也不代表API不存在。指针/width/height/spitch/dpitch按真实raw+host offset逐行映射，不复制跨度洞；42层独立storage仍分开。copy_视图不等于显式2DAPI；若后继实现需actual头核实的调用桥，保原SAVE producer fence/强ref/同当前stream真实event/失败settle，返回提交不当ACK。FULL原恢复数据布局可保原，不允许中途新API错后静默当未提交原路成功。当前worker/txn/c95f/协议/原三run均未改。

root补的两份纯CPU现场证据已读且实SHA核：export2334a167…实库d39d5796…有cudaMemcpy2DAsync/_ptsz GLOBAL FUNC；header e29cd7a7…中mapping ca962a…把cuda入口映ix，ix_runtime_api7dca9b91…457/1046有实声明void*/size_t/ixMemcpyKind/ixStream_t及PTSZ路径。已把“存在导出/声明”与“设备可用/正确/收益未证”分开；剩余stream typedef/enum/callingconvention、映射后符号与链接、PyTorch当前stream/PTSZ、Corex maxpitch/height/alignment与实际32.015625MiB pitch仍未知，不猜ABI。读取worker末段的一个本地只读命令上界越过末行导致IndexError，所需源码已打印；没有修改文件/运行库或设备，也未把该读命令记作测试通过。

反证：API内部可能仍逐行提交，可能占SM或阻塞主机；COPY次数不等于DMA描述符/时间，减少方法/API调用不换吞吐。当前95–96%GPU利用与16SM/6CPU/42storage只提供主机提交动机。保R不降低完整准入容量、不省原454/462等待，原FULL已无ZERO；本轮无阶段时间，不给收益。root要求本地检查点，本条落盘后停止继续检索/写入/实现，无新GPU/SSH/库加载/外部写；后继桥/copygate由下一阶段单独决定。

### 检查点36510ed6后：单层实际2D SAVE门已准备，待root唯一设备执行

root解除写锁并明确批准独立planner＋实际SDK编译C batch桥＋最短单层设备门；没有授权修改worker/服务。root补实际ABI原件f9c348a6…已核：D2H=2、ixStream_t不透明struct指针、Linux IXRTAPI空、Torch stream._as_parameter_为cuda_stream的c_void_p，实际CUDA/IX导出与g++13.3已取证。存在声明／导出不当设备证明，不再重复公开检索或现场取证。

本owner新增 `scripts/remote/validate_kv_pitched_copy.py` SHA **c8c0f64e7293634a28949f4338800298b43d32daa7cbd866e64dcd59833d7dc6**，纯device-worker，`--help`及导入无Torch／载库；必要compile、runpy import无Torch与help已通过，没有CPU复制模拟套件或GPU。source包含固定c95f、原两map489f、ABI f9c3、候选py818e/cpp0a4d及外层实际编译bridge.so SHA。首次任何异步copy前fixture强持全部tensor/pinned host/event/descriptors；两case原始页序、R和全部bytes均保留，pool取32578／32572；每case只一层。源view与pinned目的有真实storageoffset及双guard，页号／word偏移CPU oracle避免高级索引误判。新桥紧接同非0Torch流H2D producer，传相同nativehandle→同event真完成后先核CPU oracle，旧c95f此后才启动，避免旧路wait掩盖流错误；完整source及两端guard也全字节回读不变，CPU/GPU RNG不变。中途API失败只settle，无旧路重试；不settle保强引用到外层清理。

两case都过才首case固定8call短ABBA，event构造／首record和submit预热窗外，真实各条submit Python/C检查（含native GetDevice/MaxPitch）＋同流event完成wall在窗内。双方plan及新Tensor检查／ctypes descriptor准备窗外单列耗时，分配／填值／producer／CPU校验不计。root明确这是**C batch＋2D合并组合**，不是纯2D贡献，暂不扩第三路；c95f为copy_方法计数，新桥为成功原生API提交数，均非DMA次数／时间占比／整个SAVE或E2E。实际maxpitch不支持的段提交前拆单页并显式记fallback，不冒充已测33,570,816B pitch。实际进程/proc/self/maps只接受唯一已核libcudart d39d…；外层ldd还不足，子进程另核SHA。

framework runtime **818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd**、C++ **0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44** 已全文只读核；descriptor72／SDK实类型／extent／overflow／全batch提交前验证／pitch fallback／partial失败不降级，未见当前短门阻断。author唯一planner合同test1d470f21…1test0.013s一次通过，JSON1ec3bd2f…已读，没有重跑；只验证计划数学／导入不载库，不证明事件／GPU。gate c8c0已交framework与root只读，root初审无阻断，待framework最终回执；不因中文报告延迟上卡。

systems outer `scripts/remote/launch_kv_pitched_copy_gate.py` 最终 **3ffe8efe643a5c280a85217299bcb0adb6349c66f499659d2de9b5167dcce7da** 已全文只读核，最终仅三pin替UNREVIEWED，无额外机制改动：唯一外层flock/双idle、实SDK/头/库SHA、g++/ldd/readelf、单child300s与定向进程组cleanup、DBafter/post/fullsource/seal；worker内无锁／controller，source只regular，避旧__pycache__哈希错误。无当前生命周期阻断，没执行wrapper或copy。CLI为 `python RUN/source/gate.py --device-worker --output-dir RUN --source-dir RUN/source --bridge-sha256 <actual SHA>`；results/failed独占创建，不覆盖原件。中文说明 `analysis/2026-10-22-kv-pitched-copy-gate.md`，专项review `analysis/source/kv-pitched-copy/gate-preparation-review.json` 保SHA、CPU检查及审阅边界。

本阶段到此仅本地脚本/文档准备、只读互审，未SSH/GPU/SDK编译/CDLL/推共享库，没有设备pass或速度声明；root是唯一设备owner，实际结果待其独立新UTC门。旧c95f/FULL/progress/全部实际日志和source不改。

最终回执：framework已全文终审c8c0无阻断并回root；本owner同步systems最终outer3ffe无阻断。门／runtime／C++／outer四SHA全部保持，不再为文档改代码，root可串行执行唯一短设备门。专项review已补cross-review回执，无任何设备结果继承或收益声明。

### 032653实际单层门通过：保完整字节与组合事件小信号，下一唯一控制已采纳

root新原件 `experiments/framework/20261022T032653Z-kv-pitched-copy-gate` 及control已本地，包2ba3856fef63566c8a372818a2ae60e21c999d8022465d8d29ad13a7de99c55c。本owner只直接核结果/实际segment展开/环境/算术，没有执行systems完整validator、SDK或GPU。Engine child258707，BI-V15016SM32GiB，实际so9e33ecbf…/maps libcudart d39d…/非0handle94118921500112。MaxPitch2147483647>所需33570816，两个实际map37→11(2linear9pitched)、26→6(2linear4pitched)，fallback0；全byte/CPU page-offset oracle/c95f/source+双guard/host双guard/RNG以及计时后都true。仅一层，不当42层batch/workerACK/service/accuracy。

8call ABBA wall baseline7.415286498/1.454228535ms，candidate0.672264665/0.681895239；baseline首尾5.099倍，稳定wall gain保持null。event baseline均0.652585804→candidate0.628187954ms，约3.73864%只是C batch+2D组合描述性小信号，纯2D/E2E gain均null。CPU线程56/额度6，整门134periods里54throttled，累计thread throttled_time236317938303ns不可当wall；没有逐timing窗CPUstat，所以不归因pattern/比较/cgroup/某API。host门前3.219GB/门后3.251GB、上限20GiB不是峰值；原CPU准备old1.342/2.400ms,newplan1.443/2.264ms,newprepare0.759/0.891ms全在窗外，不是免费或可乘42。

中文结果 `analysis/2026-10-22-kv-pitched-copy-032653-hardware.md`、专项 `analysis/source/kv-pitched-copy/032653-hardware-review.json`已存。root采纳下一唯一动作：不改818e/0a4d，64call三路固定A/B/C/C/B/A(A=c95f,B=同bridge prepare(max_pitch=PAGE)的37/26线性描述符,C=真实maxpitch C2D11/6)，逐窗口实际v1cpu.stat原值/差值/单位，采样窗外；保持56threads/6quota/官方参数。只新增Clinear完整字节/guard/counters正确性，不扩矩阵；只首case计时，准备/模式填值/CPU整源比较都在窗外、submit+同流完成计入。错误则拒绝不降级；六窗完成即收口，波动/窗口节流不确定也保留不盲重复。只有值得继续才42层真实payload/lifetime含prepare门，之后才服务。本轮先checkpoint，我没有写新gate/runtime/启动脚本或新设备请求。

root后继42层选择补充已落报告/JSON：若三路值得，直接原long VERIFY1真实事务，不另造22GiB合成fixture。已只读framework边界574515e9…：新SAVE完成／SAVED及sourcefree之前复用既有单层verify_buffer，逐层冻结c95f源→event→CPU比新host，42层全过才SAVED，再原FULL回读＋consumer；独立证明SAVE，非仅host自证。原预算／fence／引用／失败settle不放宽，不新增0.7GiB影子host或GPUbuffer。目前尚无新worker代码／部署，诊断不算性能；本owner不新增脚本。

### 新阶段2746e01b：唯一64call三路门已实现并双审，尚未设备执行

032653报告同名冲突已依root指令恢复原正文到独占 `analysis/2026-10-22-kv-pitched-copy-032653-hardware.md`，SHA精确等于原7f93aab5c32e450ab7a4a9c6065dc2eabcde54c283952a7b4e631056e669dfb2；systems的…-result.md保持a6b88原字节，不再共写。root随后完成干净2746e01b检查点，新阶段解锁并明确授权唯一三路门。

本owner独占新增 `scripts/remote/validate_kv_pitched_threeway.py` SHA **9b16aec69ecc6e2bf59de7fd0f323ae543a1a32eda15486aa294e2f49c645dd9**，从c8c0原字节复制，小diff仅新增C-linear及逐窗CPU观测／64call。现有函数AST仅correctness_case、timing、device_worker变更，新函数只有cpu_snapshot，其余原函数同。818e runtime／0a4d C++／c95f／原c8c0及旧原件未动。新worker CLI和归档asset名同旧门，不新增controller／worker服务代码。

同两个冻结map只补B＝prepare_save(max_pitch=16384)的独立pinned host＋PreparedSave，首次submit前fixture强持。B是受控提交前拆段，不是实际设备pitch不足；原计数37／26全linear、0pitched，返回fallback_segments9／4属于控制方式。C仍真实maxpitch为11／6或真实回退，不混B。B须全字节CPU page/offset oracle＋c95f、source／host positive-basic双guard及计数通过；原C紧随非0流producer先核保持，失败settle／不settle强引用／不旧路重试不变。结束后三路输出和源／guard／CPU/GPU RNG仍核。

仅首case固定 **A/B/C/C/B/A，每窗64call**，A=c95f、B=C-linear、C=C2D；event首record／三路submit预热和准备／pattern／CPU整池比较都在窗前，窗间无整池比较／sleep／扫描／自动repeat。每窗前后在wall/event之外读取实际v1cpu.stat及quota/period，保raw/counters/delta和累计ns单位，不当wall损失；process_time_ns单列为进程CPU时间，不冒充主线程或wall。只核56 Torch线程和600000/100000us额度，绝无setter／官方参数修改；读取缺失／计数重置／额度变化明确拒绝。wall波动／窗口节流保不确定，不追样本，不给DMA／服务或准确率结论。

必要CPU检查compile／runpy导入无Torch／help过，无新suite、旧planner合同重跑、SDK编译、CDLL或GPU。framework对9b16完整delta终审无阻断；systems也只读生命周期无阻断。systems独占outer `launch_kv_pitched_threeway_gate.py` 最终 **b2c65963f621f83b0d093353e7135b3434d4c49bb9402c05bb2a3363aa6f5a88**，本owner实核仅gate输入/pin＋两处run suffix，逆换逐byte等于旧3ffe，原唯一flock／idle／SDK编译／单childtimeout／定向清理／DB后态／seal全不变，无阻断回root。运行四件资产冻结不因文档改动，root是唯一设备owner。

独占中文 `analysis/2026-10-22-kv-pitched-threeway-hardware.md`，静态准备/互审证据 `analysis/source/kv-pitched-copy/threeway-hardware-preparation.json`；没有写systems报告。当前实际门尚未执行，所有收益null；若后继信号值得，仍已选原long VERIFY1真实42层SAVE源free前逐层c95f核新host→FULL／consumer，不另造22GiBfixture。本阶段没有SSH/GPU或外部写。

### 035754三路实际专项完成：六窗无新增节流，保单层小收益

root已取回 `experiments/framework/20261022T035754Z-kv-pitched-threeway-gate` 及control，包 **fa80a90332005eda7cc77862c82c85876a27ee9e10692456409b7abf909b4bbd**。本owner仅直接解析results/CPU原文本及算术，不执行systems唯一整门validator/旧suite/设备。实际child260602／9b16／818e／0a4d／SO9e33／maps d39、56CPU线程／6quota保持，非0handle94323367614720。两map C-linear37/26linear0pitched、控制fallback9/4；C2D11/6真实API且fallback0，全字节/源/双guard/RNG记录通过，原件完整身份/DB/后态归systems。

固定首case64 ABC CBA，六窗CPU raw→counter→delta独立重算相符：nr_periods[0,1,0,1,0,0]、nr_throttled及throttled_time均0。CPU准备开始→首窗前有55period/46throttled，累计204298016825ns只界定计时前发生过节流，不定位具体函数、不倒推旧032653异常。A/B/C热wall均值 **0.686350722/0.655053591/0.631339994ms**，本轮描述性A→B4.55993%、B→C3.62010%、组合8.01496%；event均0.666308880/0.652398735/0.628310144ms，B→C3.69231%。A event首尾0.6791/0.6535仍有差，单次镜像两样本不称稳定硬件带宽；processCPU时间也非纯Python。小收益保留，不追加同类微门/盲重复、不乘42或称E2E。

窗外准备oldplan1.351/0.945ms，新plan+descriptor2.778/1.505ms是单次样本，不能当免费或用热差保证一次SAVE收益；真实42层需含首次加载、prepare、pin、fence、event和生命周期。独占中文 `analysis/2026-10-22-kv-pitched-threeway-035754-hardware.md`，独占专项JSON `analysis/source/kv-pitched-copy/035754-hardware-review.json` **e521ecff420487831178668a57bf04b943542d2f7ac3a0d9ef9c3defddfcef20**。root据此推进已授权原long VERIFY1真实42层诊断，不造22GiB合成fixture。

### 后继SAVE worker a662只读终审通过，尚无设备执行

framework新 `patches/framework/candidates/biv150_kv_pitched_save_worker.py` 首稿4f1dd74c…已全文对比原5d9a与唯一stub合同，无当前真实VERIFY1门阻断：只改SAVE，晚加载818e／邻SO9e33／真实maps d39；全42先验/currentstream，bridge/prepared在submit前入slot强持，原fence/_finish/except及FULL1aff／txn84be不动。SAVE后源free前原verify_buffer逐层冻结c95f读真源→event→CPU比新host，全42通过才SAVED；buffer留原FULL，VERIFY0无新增回读，部分失败不旧路重试／不settle仍持引用。单层只测非0流，service实际handle含0由下一真实事务记录/验证，不用stub声称设备通过。

root要求去重maps读库，最终worker **a662e478d20884c5b1d65e0ee3d270a62453d88166b28e092dcaf3b35a3df854** 仅/proc resolved路径set后每个libhash一次，避免重复8.39MB文件读；本owner实核该微delta与旧4f归档SHA，无新阻断，已回root／framework。唯一CPU合同实际4f/test38de41e7…/1test0.122s一次通过，receipt9df0b498…保真实旧身份；最终只微delta compile未重跑、不虚称stub验证SDK。独占035754中文已加明确“后继非受测代码”段，本owner不改作者代码／systems报告，无GPU/SSH/旧suite，420源包装待systems交审及root唯一真实门。

用户最新验证尺度（root转达）：**“确定的收益可以不用大测试，你把握好”**。035754小收益已按单层范围保留，不追同类微门；42层真实VERIFY1只补当前未覆盖的SAVE正确性／生命周期，不能删必要正确性，也不自动扩大完整官方或重复长pair。后继仅在短证据未覆盖机制、出现矛盾或最终验收确需时扩大，建议继续保持最短。

### 社区框架机制研究收口：优先 Corex blocking Event 契约，不新增运行代码

先完成 systems SAVE 包装只读终审：`prepare_kv_pitched_save_source.py` **cd3d5c2874f487f8115329d573cb5202f893ab46c89cf31764e9757decaf0209**、`launch_kv_pitched_save_screen.py` **df6a4c9e095bb25900e54c22adf56b0d1674b6a57c1b9476b55977a826a7b819** 无当前阻断。完整214400 FULL416基点只替worker a662、增邻接818e runtime/9e33 SO/0a4d cpp及独立manifest到420；1aff/84be/791c/e155原字节、原bc51long/seed721201/VERIFY1、唯一锁/双idle/source/DB/清理保持。SO只hashcopy不编译/加载，INSTALLED仅预检，必须实际SAVE源free前42层c95f对照再FULL/consumer/hostfree。静态证据2b5ef220…已读，没重跑copy/suite/设备。root后续回执042225已真SAVE42/FULL42/consumer16、32/0、DB相同；本owner本轮未独立整门验收，不把回执改称自己的设备证据。

root按用户“多开智能体查最新社区/论文框架机制”新增本owner独占社区研究，范围 CPU/web-only、不SSH/GPU/外部写/改runtime。最终中文 [社区报告](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-22-community-framework-research.md>) SHA **1c06e223d06e6ff4e3c7e50d5df13bd635a8c618b1eeaf717d894679f4727971**，四项有序机制：

1. [vLLM #47081](https://github.com/vllm-project/vllm/pull/47081)／[实际diff](https://github.com/vllm-project/vllm/pull/47081/files)，2026-07-07合并，device blocking Event。本站exact e155原件路径为214400-control/plugin-source/vllm_fl/worker/model_runner.py：758创建prepare_inputs_event，3832同步、3836 finally record，4162–4167在_update_states前进入输入准备CM。下一最小只动758的device事件工厂／blocking标志，原with/异常/流/顺序全部保留；314→340→348的异步输出暂不混，已record的事件不能事后换新。generic torch.Event接受blocking不代表有效，PR作者报告CUDA上generic没有兑现标志，本站Corex更需查证。TP4经验不外推TP1。
2. [vLLM #62357](https://github.com/vllm-project/vllm/pull/62357)，2026-10-18提交仍Open，真实num_seqs不特化；actual54c kernel178/234、reducer662/670仍无DNS，specJIT66a442–463支持参数级开关。只潜在冷/JIT收益，官方warmup/skip1后可能为零；不fake N、不加kernel实参或改SME位序，不和Event叠加。
3. [SGLang #39627](https://github.com/sgl-project/sglang/pull/39627)，2026-09-29合并，原生批量KV bookkeeping的ownership/异常边界。不是把RustTreeCore整移vLLM；该现成扩展Torch2.11–2.13/CPU-CUDA支持范围没有本站Torch2.10/Corex。actual3fc BlockPool542/597/614有逐页状态工作，但已popleft_n等批量队列、free O1、cachefull跳已缓存，不夸成重复全表。先有真实CPU占比才考虑窄批次，保block身份/alias/ref/hash/free顺序。
4. [Triton RFC #10140](https://github.com/triton-lang/triton/issues/10140)，2026-04-27提交仍Open，guarded compiled launch handle；本站此前next-framework-priority已有条件未实施计划，本轮仅补一手证据。actual66a737后binder/cache/SME/pack仍在；只eager Attention机会，不能把graph已消掉的Python算收益，不能套NVIDIA cuLaunchKernelEx或绕过Corex options/hooks/globals。未实施或上卡。

已直接核[PyTorch2.10 Event文档](https://docs.pytorch.org/docs/2.10/generated/torch.cuda.Event.html)，不是用重定向的2.14当安装契约。Corex仍缺actual Torch Event.__new__/底层绑定、IX driver_types的EventBlockingSync位、runtime createWithFlags/query/record/synchronize及mapping。旧030314 f9c348a6只摘Stream._as_parameter_和copy ABI，不含Event；实际路径/needle已发systems用于最小只读取证，避免再采整源。声明／导出存在也不证明Corex真睡眠。

报告规定后继最短证伪：同实际CM跨两步复用pinned buffer、在pending事件上等、逐位核结果/事件完成/原异常语义，不用额外global sync掩盖依赖；同工作量预热短镜像窗，窗外v1cpu.stat，等待线程CPU/进程CPU/wall/event分开。CPU等待须下降且wall不退；不支持/忽略flag/完成错/wake-up回退/事件早已完成无预算均保负结果停止，不自动扩事件种类或大官方。6CPU与copy门CPU≈wall只是动机，原长服务95–96%GPU利用/driver等待混杂不能证明3832忙等或预测TPS。

许可一手核vLLM/SGLang Apache-2.0、Triton MIT，后继借码须保版权许可并另核Corex派生文件。排除growth/terminal/短R/WAITING单步、已做dirtytable/C2D，不把SWA/Mamba/MoE/多模态或新框架整合当本站方案。所有事实仅天数BI-V150，C500由队友另验。

额外重要纠正已与root统一：原FULL1aff的single_victim仅限制单并发host slot；_drop85–96重置victim=None，_wrap_preempt没有每Engine总次数cap，有限32req一轮实际一次SAVE不能推出长负载一生一次。当前无新性能数字／运行代码；root本阶段固定检查点，下一只做Corex Event能力纯读取证，其他三项队列保留，本owner到此停止扩大检索／实现。

systems依精确缺口新增只读取证脚本 `scripts/remote/audit_event_wait_contract.py` **50168b584f013c999b719d2650bec4b47a0be1858a5996a38dee6bff9348de59** 后，本owner只读79行全文，无当前取证范围阻断：12固定安装文件及e155四窗口、五项原SHA、无Torch导入/CDLL/编译/API；missing、片段truncated及read_only_collection_not_semantic_pass保清楚。没有执行脚本。exit0仍非Corex睡眠/性能pass，缺绑定不拿新上游补成本实例事实；已回systems/root，本轮不扩文件或检索。

### 后继只读实际日志核查：原输入准备等待很小，当前机会仍未证

root新任务要求在50168以外找真实prepare_inputs_event等待证据，而非微门CPU≈wall或服务GPUutil。本owner只查现有分析索引/旧profiles文件，直接读取既存 [061506 host-window.pstats](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/host-window.pstats>)，SHA **f4902a604f0a5813e4c1148d3e16534ec3afa0951010d67c7b83a7c42a67dd62**；没有执行profile/旧validator/测试、无新文件/SSH/GPU。实际8步、shape62/61/60/59诊断窗口有明确caller归属：

- `torch.Event.synchronize`共16次；来自`synchronize_input_prep`的8次合计 **64.628微秒**，平均 **8.0785微秒/步**。CM自身是generator进出16次，累计139.238微秒，不能称16个独立step。
- 其余8次来自`AsyncGPUModelRunnerOutput.get_output`，合计 **157.091821毫秒**。这只能是输出路径等待预算线索，不是输入准备事件的数据；pstats的C方法时间也不证明其CPU忙等或阻塞睡眠，不能直接改成CPU可省时间。
- 旧native042609的10次cudaEventSynchronize合计133.157毫秒没有Python调用归属，不能补作758证据，也不与上面另一个窗口相加。

旧归档runner SHA **dfd532de4a0b0bdb286aed0f42b4d6f2c3b2c2dcf65634f895577144473b68b9**，其`synchronize_input_prep`函数AST只读比较与exact e155相同，但整树是旧SQL主因诊断而非当前SQL+C3。该窗口wall13.9476秒、SQL路径约13.4秒；长CPU间隔可能已掩盖等待，所以不能把旧微小等待外推为当前绝对无机会。反之，现有日志也没有当前e155在3832上暴露可观等待或CPU自旋的直接证据。**结论是当前机会未证；旧实测对“输入准备等待必有大收益”给出反证，不能宣称确定收益。** 不据输出157毫秒自动扩大本轮候选。

停止条件保持窄：先根据信息不完整状态完成actual Event只读取证；若Corex/实际绑定不能传达blocking语义，或后续最短真实路径证伪中事件已完成、等待CPU不下降、wall回退、buffer复用/事件完成/异常语义出错，则保负结果停止，不再扩事件种类或靠长pair找样本。若旧SQL移除后的实际等待尚未测，就明确未知，不能拿整服务GPUutil、copy门CPU≈wall或上游TP4数据填空。本轮只追加本handoff，未改CURRENT/registry/研究报告/runtime；落盘后停写，root执行source audit并决定下一最短动作。

### 9626003后：用户要求合理利用设备，唯一实际Event三路短门已准备

root新授权尽快实现独立能力/行为门，不安装服务优化。本owner只新增 [validate_event_wait_gate.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/validate_event_wait_gate.py>)，SHA **67090baad306b95679717a0f4b3e97d7a16abc9815317d3c885102ccac1d32ae**，240行设备子进程；另仅追加本handoff。CLI `python RUN/source/gate.py --device-worker --output-dir RUN --source-dir RUN/source`，不含bridge参数/内层锁/controller；results.json或failed.json exclusive保存，outer负责唯一flock/双idle/监控/超时清理/DB/source封存。没有改CURRENT/registry/服务或旧受测代码。

固定A=`torch.Event()`、B=`torch.cuda.Event()`、C=`torch.cuda.Event(blocking=True)`，**A/B/C/C/B/A各4trial**，不扫描参数/不自动重复。单显式非0Torch copy stream；每trial连续8次32MiB uint8常数0x5a GPU→pinned host，约6GiB被测D2H合计，源回读验证另有流量并排除等待计时。全部分配、首record/synchronize、copy路径预热在六窗之前，setup_wall_ns单列；保持原56Torch线程和6CPU quota，GPU/CPU RNG前后核验，不做setter。

仅被测event.synchronize区间计thread_time_ns、process_time_ns、perf_counter_ns，提交及timing begin/end record/被测event record/early query均在wait计时外；同流timing event包8次D2H。返回后必须先test query和end query都完成、host全32MiB min/max确认每字节0x5a、positive-basic两端guard原值保持，任何失败直接拒绝；**这些检查之前没有补充同步**。全部通过之后才另用同流事件核GPU源全字节，不能用其同步掩盖被测Event提前返回。相同目标重复写0x5a可能遮蔽后续未完成，故end.query为必要独立条件，不能只看最终host常数。poison只写payload，不重置guard。

每窗外保真实v1cpu.stat路径/raw/counters/delta；其范围包含该窗4trial的等待与计时外poison/字节验证，不能当纯wait窗口节流，累积ns也不当wall。setup/actual Torch类型/实际Corex libcudart去重maps路径与d39完整SHA/硬件/命令/source SHA/早完成次数、每trial clocks与device elapsed、最终RNG齐全。此门不声称真实prepare_inputs_event暴露成本、缓存运行状态、CPU自旋根因或服务收益。

强持所有buffer/stream/Event直到完成；异常仅尝试设备settle、不重试原路；若settle失败全部引用保global到outer定向结束，成功路径无global sync。finally清理可安全释放的引用；未完成的fail不能补成pass。必要CPU compile、runpy导入不加载Torch、--help均过，没有新增CPU模拟套件或重跑旧suite/设备。framework已全文终审67090无当前三路门阻断并回root；systems只需将同pin填入唯一outer。root是唯一SSH/GPU owner，实际结果尚未执行/取得，本条不借41ba声明构造等同设备行为，也不提前认定C生效或有收益。

### 045818 typed Event负结果后：唯一原生Corex差异门小fork已准备

root回执045818实际67090/32a门exit0、完整原件在本地：原A generic/B typed默认/C typed blocking三路threadCPU均约9.44ms，typed blocking没有CPU下降；C1 wall8.689ms异常不作加速。本owner当前没有重跑systems唯一完整验收，也不据该wall单点宣称收益或猜事件cache运行状态。root明确只再做一个不同机制：直接SDK创建BlockingSync事件，之后按用户“完成手头转GitHub”收口，不追加服务接入／研究／设备队列。

独占新增 [validate_native_event_wait_gate.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/validate_native_event_wait_gate.py>)，最终候选SHA **7bac3901b6ddeafb5518a473733c2486deab9d561441a6a729a92782c8e57aba**；旧67090原字节不动。只从原门小forkA=generic、B=typed blocking、C=NativeEvent，其余ABC CBA×4trial、32MiB×8、host poison／先query及完整host/guard再源回读、三clock/wall/event/CPUstat、RNG与硬件/线程设置原样，不增加窗口/负载或参数扫描。

framework独占adapter [biv150_native_blocking_event.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/patches/framework/candidates/biv150_native_blocking_event.py>) SHA **327e8aff211f33fd9f7fe0bd841b330e4205a5c0677e7a5e9b7c28ce0fec7365**，C++实际路径 [biv150_event_bridge.cpp](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/biv150_event_bridge.cpp>) SHA **ee01eb013f054fe5ebcd057794bdce9b57a977c6f3745de77e48d4411f0b31d7**。本owner已全文实读核SHA，无当前短门阻断：SDK真实pointer类型/flags OR、create部分失败保handle清理、query仅NotReady→false其他error抛；record前持refs并置pending、sync/query真成功才settled；close失败保handle/ref，无__del__或IPC/全局flag修改。声明位仍不当CPU睡眠证明，必须本门实测。

gate在所有提交前强持NativeEvent；C每record显式传当前非0stream_handle与keepalive=(stream,fixture)，不替换流。构造后记录实际编译creation_flags并严格等于3、actualSO SHA及加载桥后真实maps libcudart d39；py/cpp完整pin+outer动态SO `--bridge-sha256`校验，归档素材名biv150_native_blocking_event.py/bridge.cpp/bridge.so。全部正常完成后才close()；异常只有owner真正device synchronize成功才close(owner_settled=True)，不settle或destroy失败全留引用到outer结束，不降级/重试旧路，也不能把失败清理补成pass。

必要compile/help/runpy导入无Torch/ctypes均过，未编译SDK/加载SO/执行GPU/新旧suite。framework对draft b876全文审无机制阻断；最终仅填327e/ee01两pin及root要求的creation_flags/SO元数据/flags3断言，已发framework定向终审、systems外层锁定最终gatepin。文档不阻塞设备，root仍唯一SSH/GPU owner。此时native实际门尚未执行，本owner不提前写结果；实际完成后仅保字节/CPU行为与边界，手头收口即停止新增探索。

systems最终outer `scripts/remote/launch_native_event_wait_gate.py` **f3133a74211b98e4e137b728ea5bc398d582db0d96ca1884ff37f11469619f2e** 相对旧32a增量已只读审，无当前阻断：4输入exact gate7bac/adapter327e/cpp ee01/契约41ba，CPU g++真实SDK编译产SO，d39库/ldd/readelf/实际SO SHA传CLI，新native suffix；原唯一锁/双idle/DB/source/子进程组timeoutcleanup/seal不变。没有执行包装/编译/API；回执已发root与systems，运行文件不再为文档改动。

### Native负结果收口，转为两个可独立合入的中文PR材料

root最后回执051336原生差异门exit0，字节／RNG／close均过，但直接Corex blocking的threadCPU仍约9.435ms，没有下降；不服务接入、不再找Event变体。本owner不重复systems完整验收或设备，只保root真实回执边界。用户明确现在按方法拆PR／中文说明／依赖方便合入，全部实验结束，转协作材料准备；本owner没有远端操作权限或动作。

已完成两组独占准备，目录各为 `files/<repo-relative-path>` 镜像、中文 `PR.md`、`manifest.json`：

- [连续页复制PR材料](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/docs/pr-preparation/kv-contiguous-copy/PR.md>)：只有c95f工具 `vllm_fl/patches/biv150_kv_page_copy.py` 与独占 `docs/kv-contiguous-copy.md`。manifest SHA **7c2eab63ff2818a1ee0c5d44bfa17d13a35eeca2e7f9063e5cc90cbd6b69405a**，PR文本SHA **4b1606830eb3869c809c5a66131fb01e76036d1c1a92fb3c55891a0dcee1b89d**。
- [二维SAVE复制PR材料](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/docs/pr-preparation/kv-pitched-copy/PR.md>)：只有818e工具 `vllm_fl/patches/biv150_kv_pitched_copy.py`、0a4d源码 `vllm_fl/patches/biv150_kv_pitched_bridge.cpp`、独占 `docs/kv-pitched-copy.md`。manifest SHA **e212408de53ad5945c2fa82508118263e2d70053bf368c3e7538fa092e92a8cf**，PR文本SHA **108a851078a47f8fc1856c9148fbf1d7f60b9d23654f185cf52077c63f67c7a7**。

只读核base：本地main70d04f38382e900949ddeb34d2ac75aacdc93af4，tree82e37f8f263eeb09563a4790359ec95a0de1ca17；对应root已核remote d5e2e3a54b48dcb1b50f575d2420979591fb3e1c同tree，当前任务无联网重核。全部五个目标在该base不存在，manifest均base_blob=null及mode100644，记录每文件SHA／Git blob SHA／原source路径与SHA／证据／验证缺口。c95f同时逐字匹配旧本地37661d的工具blob，只复用工具，未复制过期README或旧kv-save-restore文档。

依赖已实际AST核：818e只导入ctypes/dataclasses/hashlib/pathlib/sys，SavePlan/Segment自有；0a4d只含标准库与实际SDK头，无PR1代码依赖。`original_c95f_runs`仅本模块自算对照统计，不import c95f。**两PR共同main、无前置依赖、任意先后合入／单独回退**；后继完整worker／协议若采用两工具再显式建立依赖，当前不虚构顺序。

中文说明明确：提交不是ACK、调用方须管producer／当前流／全部强引用／真实完成／页所有权／预算和失败settle。PR2须从Git源码按实际Corex SDK手工编译并固定SO身份，未打包SO或改变setup/wheel，也未接default；仅cuda0 normal16KiB、单层或42层、1GiBcap，其他平台尤其C500未证。032653 wall波动、035754同桥线性→二维约3.62%单层热信号、042225 R16688/717717504B真42层对照和恢复回读均按原范围写明，诊断不称服务吞吐收益／准确率。PR1四构造case也不冒充packed已实际服务部署。

本次仅原字节复制、Python compile(bytes)、静态依赖与Git只读tree/blob/status检查，没有新增实现／设备测／旧suite／SDK编译。collaboration当前HEAD始终37661d2d2cf811ef8093436fa17c424dfd63b25d且clean；没有checkout／index变更、commit／push／PR API。没有改README/init/setup、原c95f/818e/0a4d、当前冻结候选或任何实验原件。root负责发布和组合检查；本owner材料完成后停止新增研究／实验，等待定向修订。

### GitHub维护后接续：两CPU方法最短组合门，先审旧覆盖再获准实现

root已完成Github维护；本owner新任务先只读b124 metadata门与607cd async门，找6f918组合风险，不恢复旧探索。独占 [最短门审阅](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-22-cpu-combination-minimal-gate-review.md>) 已保存：b124实际提取5方法形成_prepare_inputs→_prepare_input_ids链、actual CpuGpuBuffer/BlockTable、5case/11checks及4轮原event/graph可复用，但只锁单metadata，缺async helper绑定／model.is_encoder_decoder=False／graph input_ids／同次双命中。607cd有真实单方法12类映射/stride/显式跨流与缓存门，没有整_prepare_inputs/metadata/原event+graph，不能拼成组合已验；本轮不重复12类。

静态实际关系无互相缺输入：async读CPU cumsum/prev_positions.np与原两份局部索引H2D，不读metadata跳过的req/query/scheduled GPU scratch；两helper仍同原prepare event/流内。请求重排fixture是reqID→旧行映射，不是实际InputBatch swap/condense／scheduler/输出队列生命周期，文档明确没有该完整服务证明。

root随后明确批准新独占 [validate_cpu_combination.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/validate_cpu_combination.py>)，最终SHA **abfc7981a8d5a20ff32b80f42dd30148bbeb5d680c649bf892e2b3924ead0bad**；不是自行扩大只读授权。只从b124小fork，固定basee155／combo6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141／metadata0e961／async1bb85和3旧依赖完整SHA；controller直接copy源码，不transform，不改两个helper/runner/原门。

fixture仅补decoder字段，两实际helper绑定namespace。保原五CASES/11checks，decode62和mixed952每次须metadata/async各delta1；no-previous async须0，不强迫所有shape都融合。四event/graph轮加入input_ids实际consumer并要求其跨轮非陈旧，每次双delta1，positions/seq/input_ids/slots地址固定；原CM内configure／H2D／kernel／finally record／graph顺序保留，四步之间无整卡sync，最终比较前才drain。全部timing和32call被删除，RNG从正确性流程前后核equal并保存SHA；没有组合速度/准确率结论。

必要CPU compile、runpy无Torch/Triton导入、--help通过；AST核只make_runner/worker/main改变，增加计数/pointer两小helper、删除旧timing call函数，五CASE AST完全相同。framework全文delta终审无当前正确性门阻断，final保持abfc不再改；没有执行新门／旧suite／GPU或网络。root是唯一设备owner。CLI为 `--run-dir RUN --runtime-path METADATA --async-runtime-path ASYNC --runner-path BASE --candidate-runner-path COMBINED`，沿原controller独占flock/idle/child/monitor/timeout/定向清理；systems薄层仅资产pin/DB前后/env/source/seal，不第二锁或GPU清理。该门不带权重、不导入完整runner、不会启动服务；设备结果待root唯一新run。

062205后续实际回执（root提供，非本owner重复验收）：唯一组合门exit0，五case所有比较、graph四步同次双delta1／四consumer／RNG全过，metadata总9、async总7。准备时“待root新run”已由本次结果取代，完整原件正取回并由systems唯一全审；本owner没有执行validator/新GPU。**prefill2048实测async delta1**，不是单token identity：prev行0需要写到2048-token chunk的末索引2047，common_indices_match不成立。实际decode62/mixed952/prefill2048各async1，两no-previous为0，加四graph步为7；不再把设计时未强制prefill当作观测可能0。图已核原/组合逐步相同且input_ids首末非陈旧，仍不宣称真实InputBatch重排／输出队列全生命周期、服务收益或全模型准确率。代码abfc及两个helper／runner均保持，不补门/长pair；本owner只收口静态review文档与交接，待root后续指示。

### 长期协作要求：PR、我们新增的README与说明保持自然中文

用户再次明确：**PR标题、正文、我们新增的README与维护说明使用自然中文**，英文专有名词、API、路径、命令、数值与哈希保留原样；不要为了中文化改写上游原文、许可证或实验原始证据。该要求持续适用于后续修订与新API接续，不仅是本轮翻译任务。历史发布回执／固定manifest与其证据不可为了追新状态直接改写，后续状态用有版本的说明或新回执补充。

本owner本轮只读核对 `docs/pr-preparation/` 四项CPU metadata／async token／连续页复制／二维SAVE复制的 `PR.md`、`publication-body.md`、新增说明及本地发布标题，并核 `combination-review.md`；标题和正文已使用中文，技术专名保留，无必须修正的英文标题或英文整段。另核根README、两个私有代码副本的协作README与 `docs/github-collaboration.md`、`docs/pr-collaboration-plan.md`、当前AGENTS规范，均符合中文要求；两代码副本的 `README.upstream.md` 保留上游原文，FlagGems仍链接原 `README_cn.md`。这是本地材料语言核对，不是远端PR重新读取或方法门／准确率复验。

一项状态提醒已另告root：`docs/pr-collaboration-plan.md` 开头“05:13:44 UTC后没有启动新GPU工作”和部分README的“探索已冻结／暂不新增实验”属于旧阶段状态，与062205及当前恢复主线不符；建议由root在维护当前说明时明确其历史范围，不为此改固定发布回执或旧manifest。本owner不修改这些共享文件，也不推断当前服务结果。

本轮唯一写入为此交接追加；没有修改CURRENT_WORK、代码、共享checkout、README、PR材料或远端PR，没有SSH／GPU／新测试。root仍串行负责短服务基线→CPU组合，本owner不重复062205方法门，追加后停止本轮文件写入。

### SQL独立审阅PR：原始测量与正确性证据，不继承组合成绩

用户问SQL为何未独立PR；root准备为main中已存在的方法补历史审阅入口，不重复合入。分工：framework核独立源码patch／真实历史基点；本owner只读原服务JSON、manifest／driver／server日志及CPU gate原log，未执行validator／测试／设备，不操作共享分支或远端。证据仅天数BI-V150，不能外推C500。

**SQL单项有真实独立增量短筛，但它接在保留performance基点d60b023之后，并非从13eb原版单独只加SQL。** 071554为该保留基点B0，两个SQL run不叠C2/C3／新token融合。三轮同driver SHA `22a076e79a486712ae5c0655b17a9ee986e51b987083bdcb64fdbc4840ea5603`、同官方SERVER（launch-command.json三者SHA均 `ec915d0098862907f563bd0a91d14079d59b6a82a6660710085c80f37d36887b`）、seed721101、4096输入／128输出、64请求／64并发，vLLM0.24／Corex Torch2.10／FlagGems5.3.5／SQLAlchemy2.0.48、6CPU quota。三轮均64完成／0失败、262144输入／8192输出、exit0；真实server日志KV均521840。两SQL日志有 `BIV150_SQL_REFLECTION_INSTALLED sqlite_targeted_only=1`，B0没有；两SQL runner同c81e6ae9，模块同ad84c9。三轮仍保留vllm._C缺失和shutdown forcekill等原WARN，不能写成无告警。

| 原件 | duration s | total token/s | 原JSON完整SHA256 |
|---|---:|---:|---|
| [064632 SQL单项](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T064632Z-sql-reflection-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-144829.json>) | 43.19865510286763 | 6257.972600217696 | `2ca4aff5fbd480ec5ad61f2bed39a4eb9183a4f17b05bea69ed5a141b470fe53` |
| [071554 B0控制](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T071554Z-b0-sql-pair/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-152045.json>) | 120.4714753809385 | 2243.983475301355 | `fce96ee95530251b0f1e5d4fb58279f4cf095806631ba728818260cf632d1cc8` |
| [072153 SQL单项重复](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072153Z-sql-reflection-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-152350.json>) | 43.09057237813249 | 6273.6692756764005 | `c5c9a2b6dca7a363ade8908ea2809c71b58d71b344c8f8a2fc53294890d9c34a` |

三份manifest分别为同run目录 `manifest.json`，本轮实际复算SHA依次 `e7a706ce2225d2a6bec0a4f6bf71f0b58920c0228c967211ba8d875e20752044`／`ef41f5b44e95b810b561e94cd3045baf80c50c58cb4c44f917360d49ee86c10d`／`7989f97849add91e8940e983e62410fa1a5d2c47adaf2faa1e8a7343005ba2ab`。原server.log分别 `fc633b208fccb68b12fc22da6e00bf1350d02ead7459c8b31cc6f5d5214695b7`／`6252e5f4f53ec9e21e75c1b7e0be9d209af1350dea29bd51eb812eba926e2163`／`979822978d24b85d36699744199157537dcbb57a8dd5f73110b5014e2a3e2d2e`。三份postflight均port9031关闭、68MiB／0%／无设备进程；这里只读取原记录，没有实时设备检查。

据同token工作量原JSON计算，SQL两次相对B0吞吐为 **2.7887783796524097×、2.7957733845762305×**，耗时减少64.1420%／64.2317%。可写“同参数／同KV条件下重复出现约2.79倍的4K短筛信号”；**不能写缓存严格匹配或确定的纯SQL官方吞吐收益**：早期没有持久调优库before／after完整快照，不知道其初态逐byte或schema／配置行是否相同，更不能外推空库、所有shape、整档原四轮或总分。相同driver／参数不弥补缺失的DB证据；不得后来补造快照。

**SQL独立正确性证据是配置反射／读写契约CPU门，不是独立模型准确率。** [072702原gate.log](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072702Z-sql-cpu-gate/gate.log>) SHA `db813e049d0448344c60ce4b502e3c035881149701bb5589ec790a01000030a8`，原Python3.12.11／SQLAlchemy2.0.48、6test／0.853s／OK，涵盖真实配置get／put及不覆盖、目标表过滤／列PK行、缺表后新表可见、引号／默认FK闭包、跨engine并发隔离、回退／幂等／hashguard。原 [source.sha256](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072702Z-sql-cpu-gate/source.sha256>) SHA `135c4ae56c969b975e779961e70145000f44815e37d000cb90e50e12acf3caa7` 锚定runtime `ad84c9affe0c3f4b9a4432dd2cbb3861306726f07d53328e129af41c74ea8e8e`、测试 `8f10a7d10885cc290a0aa7fab5fa1889471bcd2967ace7af3e452b60daccedec`、actual SQL fixture `6dc19cb581d70154f14b95ed9112d682c6b5919b6cf3f8dea01a78a75ec0efd7`。本轮只读这些log／hash，未重跑CPU门。

后续 **SQL+C2的101/105仅属该组合，SQL+C3的103/105仅属该组合**；64服务请求成功不是题目准确率。官方4K+93.3208%／16K+216.6027%来自13eb原版与完整SQL+C3（还含保留prefill／top-p／C2／C3）的描述性比较，不能拆给SQL。已有 [最终比较JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-official-final-comparison.json>) 本轮实际复算SHA `52f8da4bea6ba7caf4f517edccb9c3c0ecbe85db89f79372b0e5c1c4fc74d832`；其中两边KV521840／521936、初态DB512表19130行／489表18384行不同，已明确非cache-matched／稳定单项因果，不合成总分。

可直接用于独立中文审阅PR的最小摘要：“把SQLite配置模型的全库反射改为只反射目标表及默认外键依赖，保留配置读写与缺表语义。真实SQLAlchemy2.0.48的6项CPU契约通过；在保留performance基点上，独立4K／64请求／128输出短筛两次为43.199／43.091秒，对照120.471秒。早期调优库未留前后快照，约2.79倍仅为短筛重复信号；没有SQL单项模型准确率或官方整档成绩，组合103/105不继承。该方法现已包含于main，本PR补历史审阅而非再次合入实现。”

参考既有中文方案 [SQL反射计划](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-sql-reflection-plan.md>) SHA `800e280b9dcfcb222c603cd9bd27af6ac9241583c01cb80b0ea0c0df6dac6d45`；本轮只追加own handoff，精确源码／基点交framework单独审，不改CURRENT／PR材料／共享代码／远端，不新增设备或旧套件重复审计。

### 用户纠正GitHub起点：KV盘点收口，下一候选仅提窄方案

用户明确main必须原始待改造13eb，旧完整导入优化应保历史快照、按方法PR呈现。本owner只读核原13eb路径／现有PR3、4 manifest与imports，独占简表 [kv-inventory.md](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/docs/pr-rebuild/kv-inventory.md>) 已写完，SHA **8cc13dfb9cffc29242d11e5429a54894d2a7581a9ffff2b76fc713b01c2a448f**。PR3/4三个代码及两个docs在13eb均不存在，互无代码依赖／无SQL+C3或CPU方法前置；完整KV事务／42层SAVE接入另有真实依赖与未覆盖accuracy，不能偷渡进工具PR。本地FlagGems HEAD6ddb4c4对固定4df52d9全tree仅README修改／上游README备份，status clean，没有实际新增库内算子；实验draft不冒称部署。已同步root／systems，不改checkout、PR／远端或旧manifest。

root要求少整理、多构思下一步；下面只留**一个待批准实现的热launch主机路径候选**，不恢复Event或旧KV负项，也不写新门。社区一手 [Triton RFC #10140](https://github.com/triton-lang/triton/issues/10140)讨论受guard的已编译launch handle；仍是RFC，不能当Corex已合并功能或引用其吞吐。本实例actual `spec/iluvatar/triton/runtime/jit.py` 66a168…的737–790在热命中仍做binder／specialization-key／cache查找／used-global检查，**761的get_corex_sme仅cache miss执行，不是每次热launch成本**；此前社区报告该段若被读成“每次SME计算”必须按本实际分支纠正。候选只在eager mixed／prefill同kernel／tile／dtype／stride／scalar-specialization／globals／hooks完全一致时，于54c `unified_attention:1036`主kernel和`:1112` reducer两处复用首次原JIT返回的compiled对象，逐次传真实指针／标量／current stream，未知或capture走原路，绝不缓存旧tensor闭包；本实例CTA入口`:145 compiled[GRID](*all_args)`只证明该接口实际曾可用，尚不证明Attention新包装安全或收益大。16SM、42层短kernel与6CPU限制使逐层热Python提交有可聚合潜力，但decode已graph replay的部分不计入预算，现有profile不能定量其占比。最短可证伪方案是**小fork现有 `launch_prefill_visible_prefix_gate.sh`／`validate_prefill_visible_prefix.py`，取消省mask变换、只换热launch代理，复用原P2019+Q2048／KV16K两case及32call预record ABBA**，先同bits／整KV／RNG／新Q指针与后继调用正确，再核CPU/wall是否确实下降；没有正信号或guard不能低成本完整证明就停止，不上长服务pair、不直接合并新框架。当前没有新runtime／门／设备请求，该建议需root指示才实施。

后续root批准与framework合力准备最短热launch候选。本owner已直接发送上述五句／actual路径／挂点，与其约定framework独占runtime／特殊化契约，本owner独占后继新 `scripts/remote/validate_attention_hot_launch.py` 小fork（尚未写），原d3db门不改。实际compiler.py:542–553的compiled[grid]默认取当前device／stream并保launch hooks，但不保JIT globals／pre_run_hooks，不能裸绕；C2 `DecodeLaunch`先改kwargs为w2s1再进JIT，不能在外层误缓存w4s3参数。

framework据actual契约进一步收窄方案：**保原JIT737–754 prefix及真实binder，只复用post-binder同recipe的key／compiled**，不猜native_specialize_impl，不声称省binder。actual `compute_cache_key:605–608` 热路径确构造`(tuple(specialization), str(options))`并查dict；这才是当前可削预算。globals仍逐次原样核，非空pre_run_hooks／capture／未知回原尾；get_corex_sme只cache miss的事实不变。两方已把“范围更窄、尚无收益”报root，等待其决定是否值得试再写最小门，避免为guard搭新框架。接口预定`create(attention, helpers, backend)`→manager install／restore／snapshot，计数kernel_hot／reducer_hot／对应bootstrap／fallbacks；若实施，两case内仅加一次新Q／out指针的后继调用及非默认stream，不新增shape扫描／旧套件／服务。当前无新runtime／gate写入、无SSH／GPU／共享代码或远端动作。

root后续已接受此缩窄，先限定`tmp/next-hot-launch/`准备；阶段收尾时仅完成互审，随后新实验轮再次明确授权按原字节复制正式路径。最终 [runtime](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/patches/framework/biv150_attention_key_recipe.py>) **1fd87a989cf966e7f47b0831e9a80f82d70a043b54b60d370d7ef35e94f316c2**、[最短门](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/validate_attention_hot_launch.py>) **59074a46e8ff33c998fdf0e260dd5eef8527d1c60c68d614cf09fa604deb6cb2**，已逐byte复制且核同SHA，未覆盖旧门／已安装源／共享代码仓。tmp副本与 [README](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/next-hot-launch/README.md>) 保留API接续入口。

本owner完整只读审runtime：原prefix／FlagPrism／binder及globals检查保留，C2外对象不改，kernel按IS_3D两recipe、reducer一recipe，当前stream显式传给原compiled入口；元数据guard失败在except外走原尾，已提交launch的异常不重试。末次knobs从原动态globals每次读取并核compiler/JIT同对象，未见该两形状短门的当前语义阻断。CPU唯一stub合同`tmp/next-hot-launch/cpu-check.json`已只读核；它没有执行真实scope/probe／binder／compiled launch／GPU，不能冒称这些已通过。

门只fork原d3db两case／32call预record ABBA，新增一次不同值且新Q／out指针的非默认流producer→baseline/candidate→同流consumer→done事件；保输出bits／整KV／RNG／padding，提交thread/process CPU与窗外v1cpu.stat分开，未改56线程／6CPU。候选计时须两entry真hot；最终finally另核两JIT实例run字段删除／原class run身份恢复。初稿compile／runpy导入／help均过且无Torch/Triton/vLLM导入、无pycache写入；末次只填pin和恢复断言后compile过，未重复旧套件。framework已全文审门并对最终两块小改实读无阻断；本owner对runtime／knobs终审已回root，**可由root唯一owner串行最短设备门；本子任务尚未SSH／上卡／安装，也没有收益或模型准确率结果**。

085923后root回执：Pcase输出／KV／RNG／新Qout／非默认流均通过，但bootstrap与hot均0、fallback6，按必要命中断言拒绝，尚无可评价的候选性能。root原在该轮并行授权下一项独立C3重复view清理；双方仅重读a129／1219和对齐manager接口，**C3 runtime及本owner适配门都尚未写**，随未激活问题立即暂停，不叠hot-key也不猜放guard。

framework独占的一次首次fallback诊断已由本owner只读最小diff审：`tmp/hot-key-diagnostic/biv150_attention_key_recipe_diagnostic.py` **59c075f3cda1396e6fc3f256e2fb219ab07d1a38c1670be21e9a83b217305e88** 保原guards／数学／launch，只一次打印options内置标量、资格相关bound类型／值、Q/out dtype／device、hook与异常类型，非Tensor内容、无新增设备同步，诊断异常不改变原tail；gate **96eb5a7dec3c36550fae670b8a2181a28c3d2b554d1914256a3f857851885516** 相对59074只有policy pin一行变化。无当前一次定位门阻断已报root／framework；没有执行脚本／旧套件／SSH／GPU，正式源和085923原件均不改。实际拒绝原因仍待唯一设备owner的诊断原件，不能在此预写原因或收益。

root后续恢复C3 CPU准备，因framework优先修hot-key，本owner接手其已形成的1a161 C3草稿，未重造实现。独占 `tmp/next-c3-views/` 最终runtime **ba085577f24684cb980cdd09c2978192ff9b8b3a70fa62aadc1cfd3efced61d4**（只另加拒绝JIT实例run候选叠加）、gate **e5eef652b72cc40afb0af98649811d0eb52dea7956f237354b2c0d646ca5f460**、launcher **7418e0de944050b9d11eb6c510b140d33c4360675012c8c1d1d01bfc0f1906eb**；精确1219 helper AST仅省重复view／unbind，原a129 scope、顺序、scale／完整kwargs保留。唯一 `check_c3_views_cpu.py` 实际一次0.36s通过：真实两forward对照所有unified参数、alias／offset／非1scale来源shape-stride，slice12→4、unbind2→1，原scale异常／首launch异常不重试及restore；CPU receipt **9950432929ce80bce54b3eaf52355c87e2a0328410584e4d243e2bb9dbea6423**。这是描述符stub合同，不是GPU数值／factory实际身份／stream／性能证明；gate另compile／无框架import／help过，没有重跑旧suite或设备。

本owner同时对hot-key v2 **a67d3add779387331edcccffd863f1e1b70b76d0ffaf98cebdb8ac69f9458ac7**／gate **1f402c6d0d2de2de7c69e688028648fdc1f4f0e875264c570c3480555864acd4** 作只读定向审：仅原key/cache两行改为可复用配方，probe不launch，原globals／grid／metadata／当前hooks／run尾AST全部保留，故移除两个hook None资格不再绕过hook；唯一stub合同范围清楚，无当前最短门阻断，已回root。没有执行其合同或改该代码；实际设备结果不在本owner回执中预写。

用户最新转为按依赖合并已有PR并复用既有测试，root明确所有新候选留tmp，不再启动设备门。本owner已完成 [C3简短README](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/next-c3-views/README.md>) 后停写；C3稿已发framework，独立互审若尚未完成须按README待续，不冒称已验。新C3／hot-v2未复制正式路径、未安装／部署／推送／改已发布代码，当前原CPU组合B2由root唯一device owner收尾，不追加新实验。


### 6f 输入准备：入口等待反证后，仅准备纯decode死CPU gather候选

root已实际跑hot-key v2与C3视图门：前者P2019KV16K正确性真hot但wall变慢0.1869%、短输入又慢8.16%，不集成；后者大P2019 wall变慢0.3177%但CPU提交约省6.9%，后续105635 D29/P128KV1024正确性、真实selected68，wall0.4602182→0.4327367ms省5.9714%、event省0.6663%、CPU提交省7.36%，由root/另一owner保留与准备真实服务。本owner没有重跑原件validator／CPU旧合同／设备；之前handoff“暂停／尚未上卡”是旧时点，后继明确恢复授权与这些回执覆盖该状态。

下一原备忘考虑CPU持久状态和pinned提交快照分离，但root真实104544组合诊断先64步wait461730ns/preprocess1702852919ns，后512步wait4.078ms/preprocess10.849s，均局部快照；约0.027%/0.0376%不足支持高成本拆所有权。现不实现、不删synchronize；旧MRV2备忘buffer_utils当前不存在async_copy_to_gpu()，实际main已见UvaBufferPool.copy_to_gpu等，已提醒framework，未改其共享备忘。

root继而明确批准唯一 strict pure decode CPU gather候选，独占tmp/next-decode-gather：runtime biv150_decode_cpu_gather.py SHA1a9de781b2f9504c627991071c5ee4b52eda59ca8af283f28a15b9fab38ef7bd、最短门validate_decode_gather.py SHAf9bc1491347811027c94dbbbc80edd24c0ed55e193b18fc15654ab4e4976e4f1。只把精确6f:2011–2024生成token_indices/from_numpy/flatten/CPU index_select包一层条件；原_prepare_input_ids、metadata/async两helper、event、GPU消费者和采样完全不改。allN各1token+全有合法唯一prevrow，原GPU identity或scatter覆盖0..N−1，num_common==total故两处CPU H2D分支都不读旧scratch。CPU ids直接站点只有2023写入，间接copy_to_gpu1794/1852被严格代数条件排除；newreq/mixed/无prev/spec/embeds/MM/越界/别名/未知回原，每步资格重算。合法reverse映射不是请求重排策略，只保原映射；不承诺FCFS或输出随机分配变化。

门小forkabfc组合：双方6f+同两helper，原五case仅加identity/newreq两项；原4graph步改decode62，并要求同次metadata/async/gatherskip均1，CPU poison原样而GPU全有效IDs与独立CPU token/previous oracle相同、四consumer非陈旧、RNG及固定地址保持。controller沿原锁/child/monitor/300s清理，只增--gather-runtime-path，控制器stdlib生成/封存独立candidate，不覆6f。无timing；资格guard开销可能抵消gather节省，尚无局部/服务收益，不能预言大收益。

唯一新CPU合同check_cpu_contract.py实际首轮一次0.1833s通过：真实meta/async scope AST配纯CPU Tensor描述符、16边界和逐步失效，精确变换逆回、原GPU/CM四方法AST不变；receipt cpu-check.json。没有Torch/Triton/vLLM导入，不是GPU复制/stream/graph/RNG证明。compile/stdlib导入/help另过，未重跑旧suite；门已交team_view_final_check定向跨职责互审，尚待最终回执，不提前声称可部署。root正独占准确率／后继C3服务设备；本owner无SSH/GPU、远端或共享代码仓修改。最短恢复步骤与范围见tmp/next-decode-gather/README.md。


C3服务交叉审补充：按team/root分工，本owner只读tmp/c3views-service新service_append/prepare/launcher/check_actual_selection及唯一CPU receipt，不重审ba085数学、不执行合同/设备。c70542e6服务模块保ba085全core字节；candidate80610017保6f完整原文并在原C3安装末尾追加install_service。原execute恰一次/原异常透传、计数先后增量不含dummy历史，成功真实execute才同EnginePID首marker并撤观察器；prepare完整copy仅runner+module两路径、原bc51参数/seed/设备owner不变，无当前短服务阻断已回root/team。首命中checker不等于全程覆盖/性能门；complete_step_return只是原方法返回，不是新增设备完成ACK；DB前后/容量/环境按root原封存匹配。资料与本owner候选仍只本地，未改已发布代码或远端。


pure-gather最终跨职责回执：team_view_final_check已实际只读核1a9de781 runtime／f9bc1491 gate，确认CPU写点/间接H2D读取与全有效GPU覆盖证明、新req/mixed/unsupported fallback、逐步失效、原GPU方法/event、poison仅死scratch/四graph consumer及RNG门相互配套，无当前6f子集最短门阻断；没有重跑合同/GPU。回执由其追加同README，本owner已把最终两SHA及可由root唯一owner部署的状态交root。仍未真实selected、未GPU数学/graph验证、无服务/准确率/速度结论，guard开销可能反而更慢；不要因正确性门具备而自动扩大长测。本轮至此CPU准备与互审完成，后续只按root唯一队列接真实回执。


### 纯gather：预备独立真实服务接线，不改受测runtime

root要求在当前准确率后串行方法门，并提前CPU准备服务candidate，待GPU门通过后决定是否复用紧接的干净6f baseline。本owner独占tmp/decode-gather-service，复用已审C3服务prepare/source-map/launcher/evidence结构；原helper1a9de781逐字节不改。runner由原helper精确transform(6f)加极小真实execute观察footer，candidate b0993b84e7efcdd78ab7ead23aa55a4b0c16237041d61636a7266e065c65dad3；新增helper与runner仅两路径。原SQL+C2+C3、metadata/async、GPU IDs／CPU staging／event／采样参数均不变，不叠C3views。

preparer4dd446ba074bc8e7cd6751f7330832b05afb20fef151a054a0c16839ee7cff69；launcher f4a8a0586ee0c02050ce70513e4c05b89c7118465ace7532d56ad3977073a59f，原bc51/decode4k/seed721201命令行逐字相同、原driver唯一owner。footer5b9dcc8a…是追加到runner的缩进代码，不是第三运行时文件；真实execute原调用一次返回后，self的selected当次增量>0且N>=2才同EnginePID打印一次并撤wrapper，startup/dummy历史与单请求smoke不算screen命中。N>=2仅收紧观察，不改变N=1方法资格；原异常不记录假成功。checker c2c760dd…只首命中，不是全程覆盖/设备完成/性能门。

唯一新CPU接线合同首轮一次通过，receipt2e578428b1064ddd6f021fa781cb889bc7b7c03b5ab4f171955f0838b3f17c48：原helper全字节/逆6f、原execute恰一/结果/同异常context、dummy与smoke不报、首命中后撤/缓存wrapper不重报、原命令行及静态完整source map412→413两路径。没有整copy/旧runtime或方法门/GPU、没有设备框架import。已把可审代码与pin交framework owner，仅待其只读新增接线风险回执；其余旧证明复用，不新资料或大报告。root仍唯一SSH/GPU owner，本owner不执行远端、不改已发布checkout；DB/容量/环境/源匹配与完整封存由root原流程验收，收益未知、guard成本可能抵消。


服务包终审必要修订：framework指出初稿观察器print/读取失败可能把原成功execute变成服务异常。本owner只修footer前后观察各try、原execute在except结束后恰一次、观察失败静默retire并保原result/context；helper1a9与原方法完全不动。最终footer59864f48bb0b9d687d91b4c088fa04642a629ac3af0239e67c3daab8f5c5d304、preparer44018c6c8881e23a138a2cdcf8f4672bfd2635aab7076e85b955959367ddd33b、candidate runner70db5a6bbc5bb4bc75784ca6bce5d48021ff39aa58386853bc2872e8f8d7f16c；launcherf4a8/checkerc2c/1a9不变。原b099/4dd/5b9的footer/prepare/test/receipt逐字节保history/initial，先前回执仅历史，不用于部署。唯一接线合同加emit失败成功返回、前观察失败后原error同对象/context两分支必要再过一次，当前receipt ae9b8fb6fec47c401f3f343567c0a7f78c81189b783a9b33b8461eed3e38d594。

framework已只读末次delta并核最终runtime/receipt一致，无新增服务接线阻断；没有重跑该合同/旧suite/设备。README已换最终pins，待其末尾追加回执。完整干净6f BASE不仅四文件一致：prepare记录/核copy全map但只直接pin四核心，root首次选定BASE应单次核与封存070452完整412文件map一致再复用。服务启动/方法GPU验收仍由root唯一owner决定，本owner不提前跑服务、不改竞赛参数/已发布仓库或声称收益。


追加C3服务v2观察失败隔离跨审：本owner按root/team要求只读新service_append差分及4失败注入receipt，实核policy ebe870172f38a306201ec7ede620a85bf431c0994131c692be2ec17d67ea42a9、suffix c2cd377ca51c511efc20b46e99b27a5475fee4a6f826ced9dcf25fe7b8dbea5a，剥suffix后core exact ba085，prepare98cc/runner806100不变。前读取失败在except结束后仍原execute恰一次，后计数/json/print失败只disabled并identity条件撤包装，保成功result；原模型异常不吞/不重试，无短服务阻断已回root/team。未重跑唯一新失败合同、旧suite或GPU，不改其包文件，team负责README留痕。


### 当前6f真实GPU热点收口与w16唯一单点准备

前述纯decode gather正确性门通过后，root真实113627服务同DB/KV下6881.3277TPS，对照6936.7042为−0.7983%，不集成；这覆盖此前“尚无服务结果”的时点。输入event等待512步4.078ms/预处理10.849s不支持昂贵拆pinned所有权，hot-key两负结果也不再追。

root批准当前6f自然mixed原生诊断，本owner独占tmp/current-mixed-native纯CPU接线，第四execute入口停以含前三sampler，framework跨审通过。114435已实际封存：3步均N2/M2048/P2047，2D126call640.380398ms/60.2339%，MM504call337.191759ms/31.7161%，3D28.589193ms；真实2D512threads/regs102/shared65536。已读本地native-hotspots并在tmp/current-gpu-hotspots-hardware.md保存版本与图壳限制，不借旧92.96%外推。

root授权唯一历史未测w16点，本owner独占tmp/next-prefill-w16：policy c27a4da71feae630252c46a1cc310fed9fc6d26b2dd00783459c206dce27463d、gate279424148f3837e300646e6006d7cf2a300d19e7c198d138d8a8a418954a67b3。strict审计54c/59d/1219/C2e5，只2D BM128/T64/s1原w8→16；D1/P2047/KV16K上界fixture、原真实builder/writer和整KV/RNG/scale/新指针/非默认流门，严格bits失败停止timing且保maxabs/maxrel/NaN，不冒称模型accuracy失败。编译资源失败原异常恰一次/no retry；成功记真实compiled资源，32ABBA/prerecord/windowCPUstat。不叠C3views/hot-key、不改installed/官方参数，基点controller先核干净6f。

唯一新增CPU launch stub合同0.000137s首次pass，非GPU数学/资源证据；framework指出PYTHONPATH多项整串Path会部署失败，已只取首项拒空修正，最终c27a/279424只读终审ready。root负责launcher与唯一上卡，本owner无SSH/GPU。可执行参数/恢复/停止边界在该README，未扩矩阵/旧套件。


120226单点真实回执：exit0，strict所有正确性/原global恢复true，selected68/fallback0/原3D68；32ABBA wall11.08956495→14.60591725ms慢31.7087%，event10.98337078→14.49728155慢31.9930%，实际w16 regs101/spills0/shared65536/warp64。没有收益，停止w16及tile扫描，不集成/不扩大accuracy。本owner按root唯一owner回执更新，未另执行/重跑原件；完整封存由root负责。已更新w16 README、纯gather服务README负结果及当前GPU热点短文。

下一阶段仅建议末层删除无用hidden行：原6f4445/4451在全模型结束才gather logits_indices，当前M2048/N2。必须先保最后层全M K/V写cache，再仅N行Q/Attention/O/MLP/norm；前41层原路，不改采样N/顺序/RNG、不宣称只改gather已实现此算法。上界约一层/42，模型接点/residual/metadata/unsupported特征尚需CPU证明，当前无新runtime/合同/GPU队列。本阶段至此停写交root封存。


### 恢复主线：2D V迟加载单候选

root新阶段授权不再tile扫点；本owner用primary Triton官方FA2与FlashAttention split启发式交叉54c，选择V资源生命周期，不选缺并行论据的splitKV。具体源/反证/链接仅写tmp/next-gpu-mainline.md，未开长综述。root随即授权实现，独占tmp/next-prefill-v-late/policy89134ef1、gate8f83395f，CLI沿w16同门，exact54c仅新增constexpr开关/移动原V offset+load+cast，w8/BM128/T64/s1和FP调用顺序/原3DC2不动；selector逐AST复用87c6。首baseline观察只计编译信息，正式timing baseline原binding；raw asm哈希与资源不能单独证明调度/occupancy。

唯一CPU transform/launch合同首次0.0322s pass，generated b7aee63a…；无Torch/Triton/设备导入，不冒称同IR或GPU数值。framework首稿全文审未见新变换/SME/selector阻断，最终两pin无变化已交其末审/root；GPU唯一由root串行。末层tail局部门由framework独占，本owner只预留新增风险互审，不竞争实现。


### 121701 Vlate负结果与资源驻留反证


121701实际回执（root唯一owner）：Vlate strict bits/KV/RNG/scale/新指针/流全部过，selected68/fallback0/原3D68；资源确由baseline regs102/shared65536变为candidate regs100/shared49152，双方spills0/w8/s1。32ABBA wall11.106083→11.267372ms慢1.4523%，Event10.993639→11.136706慢1.3014%，暂不集成。新源确改变了资源，并不证明优化了关键路径；减少V前取可能损失延迟隐藏，但无阶段stall证据不能定因。

是否因此再试pipeline：当前本地env/硬件记录没有每SM shared/register/thread总量，已归档actual Triton compiler.py:164/506的max_shared_mem仅证明装载上限查询/检查，不等于SM总池。比如64KiB SM池时原64与新48都最多1CTA；128KiB池时都最多2CTA，96KiB池才可能shared1→2，尚需512线程与真实寄存器分配颗粒限制。不能从shared降16KiB直接批准s2，更不能重做旧tile/stage扫描；stage加深还可能重新占用shared。没有实际上限/驻留证据前只保此负结果，优先末层tail真删工作；将来若root自然取得actual完整properties/occupancy信息再决定唯一流水点，本轮不增设备诊断。


### 末层尾段局部门跨职责只读审完成

framework新独占tmp/next-last-layer-tail helper99d5a8c86dac67b7a2c0029842576fbd1439060525d4c6789b0ddd32703fc9ec/gate25d3e9cb194b9a6504db7f678f05d0f2113495e5bdd4d3829b82d813f153b650，本owner实读actual4源并核1e10 llama/0bd6 linear/6966 norm/7572 activation SHA。Llama233 Oproj→328 postnorm→330 MLP→427 finalnorm行独立链与同时gather Attention output/residual正确，QKV/Attention/KV不在此局部工具。首稿baseline计时多gather一份final_residual（生产原本丢弃），本owner提出实质修订，作者已删该额外工作；正确性仍比residual。最终baseline一次hidden gather/candidate两前置gather计窗，原norm maybe_inplace由32独立residual工作副本窗外reset，避免污染跨窗输入。新值/新ptr的输入不变、非默认流、RNG、NaN可JSON保存和actual v1CPUstat路径已补。

最终静态无当前短门阻断已回root/作者，没运行任何合同/设备；framework唯一CPU语法/stdlib/末行边界receipt不冒充数学门。输出N不能直接接原runner期待M的契约；这是随机权重actual类eager尾段、非当前生产AOT/FX接线，不继承模型accuracy/完整KV或E2E收益。后继GPU仍root独占。


### 专项硬件主线：保留A+B机会，先核实际loader交互

root授权公开primary+actual硬件研究，本owner已实际浏览厂商产品/支持页、FlagTree官方iluvatar compiler/driver/wiki、Triton range契约，落archive/ai/20261022-current-gpu-hotspots/biv150-resource-interactions.md。完整板64GB/350W不可缩放成本实例16SM32GiB；每SMshared/regs/thread/CTA、矩阵峰值/带宽仍未知。actual compiler a0d2:386明确ivcore11无硬件namedbarrier/setmaxnreg，软件pipeline/SMEload/prefetch存在不等于本kernel真重叠；TE-FL多缓冲引用实际是Ascend，已反证外推。

发现公开loader跨48KiB偏好阈值后，root纯CPU取回actual driver.c6d1b04，本owner独立核:146–157同分支：shared>49152才PREFER_SHARED及动态shared上限。原64进/Vlate48不进是新A+B证据，不是证明硬件cache实际变化或回退根因。已给root精确SDK补读路径/属性查询，不SSH/GPU。组合优先Vlate+保baseline函数cache偏好，次选Vlate+固定一步K预取/有限内层流水；两者均需真实资源/严格数值/一次ABBA，没写实现、没排设备，不因A单负推断组合负。

期间先完成framework tailouter75b06/987c定向终审：复用32a单锁/单child/monitor/DB/双idle/cleanup/seal，new99d5/25d3+actual4源/config、完整412核归档无部署阻断，未运行包装/旧suite/GPU；实际首门123334随后暴露ModelWeightParameter需要真TP组，不是尾算法数值失败，framework独占v2真实world1初始化，等待只读新delta。


补充actual SDK与只读collector（尚待root返回查询值）：`tmp/current-biv150-sdk-source/ix.h`真实定义IXDRVfunction为struct指针，cuFuncGetAttribute/cuFuncSetCacheConfig经mapping_cudart映到ixdrv*；PREFER_SHARED枚举真实为0x01，函数carveout/maxdynamic属性均有声明，但没有FuncGetCacheConfig，context getter不能替代。MAX_BLOCKS_PER_MULTIPROCESSOR不在该actual enum中，必须保未知。设备属性collector独占同目录`query_biv150_resources.cpp`最终SHA57326c2e1f2298654c3c0fa7fffbe2e5597dc6658775499c1f49262220a72e4b；SDK编译枚举，dlopen actual libcuda仅Init/DeviceGet/19只读属性和主context状态，不建context/分配/stream/sync/Set/kernel。只读函数属性必须同进程真实JIT handle，不能从其他进程传整数。初始生成过度C++转义在CPU准备检查发现并弃用，未编译/设备；最终无该转义层。root唯一owner编译执行，本owner未运行。

Tail v2接线增量只读终审完成：worker8e4903e3/outer510bd162/shd7568982，真world1/rank0/local0私有file URI、current config、actual1feda/ff605 API与源pin，不伪造_TP。partialinit先attempt，finally原device settle后独立尝试destroy_model_parallel/world并核状态，未settle保引用；原helper99d5和算法/32a owner链不变。没运行合同/包装/设备。root后续v2触发局部数值门失败并清理，说明真实组问题已修通但数值未过，不能写成通过/生产可用；等待作者/原件分析，不新增尾段设备测。


124857只读collector owner实际回执：最终57326编译/运行成功，19SDK属性rc0，primaryctx前后active0；SM shared131072/regs262144/threads8192，perblock threads4096/shared131072/optin131072/regs262144，16SM/warp64/32GiB，L2=16777216、global/localL1=1、asyncengine1/concurrent1、clock1500000/mem1600000/bus2048。按owner回执更新硬件研究并同步team；原包15223B SHA510c7a4f5d4ca3a155aa9c5551d6c162774844d30764d05fc56358a134859b9b正在下载，未冒称本owner已独立读原JSON。128KiB shared使64/48都最多2CTA粗界，不能称Vlate驻留翻倍；cache配置阈值A+B独立可测，属性不证明实际occupancy/峰值带宽/矩阵吞吐或完整调度粒度。不支持字段如MAX_BLOCKS仍unknown。


### 130457 cache组合负结果；一步K lookahead已CPU交接

当前root真实130457三臂strict通过：原wall11.0918682813/Event10.9864487648ms，A默认Vlate11.2275998594/11.1361632347，B加PREFER_SHARED11.2581162031/11.1335206032。B较原慢1.49883%wall/1.33867%Event；cache单因素wall慢0.27180%、Event仅快0.023730%，无可确认收益，保负结果不集成。A/B独立module/function且同binary/compilehash/shared49152/regs100，setter仅B一次rc0 enum1；maxdynamic131072/static0不变、carveout801不支持，原绑定恢复。本owner按root回执，不冒称独立完整验收。

root授权唯一下一A+B点，独占tmp/next-v-late-k-lookahead：policy1919c50be7914d7d77ff81910e84835fa6ab0589f9e9ba677dab3aa0885e7559、gateab9a47874b4234c2f7d9dbd51c98053204a4953685cafcb5a90130915e1ce5c2、generated06ad08f22f275bb696143bbe9fdcd19821d262d01d99f57860e8606863f43644。变换自exact54c两层可逆，原Vlate后移V＋一步K/物理页carry，仅首lo<hi、next j+1<hi预取，原partial mask/地址/遍历与FP调用顺序不变，3D原C2；不叠cache、warp/stage/tile。原同D1/P2047/KV16K上界层门，strictbits/整KV/RNG/scale/当前指针/非默认流过后同worker直接32ABBA；首编译落真实asm/resources，禁止将CPU目录中的fakecompiled llir字符串当IR。

唯一新CPU合同首次0.0530856s pass，9个边界/地址carry/byte逆回/原guard/原异常不重试/restore齐；无Torch/Triton导入或设备。framework已全文只读最终三pin＋receipt，无当前短门阻断，未重跑合同/设备。本owner给root可部署两pin/CLI，简短README保存恢复/失败/IR证伪边界，等待root唯一GPU run；尚无新候选数值/资源/流水/性能结论。


### K lookahead收益反证评审：NO-GO，暂停部署

按root最新“先推收益，推不出不组合不测”指令，1919/ab9只保CPU草稿，当前不部署、不运行GPU、不重跑合同。此前“可部署/交叉审ready”仅是语义与门的静态资格，不能替代收益资格，本结论覆盖其执行建议。

1. **没有驻留提升证据。** 已实读16SM/warp64、每SM128KiB shared；原64KiB与Vlate48KiB的shared粗界都为2CTA。carry一个128×64 BF16 K tile逻辑16KiB加页向量，可能重新扩大shared/寄存器活跃期，不能把Vlate省16KiB当可免费换取的双缓冲空间。实际分配/occupancy仍未知；Vlate实测慢1.45%，而cache修复组合也负，尚无资源瓶颈被解除的证据。
2. **源码只证明移动依赖，不证明产生有效异步重叠。** 本候选不减K/V字节、dot/softmax次数或CTA数；在PV前执行普通tl.load并跨迭代carry，未新增已证有效的async-load/wait机制。编译器可能调回、串行等待，或让下一K与当前V/P/acc同时存活；单凭源码位置不能证明latency隐藏收益，也没有当前kernel的K等待/stall或带宽利用证据来量化可省部分。
3. **已有编译器含预取/流水pass，但尚无Attention IR正文证明其缺口。** actual a0d2 compiler.py:307–309先assign_latencies/schedule_loops/pipeline(num_stages)，:329再add_prefetch，且后续reorder/coalesce；这不证明原K已经预取，也不允许假定原来完全不预取。本次CPU递归核本地tmp/experiments：真实TTGIR/LLIR只有183920三份MM缓存；121701/130457 Attention results只存baseline TTGIR ff6456…/LLIR32b351…与Vlate TTGIR305cdd…/LLIRceee81…哈希，未归档正文。本目录两.llir.txt是CPU stub，不能分析调度。没有原K load→PV/loop依赖、wait/barrier与资源正文，收益前提未成立。

最短后继若自然可得，仅由root只读取回上述**现存同哈希**Attention缓存IR/机器汇编，不编译、不启动benchmark；先看原版/Vlate是否已跨迭代预取、原K load等待是否可与PV重叠、carry是否打破现有SME/共享布局。无明确新机制与成本优势就保持NO-GO，不拿跑卡代替思考。本次只读源码/归档与追加本handoff，未改候选或新建报告。


真实IR补证（root只读取回现存cache，未编译/设备）：analysis/source/current-attention-ir/retrieval.json及baseline/v_late的TTIR/TTGIR/LLIR/ASM八件，SHA与130457原件全部一致。**最终仍NO-GO，但理由由缺正文收紧为实际机制净收益不足**：

1. 真TTGIR两者:291均只有M/acc/L三项iter_args；baseline:335–348、Vlate:325–332当轮K load→local_alloc/local_load→QK，PV均:383，没有下一K carry或显式async。这是新正证据：nextK与currentPV存在数据依赖上的潜在重叠窗口，不能再声称原版已经跨迭代预取K。普通tl.load实际会lower为可延迟等待的ml_lsa_*，故也不能声称它绝不可能overlap；但无K等待耗时/关键路径占比证明可兑现。
2. 真ASM baseline约1830–1970已交错ml_slb_load与ml_matrix_mad，并按lmcnt等待；当前Vlate的下一次页表读取/等待见约1445–1460，后续K/SLB/MAD也由native调度。新方案只尝试跨迭代global-K延迟隐藏，不能把已有矩阵/SLB交错又算收益；next页表必须先完成才能发K，实际sl_wait vmcnt(0)还可能提前约束当前V发起，净可隐藏时间未知。真实TTGIR两种layout还各生成一次物理页tt.load(:305–306)，源码carry单一向量不保证native页表读取减半。
3. Vlate LLIR在32768区域复用K/V shared（:543/645起），baseline的V另占49152区域（:552起），解释了64→48KiB但未得到性能提升；新carry会增加K/页向量活跃期并可能破坏复用/加寄存器。128KiB/SM下原64与48仍都最多2CTA粗界，字节/dot/CTA数不减，已负1.45%的Vlate上没有可量化正收益下界。保留1919/ab9，当前不测、不改。framework独立读取同IR亦给NO-GO，无新合同/报告/SSH/GPU。


### 真IR下一单候选：Q dot fragment循环外保留（仅CPU分析，未实施）

确认不是已hoist：baseline TTGIR:251–252在循环外load Q并local_alloc，:291进入K循环，:346才local_load成原dot_op；LLIR:1066–1081在循环体逐次从Q shared读取16个<2×BF16>，ASM的循环体BB0_37:1049–1085保留SLB读，随后Q寄存器被K/PV复用，native未保整Q跨迭代。故唯一可解释的候选是**把相同dot-layout Q local_load移到loop前并保持该fragment**，不是把源码已有的tl.load(Q)再移一次；每CTA每K tile确可删除32KiB Q shared读，dot/mask/FP次序和HBM字节不变。

布局[8,1]、8×warp64=512线程，每线程Q为32BF16=16个packed32bit寄存器；跨softmax/PV保留可能把约102regs推向约118（只是活跃量估算，实际分配/复制/舍入待证）。SM262144regs使4CTA×512线程的raw界为128regs/thread，8192线程池也不先排除4CTA；但scalar/分区/分配颗粒/CTA上限未知，不能承诺occupancy翻倍。Q原32KiB shared仍可能作为**prologue布局转换scratch**存在，只是末次使用提前后有望与loop的K16＋V16复用，让静态shared从64趋32KiB；是否真的释放这32KiB必须核allocate_shared结果，不能从删load直接声称已减容量。

表达能力已核actual spec compiler.py:115–158的IRSource可读.ttgir、:324–330跳过已完成TTGIR阶段；actual backend:365–378在make_llir里重新执行allocate_shared。因此可用隔离、精确可逆TTGIR变换只hoist该local_load，保持原dot operand类型、不升级框架/编译器或改installed。常规tl源码目前已Q-loop外却被lower成loop内local_load，未查到可靠的单个tl开关能强制fragment保留，不拟盲试tl写法。当前结论：**保留Q-fragment hoist这一条，只有CPU SSA/同步/lifetime可证且既有编译链确认删重复读、shared/regs未失控才考虑最短设备门；当前不直接上卡。** 无runtime/合同/编译/GPU新增；K lookahead维持NO-GO。本次收益来自实际重复shared工作可删，不继承任何模型精度/服务收益。


### Q fragment最小CPU实现（待新增差分终审/设备，未扩大方法）

root批准per-call ir_override方案后，独占tmp/next-q-fragment-hoist。policy80d63add1d209335ebdc2c16cc605dd5fd89e6d63d0f7b1b456990804c863097、gate6a7f042d91a509f5f0c6950c9856efcc9d0a4c22035f3747214c7d5e0f789853。只将exactff6456 TTGIR的同一Q dot-layout local_load外提，逆回精确；原Qshared alloc、dot/mask/FP顺序/循环/早退和3DC2不动，输出IR1543c2f348a96d68abda955e0333feaa1dd007eeb59593b5445d5d8a8e3f42af。原baseline真实调用后拿asm TTGIR；独立JITFunction保原fn/参数/标准run尾，只有per-call ir_override额外options，新内容hash路径xb写并验证，无installed/全局hook/原cache修改。

recipe保全部scalar类型/值、tensor dtype/device/shape/stride/256B余数及native binder specialization/options，当前tensor参数不缓存，ASTSource ABI/const/attrs亦核。描述的是caller kwargs binder recipe，不冒称重放原FlagPrism注入后options；原prefix仍执行一次，compile knobs另核同态。已补actual7e3 KVQuantMode的显式IntEnum冻结/类源码guard。framework一度把module/spec pin方向读反，本owner复读130038原error与130457成功source后澄清，作者已撤该阻断；当前模块66/a97且类方法co_filename独立锁spec。

root指出首稿逐selected读69KiB IR污染计时，本owner已在首合同前改为write/bootstrap/correctness与计时前后核，热cache禁文件读。唯一新增CPU合同首次0.0627208s通过：真实IR逆回、原LLVM循环Q读16、stubhoisted CFG判定、cache隔离/currentQout/typedEnum/guard回退/原异常一次及热path无IR读；未导入Torch/Triton、未编译或设备。门复用最近D1/P2047 KV16K上界strict bits/KV/RNG/scale/非默认流及32ABBA；真实TTGIR位置和LLVM循环Q读消失必须过，否则不计时；真实IR/资源保存供Q写→同步→读及scratch复用审。barrier摘要不等于完整同步证明，不先声称shared减32或occupancy翻倍。当前跨审进行，root唯一SSH/GPU部署，无E2E/模型accuracy或收益。


framework最终80d63add/6a7f042d新增差分只读终审完成，无当前CPU准备阻断；没有重跑合同，明确不是收益/上卡批准。固定门的caller recipe/compile_state/ABI对齐可接受，不能推广任意动态编译前缀等价。真实barrier/emptyloop/资源/循环Q read0仍待root一次实际compile＋bits门；两代码SHA不再变动。README已保存此回执，交root唯一执行决定。


### 135941真实正信号与服务最小接线冻结

已独立读本地135941 results＋真实IR/ASM（不运行全validator或设备）：所有strict bits/整KV/RNG/scale/新Qout/非默认流/绑定恢复true，selected68/3D68/fallback0。wall11.028873859375→8.811432640625ms省20.10578094%，Event10.930427551269531→8.604556560516357ms省21.27886562%。真实candidate TTGIR291 Q local_load在292主loop前；LLVM513 barrier→538–567一次shared Q读取，循环内Q读0；原K/V循环barrier保留。shared65536→32768、regs102→114、spills0、w8/s1及SME234881027不变，candidate LLIR755d0d17…/ASM16f3c32e…；符合删重复Q读与scratch复用机制，但未测实际驻留、不将20%外推服务。KV4K第二fixtureroot也报strict过及局部正信号，完整结果由root封存，本owner不重复跑。

root批准独立tmp/q-hoist-service/biv150_q_fragment_service.py最终77b489a8ed0d306558405152f94ae4c19cbc2d7132b11a56d0b9610f6e729a6d（80d冻结原稿完全不改）。私有JIT lazy初始化device binder后才挂self.compile，避免create_binder覆写；保run/nativebinder/完整真实prefix options/SME/hooks/currentstream。cold先用真实ASTSource/options正常compile/cache-hit，只有真实TTGIR exactff64才生成内容SHA路径并ir_override第二编译；未知IR返回已compiled normal缓存，非默认shape不靠fixture描述猜ABI。返回候选ABI/const/attrs同源、真实循环Q读消失才可选；original options不变，源/全局hook/原JITcache不改。运行时只当前参数，hot没有二次binder/IR哈希文件读；async/capture/动态pre-run hook等原路。未知cold最多8份实际IR/ABI/options/资源及原因，atexit尽力一次summary。

服务风险review已针对新增语义收紧：normal compiler原错误在try外透传；冷候选准备/override/proof失败只返回已compiled normal，不再次compile或launch原版；真实candidate native调用在try外恰一次，之后compiled None/观察失败保原返回不重试。只有返回optimized hash才计selected_calls；原ctor成功后的安装半变更异常rollback。framework负责独立footer/prepare/launcher与真实execute首次命中（startup/dummy编译不算），team负责compile/cache增量互审。

按root/用户“验证成本高就直接上卡”最新明确指示，停止未完成check_compile_cpu.py stub，文件头已标未完成/未运行，**没有新CPU合同receipt或通过声称**。final77b仅source syntax；已复用80d真实两轮strict方法门与framework13项footer CPU合同，不重跑。最后post-launch观察小块已发两owner定向末审，准备root唯一一次真实短服务验证新接口与命中；当前helper未部署、无服务/模型accuracy结论。新SSA/IR白名单仍仅ff64，不把root回收其它14种缓存IR或四种divisibility变体当新受测白名单。


153947 root已唯一部署77b489短服务，尚在途。按最新收口指令，本owner仅将未完成/从未执行mock改名check_compile_cpu.draft.py，并以hardware-freeze.json固定当前8项代码/源map/独立footer receipt SHA；未改helper或增加实现/测试。框架13项check_service_cpu.py与未执行helper draft严格区分。后继只读本轮真实cold recipe/IR，不盲扩白名单，当前至此停增量实现。


### 153947真实服务recipe专项：机制命中，终态计数有限

本owner只读153947 run/server.log与control/q-hoist-artifacts/319325共17件，不运行全validator/设备或修改白名单。recipe-01 JSON SHA0e1548ee42fef1992fd236c5a59ce5709a3d619c7f93da30ea9ae8bc62cc90e9，recipe-02 SHA2be59d91789de22af3a12911460edee7541a7317c50ae0e5c0e9413ba58dc5ad；二者均selected、原TTGIR exactff6456f7…、override1543c2f3…。signature/constexpr/options/target相同，ABI attrs仅raw参数49 num_seqs缺项与显式空list之差；不声称两份原ABI字典逐字相同，也不据此扩白名单。

已核两个实际保存candidate TTGIR/LLIR/ASM的SHA各与其recipe相符：最终TTGIR同e14f459760d505268aa5a6b871c95556f11c1eb009db97fe845c11a2f90f1334，LLIR同755d0d17e66437e850328f61b4686957aaa33ff5b1b021c977b2ee1e79678ce9；Q dot fragment在loop外、LLVM循环内Q读0/总32、原barrier保留，shared65536→32768，w8/s1/warp64/SME234881027不变。两份ASM并非逐字相同（3ea248d6…与16f3c32e…，尾部shuffle常量与选择顺序局部不同），均实际header VGPR114/SGPR104/private_segment0；不猜该差异成因。cold JSON n_regs/n_spills均null，不能写成现场加载后寄存器/溢出API已观察值；ASM private0亦不替代n_spills实测。机制与先前严格层门一致，但不把barrier计数当完整同步证明或承诺实际occupancy。

真实Engine319325 execute37 N2/M2048成功返回后marker当次selected_calls_in_execute=42、当时total=168，明确not_all_steps_counted；它证明真实42层命中，168不是全服务总数。保存的两cold无candidate_error/失败recipe，server.log未见ERROR/Traceback；shutdown保留force-kill剩余进程WARN。artifact缺summary.json，故最终selected/fallback/3D/record_error总数不可观察，不写全程fallback0。本轮root已报64/0与474seal通过；本专项不重复其全原件验收，也不将这些结果当模型accuracy门。配对154518尚在跑，当前无端到端收益结论。仅追加本handoff，不新增代码、测试、IR白名单或长报告。


### 2026-10-23 框架/KV主线：恢复窗口互审与公共前缀成本小项排队

root已正式转回干净6f框架基线，不默认叠Q；算子由队友负责，本owner不再准备kernel变化。既有BI-V15016SM/warp64/L216MiB/32GiB仍只作实际资源约束，不从GPU数量或padding比例直接推吞吐。旧114435三步N2/M2048只代表其mixed窗；chunk对齐、growth、terminal、等待队头瞬时fit、buffer barrier、CPU gather等已有反证不重启。team/systems又核实际DB的decode M14/16同BM16、24/32同BM32、36..40/61..64同BM64且dummy Attention早退，因此图加密暂不实施，不把31→32或33→40的行比例当可删GEMM工作。

本owner对framework新恢复native包四件增量只读终审无新增阻断：footer e13d46137f48f8bc6923676115c3f8b7dbf12e5fd4ec176721fad2b35fe0c26b、preparer671817d2dfffb267d092477420bb5309bbbc568baa4136b96ab4415d8492e0ed、driverc0e163524a0ebb4fa1dcf84b0f61103f4e8a4fa593394ba20c7aca30d967f79b、launcher579992c40eef6bb94943ec8cf61d78f72b1dc5c32321b2ca4ef6d012d351b749。首实际preempt同rid与worker CachedRequestState身份，恢复q>1且真实payload computed才start，最多8连续原execute后下个入口stop涵盖sampler；CPUknown明确不是GPU完成floor，不读Future/设备值。完整412/原longargs/原owner/DB封存不变；只新增稀疏partial puredecode N直方图。未执行作者stub/旧suite或设备。165525已由root完成，末个partial hist N1=32含31smoke且可能尚漏最终N1尾段，不能由此断言完整N1长尾不存在；窗口量级与因果由framework本轮实际分析，非本owner新设备结果。

唯一并行CPU小项为**Triton不支持cascade时公共前缀统计死工作**：actual df780 schedule1002–1009→2e91 manager520→22e FullAttentionManager590–598逐页refcount扫描；6f2591/2627–2722只供cascade资格。1219 Triton Builder没有覆盖该能力，实际c524988a…基类方法固定False；注意1219:339的False本身属于Backend，不错误标为Builder。APC命中查询、哈希、分配、free均在独立路径，不关APC。framework已交叉确认消费者链。单请求约1K页扫描只是代码复杂度证据，无当前累计成本，不据此承诺大收益。

tmp/no-cascade-prefix仅CPU准备就绪：helper e17af034150a6274c4d14c94b7bf355a1541f05929521c846a4e3de320314131；observe initfooter002007a57474d8502c9e5f29aeda5c5fa0ad610a8590920a7ed93bc5de262679；preparerff5e30cd7f537508cb633c64ba16f6c6cd5e8b81a5a88c0f0e54a095773380aa；launcheracde0581fbe11d0bb88f9949ad4f51b91de5b56c73271becd2194c5ba097d12b。root指出首稿EngineCore/Scheduler类过窄会拒实际实例，已改为已审exact EngineCoreProc/AsyncScheduler da63，未知继承不宽放；完整42层单Triton组能力只安装一次，原方法/source/identity守卫。helper默认关闭，接线只显式env开observe；原callee恰一次，异常context保持，单/多请求分别累计perf墙钟和calling-thread CPU且含相邻clock成本，稀疏累计不称全程。init安装/atexit失败回滚；完整412→413只init+新helper，runner6f与算子原字节不变，沿原bc51 owner/锁/DB/清理不新造controller。

helper中skip只保N1/O1身份guard、multi直走原callee不读clock，**root未批准skip服务**；这不是默认/已部署优化。最终helper末两块已由framework只读封口，接线小审尚待回执。当前只过source syntax与真实init附加compile，没有复杂mock/CPU性能receipt、源码copy/GPU/服务或收益声称。观察尽可能并入下一有价值实验，不为其独跑五分钟；原callee预算很小即关闭。无新报告、外部写或GPU请求。


本轮最终收口（root本地b9f1a77，未外部发布）：no-cascade-prefix已归档，**仅observe接线就绪；skip未批准、未部署、未测净收益**。不再修改归档代码或新增tests。root回传165525完整puredecode直方图N1=362（含smoke），替代早期partial N1=32作为本轮完整次数观察；本owner未重复全raw验收，不由partial或完整步数推原callee成本/收益，累计原函数wall/threadCPU仍未知。既有恢复native四件只读终审结论不变；没有独立prefix长run、SSH/GPU或新算子/调度实现。此后观察仅随下一有价值实验按root安排，不为本项独跑五分钟。

### 2026-10-23 PR12绑定结论与BQ16七段链就绪

只读PR12固定head cf1f44876e6cf9e16e8e53f160d630972e535109与原C3 a129，源码保存tmp/pr12-c3-readonly。**不存在所猜的mixed decode漏路由**：C3捕获原forward方法，方法内unified_attention仍动态取backend全局；GQA安装同步重绑原attention与backend的同一unified对象。D29切片保原token/head stride，scratch按显式stride使用，prefill maxq>1原路。没有修改队友分支或新写算子；PR宣称收益与accuracy不是本owner独立原件结论。root已据此停止补漏方向。

公共前缀173203短observe由root完成：partial128次均N1，含约32次smoke，累计原callee wall10.696291ms/threadCPU10.453319ms；只是可删除扫描成本观察，非E2E收益。后续prefix skip服务pair虽完成但KV521840/521936失配，root不认性能归因；不追重复样本。

分块对齐先纠正单位：54c BLOCK_M128打包8个Q头，真实BLOCK_Q为16而不是128。真实165525恢复start2944、target13760至16704、D29×7，A=[2019]*6+[1646]。BQ128改为[1920]*7+[320]会多一步且固定BM256 GEMM tile55→58，故停止；不以padding比例虚构大收益。唯一保留BQ16为B=[2016]*6+[1664]，同7步/同target，valid Q tile865→860，真实causal KV tile-loop计数133329→132440（少889，约0.66677%），launch865→867含新增空tile早退；固定BM256模型GEMM tile55不变，但实际新M2045/末1693的autotune与全模型数值仍未验证。原M2048/末1675不能被Attention局部门替代。社区参考[SGLang schedule_policy.py](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/managers/schedule_policy.py)（本轮读取blob197d7bbacaebde812a1c90fc0c69af88cd6eace1）的tile-budget只在AMD路径启用；本站C3单prefill/compact cu且BQ16，不能直接移植其legacy矩形padding收益。

tmp/next-bq16-chain/validate_bq16_chunk_chain.py冻结a30c7206e31de9fb12580878bf9986e980f40515449b133b8f2c7bf410c6dc51；root复用shell a7848995e36f84913a7572a42d08efc63cb9bd2f5a6c90ae6de89ea997d78639，clean6f100830，不叠Q/GQA或新policy。仅原Builder/Writer/C2/C3七段链：绝对target QKV/slots同一、不可变共享past、future NaN、相同D29构造decode长度16385..16391（非实际观测长度）；逐段writer后forward；全target/decode严格bits、整KV/输入/非1scale/RNG/padding、全新Q/out非默认流消费者后才32 ABBA。writer f182实际method签名已只读核对。计时含Builder+writer+forward七段，输入打包与分配在窗外；计时重放cache已填，未模拟真实模型/GEMM/请求采样或未来scheduler公平性/APC准入。只source syntax，无新增mock/旧suite/SSH/GPU。framework正做新增worker差分只读终审，root唯一设备owner；若strictbits失败即停止，不放宽原门。

framework已实核a30c末版与side/post checks，终审无当前短门阻断，未跑合同或设备。root先串行180643候选/181134配对基线，BQ随后。等待时仅CPU核actual Scheduler df780：RUNNING在502后/504前、WAITING在842后/874 allocate之前可调整q；后者必须用APC查询后local computed。actual AsyncScheduler da63继承原schedule，只在父1130 computed推进后处理placeholder，因此不可在返回output后改q。仅静态定位，不实现调度：text/noSpec/MM/Mamba/connector/streaming且aligned computed、预算截断非末片才可能floor16，decode/末片/未知placeholder原样。释放余数可能被原FCFS后继消费，单改q不保证M2045或7步；若未来验证同链必须额外限制唯一尾部prefill与未分配余数策略，且只成功alloc后生效、不预扣失败预算。B门净益/实际调度采样与准入覆盖未证则不实现，未改scheduler或扩研究。

交叉复核进一步限定：上述“未分配余数”只是链与服务覆盖差异的风险说明，**不建议为复现M2045新增吞掉余数/冻结budget策略**。未来若有正信号，保持原循环可消费1..15余数并实际记录M，或仅最后running且无waiting等已证无人消费scope；原FCFS顺序不另改。当前没有批准或实现reserve变体。

### BQ181739局部小正信号保留，调度不实现；下一优先联合兼容

root回传181739全部strict bits/整KV/RNG/side/post通过：原每层7链wall60.16903→60.02306ms，约省0.2426%，event60.02904→59.88879ms；原件由root封存，本owner不重复validator。其每层差0.14597ms，假设42层直接相加仅6.13ms/220.407s约0.00278%；即更宽松把3.4864s完整恢复窗都按该比例改善也仅约0.00384%整轮。这只是基于局部门的条件量级，不是服务收益或严格上界。末端无waiting覆盖未证，普遍floor余数会改变后继prefill/M及采样机会，因此建议不为该点实现复杂scheduler，不追GPU重复。

主线优先现有Q（2D，已通过accuracy）与队友GQA（3D decode）框架联合兼容，不能将二者历史收益直接相乘。只读发现确定接线guard：Q install354–355要求原unified函数globals为Attention模块，已安装GQA wrapper的globals属于GQA模块，直接叠footer会拒Q。与framework交叉后优选只增加exact GQA源码1a81409b的身份解包验证：已加载模块dict、wrapper代码/source、closure original与__wrapped__同对象、原函数globals仍为Attention54c；不通用unwrap、不改两unified绑定或算术。GQA fallback调用捕获的原unified，而该函数动态读取attention.kernel，所以prefill可达Q；decode仍GQA，C3仍动态读backend global。Q restore仅还原kernel，不破坏GQA closure或其捕获C2 reducer。当前仅建议、未修改helper/队友分支；联合的真实mixed覆盖/数值与同环境收益仍须root最短门，不继承单项accuracy成组合结论。

上条reducer措辞更正：GQA _make_wrapper虽写reduce_segments局部，patched实际不消费该局部，而调用自有global _reduce_partials，不能靠“捕获C2 reducer”论证。无冲突的充分接线依据是Q只改attention.kernel，不碰GQA自有operator或reduce入口。root已批准framework独占tmp/q-gqa-framework的exact guard与同GQA基线/联合candidate接线；本owner只审新delta，不跑组合大mock。已交精确PR12 helper1a814与6f+GQA footer7686–7703。GQA stats()可提供calls/fallbacks，但FIRST_WIDTH与calls增加均在native调用前，且可能startup/capture发生；真实execute成功返回后的当次delta才是该次Python调用证据，graph重放counter不增不等于GPU未运行，完整结果仍由原服务验收负责。

已对tmp/q-gqa-framework最终helper51fcaf55133124c2e51dfa0385e1939bf908b65f8444ac63f912329f6ca73800新增guard做只读末审，无当前短服务接线阻断：只import sys/固定GQA SHA/新增安装时身份检查；兼容原canonical函数，GQA限自然已加载且exact源码与实际codefile、globals、installed标记、freevars=('original',)、closure original is __wrapped__及其原54c globals/file。没有通用unwrap调用、重新绑定入口、compiler/launch数学或新热路分支。@wraps表面module/name不用于错误识别。完整preparer efdae5f4…与launcher77807610…已读，基点412→GQA baseline413（exact PR12 cc7f runner）或candidate414（追加Q helper和原409e观察footer），同bc51/seed/原screen/设备owner，不动队友算子。没有执行mock、旧合同、拷贝构建或设备。root可先baseline；现409e只输出Q真实execute命中，GQA startup marker不足独立真实调用计数，已将stats()复用与graph重放限制交root决定最短证据。未把单方法accuracy/吞吐继承为联合结果。

root已启动183552 baseline。candidate新增observer0f25839e84f26e9b376892757b664977ba8e95c374a3c69484b6a7fe0a58e778与preparer765f39e214dda18e346a5a1fdd361ef98b02f9ca804f381f2e9e7a16b0e628bf小delta只读终审无当前阻断：在原execute前后读取已loaded GQA.stats，原模型一次在try外，Q/GQA可各在不同成功execute记录首positive delta，齐后按identity撤观察；计数/JSON/print失败只retire保原返回，不改算术/路由。明确Python计数不含graph replay、不是GPU完成证明；若GQA只有replay未见真实Python delta，观察可能持续到结束，此时保coverage限制，不能反称operator未运行。不新增probe/mock或重跑旧门。

社区并行只保一个未实施的小候选：**每步页表仅传活动列，固定GPU full stride/地址**。第一手[2026-08-13/14作者报告](https://github.com/ryanzhou/deepseek-v4-flash-mi300x/blob/main/DECODE-OPTIMIZATION-20260814.md#3-copy-only-active-block-table-columns)及[Apache-2.0实际patch](https://github.com/ryanzhou/deepseek-v4-flash-mi300x/blob/main/patches/block_table.active-width-copy.py)（读取gitblob9be910b567b0aa381a464f88e166140c2459ac50）用max(num_blocks_per_row[:N])裁列；作者MI300X/5组40.9MB收益不搬到本站。actual b3a6649b… BlockTable166–167仍每step fullwidth，6f1979 commit；旧zero-dirty工具只跳零修改或完整copy，裁列曾列后继但未实施，故不冒称新发现热点。本站31×8192×4约1.016MB，若最大已分配1060列仅131440B；属于字节上界，非已测时间。Corex非连续copy可能内部pack/多launch，且dummy/capture padding device写、row move/reuse、有效列界均要证明；先用既有trace确认预算，过小即NO-GO，只有值得时才固定stride一轮字节/guard/stream+copy-wall/event判别。不立即实现或申请GPU，不建dirty状态机/新算子，不将其排在Q+GQA联合前。

新增配对审阅已收口：compare_service_pair.py17686721f6b5b79c18410dced9a7f52ef29e0321fd212c3cad33324fd68d857f全文静态无当前门阻断，413/414完整source bytes、原bc51/SERVER/load/seed、DB四端/KV/packages/CPU quota与后态才给single pair结论，GQA基线无实际observer与graph重放计数限制已明确。root准备的accuracy8786416e9fdae6f9ac7f8a7b3e437ce5385d0c49be06aeed00b1ff52fb05bc52仅相对旧Q准确率launcher改新414 source/ref/三pin/run名称，原35d driver/官方脚本/SERVER不变；仅可信服务信号后由root决定执行。本owner没有运行raw比较器、准确率、mock或设备。

active-width只读预算/反证：旧a3 rank0.1792531794497726472.pt.trace.json.gz SHA13a2571c16317876b571f4b9152f0881c290cdbff3b13740fc746a29236eb04d含4次原8192列H2D，1835008/1802240/1802240/1769472B，设备69.473/67.907/79.780/66.707us，中位68.690us、累计283.867us；是旧54–56req/旧方法profile样本，不是当前6f稳态预算。当前114435/165525 native SQLite的cu_memcpy均0行且无Memcpy API，不能从空表断言上传无成本，也不能回填69us。实际wheel是2.10.0+corex.4.5.0；[上游同minor Copy.cu](https://github.com/pytorch/pytorch/blob/v2.10.0/aten/src/ATen/native/cuda/Copy.cu)的copy_requires_temporaries与copy_kernel_cuda明确使非连续CPU↔GPU经过临时contiguous buffer、H2D、GPU copyback，不是自动native2D。本地5.3.5 copy_跨device亦redispatch，未找到exact Corex派生Copy.cu，故不能声称当前二进制必同上游；但足以**NO-GO直接照抄两维切片.copy_并当成零开销2D**。只保显式原生2D一call、固定stride/source pinned/原event生命周期的后继可能，预算与收益未知，不新写门/请求GPU。若未来推进，真实commit门必须比较有效已分配列（不用seq_len冒代）、保tail/padded rows原初始化、dummy/capture完整原路、row move/swap/reuse和graph固定指针；候选的width计算/提交成本需入窗，不单报减少字节。

root回传组合服务21项可比门通过、相对GQA吞吐+7.466632%/TTFT−9.416976%，184819组合官方accuracy已由root唯一启动；本owner不重复验收或设备。active-width继续只读165525最终native-events.jsonl的decode_histogram：1838个观察step、∑N=28560（含smoke且原字段workload_complete_not_asserted=true）。由6f每步一次full8192列上传公式得935854080B；若仅拿旧trace约26GB/s算纯带宽项约36ms，**不是当前传输/critical-path实测或净收益上界**。此体量不支持MI300X40MB/graph的收益外推，未知host提交与copy/compute重叠仍不能被该除法替代。结论维持低优先暂缓native服务接入、不贸然测；仅在一call无packing与真实commit预算有证据时，才值得一个固定stride短方法门，不写新实现/mock。本轮调研到此收口。

### 当前组合GQA host wrapper缓存提议：NO-GO

CPU只读exact1a814源码与184141原server.log，不运行设备/导入框架。GQA536/552的inspect.signature只在install使用；patched394无signature.bind。actual1219统一入口及C3两子调用均keyword，399的位置参数映射不走。scratch三次narrow已按output data_ptr/stride0/segments缓存436–446，不存在每层重复narrow构造的已知热浪费；_pick_segments只是整数ceil/power2，不能从代码短循环推大CPU成本。成功GQA直接调用自有_gqa_decode_attention/_reduce_partials，不走原C2 DecodeLaunch代理；原hot-key已负，不能将同类binder/keycache再包装成新框架机会。

coverage有实际证据但不是耗时预算：184141 Engine339894 execute43 N2/M2048成功返回后同时Q delta42/GQA delta42，说明mixed C3每层Python wrapper确实暴露；原log FIRST_WIDTH出现在FULL decode图捕获期间，puredecode重放本身不执行这段Python，不能将capture成本逐step累计。当前剩余每mixed调用是eligible静态属性/kwargs检查、整数segments、stride读取与两个原JIT调用，没有current组合的threadCPU/墙钟分项或稳定暴露预算。故**不实现metadata/cache新候选、不改GQA算术或路由、不重做hot-key/另开长诊断**；未来若已有有价值profile顺带证明该wrapper是host临界点，再讨论只删除确定死工作。已同步root；184819准确率保持原owner在途。

root新workflow scripts/remote/seal_completed_accuracy.py 716e3518bb15775f6758ddd15947f476782bcf74b322b2d73f3991ec5af39a41已全文只读，无当前184819封包阻断：限定run ID、终态exit0/evaluation_completedTrue/cleanup空，live完整源map与manifest归档SHA、owned PID退出或Z、双栈闭/GPU68MiB0无进程；唯一math_500报告parents[2]正确落timestamp目录。原review_accuracy_gate的rc0/1只要valid都封存，accuracy_gate取原JSON，封包exit_code0不是accuracy通过。报告/命令/两脚本副本/seal/archive均exclusive，新失败留下原件不自动覆盖。无Torch/模型import，未执行脚本/mock/设备。复用小边界已告root：EngineCore regex只认无后缀日志，当前实际格式适用；未来DP后缀可沿既有comparer小改，不据当前review夸成任意worker拓扑覆盖。

tmp/q-gqa-resume-native已完成新增身份/ENV只读终审：preparere4e4bfe30cfeb52550b35e80687a643422bbfbcf735728fd27d543287d2111cf、launcherd9b40acd01f931fd17c35a717a87caa232fc9633b725df9e34ea11316eb29d04；原footer e13d4613与driver c0e16352逐字节不变，完整414 mapbf69d06d…锁当前cc442/GQA1a814/Q51fc，不叠191047准入observer。只runner末追加原footer；新control绝对Q artifact目录ENV已补，避免ctor因缺ENV拒Q而错当组合。原longargs/seed/native窗口/单owner与清理保持，已回root可唯一部署，没有执行合同/旧suite/设备。后验须组合真实markers与nativevalid，ARMED仅安装；窗口含同批所有decode/GEMM/sampler，不能全算victim可省重算。窗后N直方图及其monotonic档间差只回答CPU提交cadence，低N尾部没有GPU采样便保持未知，不套旧6f3.486s或新造第二大probe。

192308独立只读原events与SQLite视图cuda_kernel，不运行framework唯一reader/全门：Engine345934单stream1、3696kernel、可见首末span2.855519772s/activity2.807461640s。真实7步2944→16704，target6×2019+1646=13760（不是191047的13672），旁路29×7=203。2D294call/1.587201499s、全部regs114/shared32768，与Q资源一致；GQA294call/319.573598ms＋自有reduce294call/2.528606ms；MM1176call/776.657018ms，与framework唯一输出192308-analysis.json相符。这里只审新GQA name分类与CPU cadence边界，未重跑其工具。初先按root准备要求落了一份摘要稿，随后获知framework拥有唯一reader，已删除未执行稿，不留重叠入口或假结果。

本轮恢复成本不可全归victim：旁路decode GQA约322ms本来就需要，其他decode的MM/sampler亦不可删。仅“删除这次重算、其他保持”理想反事实里，把全部非GQA activity都当可删也约2.485s，仍很松、并非有限调度策略全轮收益上界；低N1/N2没有合格恒bin采样则保持未知，不再补诊断。root已明确有限策略只测试总成本能否降低、不保证无抢占；本owner结束native分析，接续只审finite新增horizon/原allocator与FCFS回退，不扩新报告/probe/旧合同。

### 有限首完成窗口准入：新增语义与接线只读通过

最终helper `tmp/finite-growth-admission/biv150_finite_growth_admission.py` SHA8f564dd5340a6ce796ffec0dbecf9e41b607fc0649304f387be327e98d64a6c5；只相对原growth-v2审新增finite逻辑，原_remaining_blocks/_wrap_schedule/_require_original AST相同。191047原before_allocate实证step276/running30有29个合法anchor、H791；computed==known、placeholder1、next_decode_eligible_step==current可触发，并非永远拒绝的纸面scope。所有resident和fresh WAITING都保完整prompt/current，有限未来为min(H+2,remaining)，再与computed和current+placeholder取max；不借未来释放、只原predictor计算新需求。fresh/APC0/preempt0/output0之外、未知状态、empty running均回原分配器，后者避免无人运行时自身阻塞队首。没有新增页预留、队列重排或采样操作；H+2只是固定异步窗口假设，不能承诺无抢占、完成期限或收益。

接线footer bcf83c5b03b83dbe20121fc35b1ad797b564147a3132803bbaae8dac30e6e7e7、preparer ed5876b8e05bdd44c621848db33c8d1238c094bf506f4ffd15be92c8cb007aca、launcher58d4a6f0ccf4c61cc6f6159d04204a95494f4215120aa2c9a9a2398ec180a16c均新增差分只读无阻断：完整QGQA414→415仅init/helper，runnercc442、原bc51 long/seed及Q artifact ENV保留；INSTALLED仅安装预检，实际FIRST_CHECKED/DEFERRED和结果仍待root唯一服务门。已消息回root及两owner，不运行mock/旧suite/SSH/GPU。framework补充192308端点cadence为N2约21.152ms/count、N1约27.893ms/count（后者含shutdown/drain），仅CPU事件间隔，不升级为GPU步时或finite策略可省尾部成本。

下一并行点“保住被抢占KV/APC”暂为NO-GO。CPU只读actual single_type_kv_cache_manager 22e3677…:408–409已reverse逻辑页释放，尾部先牺牲；block_pool 3fc5dfe…:622–635将无hash页prepend、hashed页append，故有效前缀已比自身尾部及较旧缓存晚淘汰。get_new_blocks:556–563在真正重新分配时才撤销hash，不是preempt主动清空全部有效KV。再提升ref/移出free会占用仍在running请求增长必需的容量，可能把原一次抢占转移为另一次；单改eviction优先级则尚无实际页级链证明存在可无代价替换的更低价值缓存。192308的2944已保前缀/13760重算仅证明结果，不证明这种可替代空间。该点并非旧full-output预留，但仍受同一32GiB容量守恒约束；没有新operator、host offload或有效共享页证据时不实施、不新开诊断，先保有限准入当前服务的正负原件。

有限pair比较入口03e523ce54a1fb965c132564b5aec06d062aac7a822e77eb250249a7593162c6只相对176867旧入口审新增delta，无阻断。193302原UTC/Prometheus/v1cpu.stat格式只读确认兼容；没有运行比较器或旧21门。完整414→415 map、原命令只finite ENV/marker差、FIRST_CHECKED/DEFERRED同Q/GQA Engine及future>free/H>0均受验；series前后标签与exporter process同一才报CPU/抢占差分，不将exporter CPU当总Engine CPU或累计throttled_time当wall损失。root已知candidate KV521936与baseline521840失配，新same_KV门将可比收益置null；仅保描述比例/机制观察，不追配容量重复轮，不申准确率。

193302/194020/194634启动容量差只读专项：三server.log均无DETERMINE、init/requested/nonTorch/torchpeak/nonKV/available或graph估计原值；manifest和control也未保存相应profile分项。实际仅KV521840/521936/521936，三worker完全同a8de1780…，同torch.compile cache f7af72be36与AOT7a5165…，同原SERVER/util0.85。candidate Engine安装marker在权重加载前，只证明安装顺序改变，不是非Torch或峰值分项变化证据；helper无直接设备API/分配，也不能反证传递import没有间接影响。a8de:595–598公式仍requested−nonKV−graph_applied，本轮缺值不能计算各项。尤其96token/6页对应KV payload差4128768B=3.9375MiB；此前带6a样本已证的4194304B nonTorch差不能回填本轮或据页数逆推。原log SHA分别ef2a5e85448d9c1d63577a0c0530aea0e0e5a1211461cea38a5929c9404788b2、842747cb9ab9c417edbd61e9f8e734f2c2d3361842951f0ee6efd3fd50a4e6d3、61c12957559b7f4359e24050c4081eceef2fcedd7fb6bf27d94a7512ed945e52；结论仍归因未知、KV门失配，不能把表观约1%当严格收益。只读现有原件，不改代码/新测/配容量追样本。

复用memory observer仅条件GO：原6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c仍沿自然已加载Executor/真实worker接入，不主动import WorkerFL、无新设备采样/统计同步或Snapshot，单次原profile结束恢复三hook。旧215849/220122两startup相等并未解释历史差；222731专项de35192…只定位profile前已存在的4MiB nonTorch差额，非allocator/分配来源；两个observed pair c7f7ffa…各自可比但跨组521840/521936，证明该观察器不是容量控制器，不应称已失败控制策略或据观察器存在保证容量相等。初稿提前import WorkerFL方案只是CPU阶段撤回、未部署；旧full-output reserve负结果是另一准入策略，不能替代这次分项解释。

当前最小新增接线缺口明确：QGQA414 init e043b789…在原白名单，可末尾精确append；finite415 init c9a2da56…不在，原字节6a直接接将REJECTED。若root决定复用，仅独立副本新增exact finite init允许值，两侧同observer资产、完整原footer之后追加，保原executor/worker/io/CM身份守卫、原返回及finally；不改旧6a/原件、利用率或KV上限。当前a8de/6d8仍相同，未知executor依赖由原loaded guard拒绝而非宽放。实际后验必须同Engine的DETERMINE_RETURN/profile1/PARENT原list/三restore，ARMED不算完成；只能回答本轮差落在哪个profile项/快照阶段，仍不能证明finite import因果或约束未来容量。未复现即收口、不追启动样本，不单独longbenchmark；失配收益仍null。此轮未改实现、执行旧合同、SSH/GPU。

root随后批准仅QGQA414/finite415两次最短smoke（原bc51 --smoke-only、SERVER/Qenv），本owner已按批准创建独立tmp/current-kv-memory/biv150_kv_memory_observer.py SHA9d43de58bfe587e3f80cbc8aeed2174f03755172858817fb7c90769374aef119。相对旧6a仅EXPECTED_INIT_PREFIXES新增finite c9a2da565f519ea6ebd5edb9b2456ccc4f077141af0fbc00e907f1ecb34df363；删除这一行后逐字节逆回，syntax compile通过，旧文件未改。INIT_FOOTER与原scope/NoNewCuda/单次RPC/CM/三hook恢复全字节保持；未执行stub/旧合同/远端或设备。新pin和原footer已交root做完整map接线，待新增部署差分只读互审；两次未复现即停止，不以此转换成新性能pair。

root再授权我独占当前接线：prepare_current_kv_memory.py SHAe3b93fe293a054db0704e4c2dc5f4e0dc6bd0ae08be844eedea2709c1f826bb7、launch_current_kv_memory.sh SHAafc2e1731341845dfc9132d944242a1f5c0dcfb5893805eefd404ef213112bf5。CLI仅baseline|finite，每次一侧；原bc51 --smoke-only/seed721201、VERIFY_RESTORE0/Q artifact ENV始终，finite ENV仅finite，baseline明确unset防继承。原driver唯一flock/进程/清理owner，后置轻wrapper只验同Engine DETERMINE/profile1/PARENT原list/三restore且无observer拒绝，control另存runner-exit-code，不改原driver exit-code。不新增Q/GQA真实execute门，root从原32token smoke/logprobs/tokenIDs原件读取。原完整map镜像bf69d06d…/7ad1f1acd9188b617a879f7e5de97c883fddf5ccc7981cbb27e0e474f92043c7，基点414→415/init00e8与415→416/initc037eb5b85f36dbfb6a7c027ebf2d267404b8759fb9a6919b6106e7bda327f5b；receipt外置，原runner/worker/Q/GQA不动。mapping AST同旧finite，源/三个heredoc及两实际init append仅syntax compile通过，无copy/旧tests/远端设备。root已全文接受准备部署baseline，故不再扩测试/门；framework已在做新增差分只读审。

两次current smoke已由root验收；本owner仅读原server.log分项，与analysis/current-kv-memory-smokes.json（ecc29b31b9c4fe291aae0df58958202b56a9212b244b7b8ab3798ff350e74c17）一致：201344 baseline Engine354441/KV521936，201518 finite Engine355062/KV521840；各profile1、同PID原PARENT列表及三hook恢复。init/before_create全同，finite在before_profile已多4194304B cuda/nonTorch残差，after仍同差；profile过程自身nonTorch增量两侧均60817408B。weights5101233152、torch峰增656424960、requested29205777612.8、graph0不变，故本次available精确少4194304B并因整页floor少6页。方向与旧性能pair相反，不能回填旧pair或归因finite安装/具体allocator；nonTorch仍是总占用减reserved的差额，非分配trace。建议停止独立追这4MiB：组成/出现阶段已知而来源未知，继续allocator诊断不值得新增样本；但容量门不能因此忽略，约1%表观信号仍收益未证。只更新本交接，不新报告/测试/SSH/GPU。

root新official接线tmp/q-gqa-official/launch_q_gqa_official.sh SHA815f443c0399cae1bcc94fd8313f7eea4dc22b1f3aa233a3f5093456a9223359新增风险只读无阻断。bf69完整414 map与184141原件逐byte相同，原source/control副本双map核验，无finite helper；env -u finite、绝对Qartifact、原official79119f/common35d/benchmark0813与官方两case×4不变。仍只有原driver的锁/owner/清理，终态后才seal，不因安装marker冒称实际Q/GQA或准确率重过。只两个Python heredoc syntax与Git Bash -n exit0，未运行模型/旧工具/设备；已消息回root可部署，真实execute/原CSV均值/DB/源后态由终态原验收负责。

official202736由root唯一启动后，按授权准备tmp/q-gqa-official/seal_q_gqa_official.py SHA5d60263eab32eb572c91551ee11aa0d65f46de2e0edbf08e96f82509db72ad30。复用原accuracy终态封包模式，只读official_benchmark_completed/exit0/cleanup空、原validation八行两摘要/4轮skip1/第2–4轮均值flags与对应CSV哈希；不再调用validate_outputs或模型。完整414 live/control及manifest归档字节、exact launch815f/原Q ENV/finite unset，实际同Engine Q/GQA成功execute和无finite、DB前后完整、runner/server/benchmark/Engine PIDs退出或Z、双栈闭/68MiB0无进程才独占写post/review/自脚本/命令/rawseal/tgz；任何既有输出先拒，不覆盖失败原件。CLI仅run ID，无新设备owner/锁/清理动作。仅syntax及subprocess静态限定只读ixsmi，未运行/上传/SSH，root将审新增接线并在原driver终态后决定执行。

root终审后仅新增installed-live六行，最终sealer SHA bf2ec87c7d3ca42c1aeed2ae5d05121ce7c90d8d038d6a29a12b4982cf3c1c58；本owner已只读确认manifest installed/映射实际site文件SHA并保存installed_live_sha256，删除六行逐byte回5d60263e原稿，无import/设备调用/重测；无新增阻断，未执行封包或旧suite，此项收口。

skip-computed-H2D新增只读审通过：tmp/skip-computed-h2d preparer23d833a1bd3f4155652a2457b19bdaedf29b918de488e18e5b986b2cb5e08427、runner97f41ac455cad0db7c8ddfd2b9809e77326b6472285cb14e56ce486f2f0f7443、gate461676a0b6517e5c832d315fbcfe18aff059ad0bd23cf14e51da7f34cfe4af42。只把原else computed H2D延到metadataFalse首部，原async条件/body、metadata helper/event/0e961与1bb85及所有算子原样。全runner实际GPUbuffer消费者为2194/2198的metadataFalse位置/seq计算，及2229的async+mrope drift；helperTrue明确拒use_async_spec_decode，故True分支无该值读取，未知False仍先补原copy再原消费；其它num_computed字段是CPU/request状态不可混淆。方法门保原5case/4graph/input_ids与同双helper、True全毒/False完整方法恢复当前前32行；root抓到的无消费者computed尾部误比较仅删一项，旧d5f22完整保留，不填平尾部。原controller唯一锁/child/清理、CLI四资产匹配，只三源syntax通过，未重跑fixture/旧suite/SSH/GPU；真实async-spec校正body仅源码保持而未新测，方法门不是服务净益或新accuracy结论。已回root/framework可部署短方法门，当前official不动。

skip-computed-H2D新launcher e8f9bbf773e7f0b703f3a07c709c5e03324e0210f2a9d14ee1911e97348726dd与tmp/deploy_short_gate.py当前5652c794…的唯一skip分支增量只读无阻断：bf69完整184141基点、prep23d/gate461/owner607固定，PYTHONPATH=base:原scripts，四CLI及无位置参数launcher匹配；两helper来自原冻结base，无漏传async资产。deployer只复制四件并SHA验证，launcher双栈/68MiB0无进程预检，实际gate原controller仍唯一flock/child/300s/monitor/cleanup，不新增owner；finite明确unset，方法抽取门不需Q artifact ENV或模型构造。只heredoc syntax/Git Bash -n exit0，未运行deployer/SSH/设备/旧suite，官方在途期间不得启动，已回rootready。

tmp/skip-computed-h2d-service新服务接线preparer e174044c38fe21351c23922d1307003a47e876513a8864a03eb5e3be4c96f1f3、launcher c342134afdf2414c0c3931b24dcb8f8a4508a4ebd2dc7fc7ce2bffb738f22251仅新增风险只读通过。固定184141完整414/mapbf69，candidate只runner97f且对425输出map；纯stdlib transform经runpy仅加载定义，不执行main。部署前方法门461真实exit/manifest/status/graph/fallback/RNG字段与六归档源SHA全部必须符合，未PASS即拒复制；未重跑gate。原bc51 decode4k128/64/c64/seed721201、Q绝对ENV、finite unset、source/control/DBbefore保持，purpose.source/fullmap/plugin-source/runner.pid兼容原seal_framework_screen，原bc51唯一锁/child/清理，不加observer或controller。未复跑旧检查/模拟/GPU/SSH，当前official不动；已回root/framework无接线阻断，方法局部正负不能提前继承为服务收益。

swap收益判断更正：撤回此前将0.06%–0.20%或接入验证成本用作“当前swap无意义/更无优势”的推论；前者是省ZERO对照，旧swap→no-swap因为KV失配仍未定，重算提速只降低机会成本，不自动证明swap无净益。现有experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic/native-events.jsonl中stop.executed_steps明确唯一target的q=[2019]*6+[1646]、payload_computed2944→15058、总13760；其余29条每步q1。原native-trace.json只读cuda_kernel视图中kernel_unified_attention：grid(127,2,1)252call/1252.646547ms，grid(103,2,1)42call/334.554952ms，恰7×42层；另_gqa_decode_attention为grid(29,2,8)294call。因此全部1587.201499ms 2D可归属目标本次恢复prefill，而非按token占比分摊；与tmp/q-gqa-resume-native/192308-analysis-endpoints.json的window.events.stop.executed_steps和kernel_sources_reported_separately一致。可归属不等全可避免：preempt仅CPU known/computed，GPU完成floor未知，安全可SAVE R/恢复尾片及当前真实同几何往返、同步/host分配/RPC/重准入时序仍缺。776.657018ms MM属于全batch不能全归target，322.102204ms GQA及reduce属旁路203token不可删；不把旧构造copy单次样本直接相减得净益。保留当前swap净益未定与这份明确机会证据，后续由root按组合源闭包/复制机制决定，不改短门队列或新增GPU。

另有未测的反向搬运具体机制：只读experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/server.log（SHA58cf312b903604c8c6200fb41d44b34c3175a8988d2b4271201047b9cf50fa50）唯一RESTORE_FULL RPC_ACK.command.pages，1043页/R16688/717717504B原序已升序、66连续段。沿818e规则保三个长连续段796/37/147页，仅singleton区取正恒差，14段精确展开等原数组，其中4线性/10二维；理论42层2772→588次API，最大目的pitch33570816B，bytes/逻辑映射不变。旧818e prepare_save只cuda源→pinnedCPU，0a4d桥硬DeviceToHost，descriptor.kind仅线性/二维而非方向；不能交换指针冒称H2D已支持。当前未找到该反向点已实施/否决证据，保留为独立框架搬运候选；次数下降不等时间/净swap收益，未实现、未测，也不叠进仅source身份重定的首个QGQA+FULL组合判别。

tmp/q-gqa-kv-swap新组合增量只读审无阻断：worker2de7802d7b07d6f11c8e8f304df36d5503c1189cee9d4ad60f3fbc80fbb98a52与protocol91185a23dd56cc7b1d882e9b4b3ccbfdb0d491dce060e658b183ee563d04d3ab各唯一runner锁e155→cc442，独立逆换逐byte回a662/1aff，旧事务/queued/SAVE/FULL/失败settle语义不改。preparer6d09374054f2ae1df54f7dc9fceb5e221eae3f8b39bcbaf5a93c0500c5181cc4与launcher1bd16b321ae7d1d11e105f7c0e3ed19e3712afb059b1989a5974556872d8e03e固定bf69414→82514a24422，只init旧footer+8资产、cc442及Q/GQA/metadata/async不变；SO邻接命名/原bc51long/seed/QENV/finiteunset/VERIFY1及原owner/sealer接口保持。Q观察包ctor/execute，protocol包Core与原_update_states，没有已知相互覆盖；GQA只读KV/自有scratch写、writer/storage地址不动。不叠RESTORE pitch/selector/单H2D；反向pitch独立材料已保tmp/q-gqa-kv-restore-pitch/README.md SHA9cecaf02399571d1207b447b2e0be97838c7f234f18b542489a421a54aa6ac70。已回root/framework可做隔离VERIFY1，非已经证明组合正确/净益；实际两组42byte/runner六checks/原consumer/QGQA/host释放及原件仍须本轮，旧accuracy不能继承。未重审旧suite/运行设备/SSH。

首VERIFY1 reader6807e3ae75fd5e565f5a4f16502b81cfc57f3e0551c088fa35491a834a93ab56仅新增适配只读无阻断：2071/81f原raw+FULL段保留，422源与新包装pins，SAVE用818e纯整数plan核动态segments/linear/pitched/fallback，源free前42验证与FULL目的42验证分开，同ACK Engine的Q/GQA成功execute/N>=2/M>0，不将合法stream0拒绝或提交当完成。safeR明确raw缺完整issued/queued/known，不能独立重算上界。未运行definitions/inspect/raw/旧run。可选一项最小收紧已发作者/root：同旧compare要求gqa_python_count_excludes_graph_replay=True，且两marker可在不同step，不证明恢复那一步的全层路由；固定observer源码本已发此字段，不阻塞先部署，也不扩suite。

root回传213134 VERIFY1经新reader6c5f73aa实际PASS：32/0、R16688/1043页/717717504B、源/目的42字节、SAVE210/FULL2772/0ZERO、原consumer16、KV521840/DB540稳定；本owner不重复原件验收。仅新VERIFY0 launcher f5ea8719d6d3fe50b4695a3024307bd0689763e3614a4c3a20ed3d737fa9f817只读无阻断：固定184141414/bf69与213134422/8251，原control/live/归档全map及四来源文件保持；不重建或改源，原bc51long/seed721201/SERVER、两侧VERIFY0/Qartifact绝对ENV/finiteunset、原driver唯一owner和sealer接口保持。先验exit/post不是自动取代人工字节验收，root已PASS；每次单侧、当前卡/双栈重查，无自动pair/重复。已回root可baseline，未重审VERIFY1/执行旧检查或设备；可比性仍待真实DB四端/实际KV，不预认收益。

后继独立H2D实现已按root授权只落tmp/q-gqa-kv-restore-pitch/：biv150_kv_pitched_restore.py SHAa7439c2c0b2b588dcd2af5c66b6eb62e562132ef8b5bc1d54ce54fc4b6e9804c；biv150_kv_pitched_restore_bridge.cpp SHA48295ffde897cce988d3a8460904ab4451669e1de2fbe2bd5257d3f75e35ab20。显式传原已加载818e runtime，make_restore_plan/prepare_restore/RestoreBridge只增加恢复方向几何，旧0a4d整个字节是新cpp前缀，追加SDK HostToDevice入口且原D2H不动。全batch1/42层、pinned/raw/storageoffset/范围/无alias/1GiB在首copy前验完，超pitch只预拆；提交返回completion_ackFalse，部分失败抛出/不旧路重试。独立helper不证明fresh/ref1/unhashed或目的资格，后继仅FULL原_full_restore_plan/绑定/fence之后替提交，原_finish事件/42层c95f回读/serial/phase/失败slot强引用必须保留；当前没有worker/协议/launcher/已部署8资产变更。

唯一CPU check_geometry.py bf6c4f3597b04c0e3e74ab27f7fdf45f979694e1aecb0e33cd6a52db2a6ce480一次exit0，cpu-geometry-check.json SHA49719dd50d6b1640305633d52df05c9acac0d7f31a08142f003bd920c4caa1fa：042225实际ACK行215/pagedigest核对、全原序/逻辑映射14=4线性10二维、42层588calls/max目的pitch33570816B；低pitch16384预拆回66线性、下降页序不排序，重复/越界拒绝。检查禁止CDLL并确认无Torch import，原D2H前缀与新增方向函数逆关系精确；未构造Tensor/PreparedRestore/Bridge，未编译SDK/执行设备，因此不是H2D字节、completion/失败或收益证明。README6dc0637789508ae6765e002f43baf2193881ac716b6a313f3c00e728de540a21保接口与后继最短风险；已请framework只读互审新方向，当前VERIFY0 pair不混入。

当前swap VERIFY0 pair reader仅新增差分静态审通过：0490973主体及最终5c0bd8568928d223dc7720c8419d32482b6bb7a847bdad92be4a3dedc393d986的Windows extended ROOT/HERE/ns ROOT。原finite20共同可比门与c0 FULL段保留，只4项finite换414/422身份/ENV/附证，SAVE用818e纯整数全几何而非仅sum计数，并要求VERIFY0无SAVE回读；同Engine实际Q/GQA与graph计数边界复用，DB/KV失配gain=None。Windows修不改数据门；未运行reader、raw或旧suite，真实一次比较由root/framework负责。

root继而批准独立单层H2D正确性入口CPU准备：tmp/q-gqa-kv-restore-pitch/validate_kv_pitched_restore.py SHA10e5ec18ea1a1ddc125362a9bf21063f59c6a196214a0873a455c1c8ed3d6df9；launch_kv_pitched_restore_gate.py SHAed7331a693719a5db950527812eac3072432d8bc4e6db2da1cd32fcbed6f4862。只042225真实目的1043页/单层，host与GPU view均一页非零offset，新H2D紧接同非0流GPU compact consumer/D2H/真event，先selected全bytes/guards门再完整pool CPU oracle（全部gap/双guard），之后才独立c95f H2D参考；host全源和RNG不变，无性能窗口或旧SAVE/D2H提交。native失败包括0submitted均settle，未settle保global所有资源到原owner清理，不重试。helpera743/cpp4829未改；它们已获team新增方向静态互审无阻断，不是设备PASS。

controller严格复用原3ffe owner，8项SOURCES固定隔离绝对路径/workspace/experiments/minicpm-s2/scripts/kv-pitched-restore-gate，旧HELPERS仍ROOT/scripts；原flock/双idle/SDK身份/g++/child300s/PID/monitor/cleanup/DB/seal不改，无新控制器层。静态receipt gate-static-check.json SHA86e8469b97a102e2afdcd0d481fa2cc9fcaa938c04f085bf14456c08af7ce42d已一次通过syntax/纯stdlib定义导入/--help/素材SHA/controller逆回，含完整本地→remote上传映射；未运行Tensorstub/SDK/设备。controller生成首个CPU命令因LF/CRLF定位在写前失败，修正后才生成最终稿，未动旧原件。team最终只读10e5/ed733无新增阻断已告root；准确率215836仍唯一owner时不能启动，本owner只交可执行队列，待root串行门，无性能或42层事务承诺。

后续社区机制只保留“FIFO异步H2D enqueue＋真实完成依赖”一项，当前不实施/不上新门，并非已测性能否决。2026-10-23网页核[SGLang PR38472](https://github.com/sgl-project/sglang/pull/38472)（9月8日提出、head4a07e45、仍Open）和[当前cache_controller的LayerLoadingEvent/LayerDoneCounter](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/managers/cache_controller.py)：线程交接必须有recorded/enqueue-done代际，未record事件或旧finish query不能当完成；他卡报告不外推本卡。此机制若成立可隐藏传输/CPU提交阻塞，比只减API次数更宽，但不是再次节省192308已归属target的1.587s重算。

本地当前91185协议_wrap_preempt先真SAVEACK才原free，内存满时加线程不能提前释放；_try_restore仍须pending_frames空/placeholder0/完整fresh私有容量，_rpc completedACK后才computed/publish。可保原fence后让H2D pending期间仅运行不触目标页的RUNNING工作、真event后发布，但须新增pending/重入/取消与slot代际，不能仅换copy stream。BI-V150单asyncEngine/16SM与6CPU报值不证明重叠净益，DMA还会争HBM，holding目的页也不增加KV容量；当前无同几何传输临界段与可独立batch预算，故暂不扩线程/逐层协议或单独诊断，先保当前H2D门。[vLLM46014](https://github.com/vllm-project/vllm/issues/46014)的async队列重准入问题另证GPUflush完成与Core消费完成元数据有别，不可削原frame屏障。framework交叉同意此条件保留/当前NO-GO，无新反例；只更新本交接，冻结H2D资产不改、无SSH/设备/新实现。

root回传222047单层门实际PASS/SOf9bf8757，425 VERIFY1 222222在其唯一GPU在途；本owner不复验单层原件。仅reader tmp/q-gqa-kv-restore-pitch/review_restore_verify1.py SHA07a62cd60e4a1e35d7a298ead65f292a56aebffdbbbe3710c834df5123a41614新增静态互审无阻断：2071只替SAVE/FULL提交calls表达式，原FULL c95f verification_copy_calls==42*destination_runs、真实completedACK/字节/0ZERO/serial顺序/runner6项/consumer/host释放及idle均保留。新FULL按本次页号和实际maxpitch经818e/a743纯整数展开linear/pitched/fallback/calls，未硬14/588；425全源由原422 map、f29/352/9f固定接线和单层PASS完整seal附证/实际SO/None单点替换绑定，三个新增restore路径不能覆盖旧源。两组42验证和Q/GQA同Engine真实execute均须本轮原件，不当accuracy/收益。只读取源码/哈希/路径长度，未导入或调用reader/几何/raw/旧suite，唯一实际验收由systems/root负责。

后续VERIFY0薄launcher worker-draft/launch_restore_worker_verify0.sh SHA5c1542d3ed7fdd3a4336294bd891d57b50feaa13b05c7d2b597a397c58971699新增静态审无阻断：fb8b867222b7b1c867e457c4c3f7f72cb6e4dce42ad528f28aa211c8cf7734ed完整425对原422确仅worker+三个restore文件；显式本222222 PASS报告/run/source-map/SOf9bf匹配，exit0/安装不足。固定两源/原control附证，candidate必传本launcher完成baseline，DB before/after/newbefore均complete且三SHA相同才启动、不配库，candidateafter仍须后验。原bc51long/seed/SERVER/VERIFY0/Q绝对ENV/finiteunset/driver唯一owner/PID及sealer接口保留，未运行脚本/旧门/设备。

reader随后仅Windows兼容变更：ba5扩展ROOT/HERE/旧exec ROOT保持深目录可读；root真实尝试遇SQLite URI authority:%3F，d45de2f8d72d79321629b6ddcdcef5d5eaf68bc756745dfed0aa07a37bc6c6bc在唯一原fingerprint调用入口去extended前缀并强制绝对<260后仍调原算法，其余路径保持extended。已只读新增块及实际C盘before181/after180字符静态凭据无阻断；不泛称UNC适用，不删DB指纹/物理SHA或逻辑字段，不是设备错误，也未因此重测GPU。未执行reader/SQLite/旧suite，实际一次重跑仍由root负责。

新VERIFY0 pair入口tmp/q-gqa-kv-restore-pitch/compare_restore_verify0_pair.py SHAb329875577a20e6c98b94827bfbbd702e333ae160e1de5f82f408f40c13d6977仅新增差分静态审通过：原20共同可比门保留，baseline exact值只重命名422；8251/422→fb8/425完整源只worker+三个restore路径。两臂均原c0 SAVE→FULL→DROP真实ACK/字节/0ZERO/runner6项/consumer/host释放且无回读，baseline FULL仍42*连续段，candidate才改sum并调用d45纯整数逐页/maxpitch/fallback几何，不硬14/588/672。SAVE源及FULL目的submitted/transferred字节条件不放松，完整42读回复用已验VERIFY1报告/SOf9bf附证，不能称VERIFY0又读过一次。四端DB仍原0f2 fingerprint及物理/逻辑/表行数，Windows仅d45短路径入口，不删算法；任一KV/DB/来源/环境失配gain=None，描述百分比不当收益。未执行reader/定义组装/raw/DB/旧suite或设备；root串行baseline223056与后续candidate，唯一实际比较由framework/root负责。

下一社区host点只读后NO-GO、不实现：单slab＋42不相交host view可少41次分配，但不减GPU normal42/传输bytes。2026-10-23网页核[SGLang host pool布局](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/memory_pool_host.py)及[PyTorch CachingHostAllocator::allocate](https://github.com/pytorch/pytorch/blob/main/aten/src/ATen/core/CachingHostAllocator.h)，后者有条件PowerOf2Ceil/free-list，不能当actual Corex allocator已确证。[vLLM56410](https://github.com/vllm-project/vllm/issues/56410)是9月11日他机host放大报告而非本卡收益。现有223056/223540 server.log各SAVE行212中memory_before→after_pin实际增加1415471104/1415176192B，payload717717504/718405632B，近42×32MiB；若同舍入成立，单slab理论1GiB相对1.3125GiB可省320MiB host。但快照还跨producer fence，非allocator trace/时延；after_pin仍约10.8GiB host余量，不能转成KV增量或吞吐百分比。三处host alias/完整覆盖资格需另改而时间预算未知，framework交叉亦无反例，team摘要无独立pin阶段时长；不为此开门/伪异步/固定buffer，不重启凑425容量。

root随后选strict decode allocator无状态快返进入CPU判别，本owner转专审2e91/22e/9dd真实闭包而不写竞争helper。FullAttention remove_skipped→0，已有容量的allocate_new_blocks→[]，num_cached>=floor(cache_tokens/16)的cache_blocks立即return；原create_kv_cache_blocks对全空恰返同一self.empty_kv_cache_blocks，必须保该对象身份。新增guard关键已发framework：仅原RUNNING默认reserved_blocks=0/full_sequence_must_fit=False等（否则0新增仍可能因free−reserved负而原None）；hash边界用floor(min(min(computed,maxlen)+q,request.num_tokens)/16)，不能仅computed%16；rid须真实存在owned list与num_cached条目，newcomputed/APC/ext/lookahead/encoder/spec等未知原路。queued允许computed乐观推进但仅证明槽位/hash无操作，不声称GPU完成、不改frame/fence。旧061506 480次/8步累计11.557ms仅历史调用预算，不外推当前wall；当前16SM/GQA及2batch流水可能隐藏CPU，所以先测完整guard净CPU，净不省即停。社区[当前单类型manager](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/single_type_kv_cache_manager.py)已有内部no-op early return但也新增partial-hit CoW等语义，不能整份升级或只凭最新类名宽放；本候选只锁旧actual源码，尚未实审新稿或运行CPU合同/设备。

strict noop allocator 首稿新增闭包只读封口：tmp/next-kv-noop-allocate/biv150_noop_allocate.py SHAfc410a4a02f93694402480a91a4a027ce16e5c6beaf90efc59d141cf0c5de2b3，无当前语义阻断。actual df780 RUNNING525仅传q和lookahead0；computed<max、ceil((computed+1)/16)<=owned、floor(min(computed+1,known)/16)<=cached分别保证原cap一致、predict/allocate无新页、cache无新完整hash，FullAttention remove_skipped恒0，最终保原empty_kv_cache_blocks同对象。owned与cached原条目存在，不能靠defaultdict补造；页/hash、APC/newcomputed/external/reserved/fullseq等未知调用均原路。06b1的prompt_embeds/resumable/structured等guard字段真实存在。422 protocol91185只包scheduler/Core/runner状态，不替换allocator/coordinator/single方法；其restore277的q0+external/delay等必原路，不改queued/frame/fence/SAVE/FULL。作者唯一CPU receipt报告normal/queued同状态及页/hash边界原异常，并有局部Windows含完整guard净省，本owner未重跑；不是实际6CPU/E2E或生产scope证明。生产MiniCPM/normal42/Async scope与安装仍待最薄接线，当前helper默认不安装、不能直接部署；已消息root/framework，不重复基线225044原件或旧scope/设备。
noop 422→423短服务pair reader tmp/next-kv-noop-allocate/compare_service_pair.py SHA0f762687231bead717486a1ce5a158a2b3a4c8afe05e20b1e88cbf1be2901ca9及reader-pins.json SHA099438ee5041fa25f5bc72303d23a3847ff599938dbbfa88aeb2d420aec14753新增静态审无阻断：固定8c0→03e按原AST提取20公共可比门，同KV/四端DB、原bc51 decode4k/64×4096/128与seed、包/6CPU/完整归档源/后态均保留。exact8251422→beb7423仅init/helper，a826/72f及CPU fc410完整前缀/e876附证绑定；FIRST_SELECTED须与Q/GQA同Engine、原Core成功返回、多running且正selected增量，ARMED同Engine唯一、无finite。4K短负载不强要求SAVE/FULL合理，标记不等全覆盖或GPU完成；任一可比项失败gain=null且描述比率不当收益。仅读源码与素材hash，未执行reader/definitions/raw/旧suite；root唯一230741尚在途，终态由其只跑一次。不重审已验422事务，也不因局部CPU计时先认服务收益。
2026-10-23 CPU社区/硬件再筛：本轮没有发现可凭已有预算直接上服务的新KV大项，不重做finite/fullreserve、BQ16、dirty/active-width、slab或假异步。FullAttention原22e只按free页数准入，物理碎片不降低容量、只增加copy段数，现SAVE Cbatch/pitch已处理主要提交；42层packed页布局也不能继承DeepSeek混合模型padding收益。当天核[vLLM官方9月8日AgentX说明](https://vllm.ai/blog/2026-09-08-vllm-agentx)的packed/hybrid优化，本站单组uniform Full42没有其多组/FP4节省前提。[SGLang当前schedule_policy.py](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/managers/schedule_policy.py)有WAITING_PREFIX_REFRESH_INTERVAL=32与AMD-only tile budget，但本站22e首hash miss即break，不能套radix长walk成本；BQ16真实链仅约0.24%局部已保留，不再包装参数策略。原surviving-prefix复用仍只是旧条件项：若实际同逻辑hash/Block/ref证明H页存活，可少H×688128B H2D，不增加free容量；当前422尚无H及独立copy临界预算，不用192308无swap的2944缓存长度替代，也不扩混合cached/fresh事务。

root提出且由framework拥有的compute-order/sampler-order分离，是本轮唯一值得继续CPU核的框架候选：只mixed eager私有执行token/metadata按q1前置，原InputBatch、请求/采样行序保持，末hidden用invP[原logits_indices]取回原N行；不需全M hidden逆拷贝、不改Q/GQA算术。[vLLM当前utils.py](https://github.com/vllm-project/vllm/blob/main/vllm/v1/attention/backends/utils.py)确有reorder_batch_to_split_decodes_and_prefills，本地actual旧utils:637亦已存在，但其InputBatch.swap机制会影响采样顺序，不能直接移植。已与framework交流一次：收益仅来自当前非prefix q1由2D变GQA的差额，须减一次模型入口重排及新增launch；旧173003的759/3000只旧覆盖，旧mapped局部正/服务负都保留。192308恢复七步29decode已全GQA，target的1.587s prefill不可删；不能把总2D60%当新预算。N32 fullstride8192 int32表一份1MiB，GPU gather需约2MiB读写及launch，CPU pack则另含CPU/H2D；必须保私有执行视图，不就地污染下一步self.input_ids/固定graph buffer。最短门应复用原非prefix D29层fixture、slot/KV/bits/RNG与原scale，重排仅按一次模型成本归账，随后有当前coverage/净正才短服务；本owner不写竞争runtime、不先承诺收益。

team正在准备422稳定puredecode8步同钟native诊断，本owner只给已有读点/风险，未另造reader或设备。旧042609的真实GPU graph aggregate与GraphLaunch相关ID、clock_snapshot已由team核到，撤回“工具不支持图”的泛化；192308无graph是mixed窗口，不能代替puredecode判断。第9execute入口stop保第8外部sampler，边界sync清空queue2须舍过渡并标诊断非自然吞吐；graph.end到下一graph.start还含LM-head/sampler/metadata GPU活动，未扣同窗真实GPU活动并集前不能叫CPU供给空泡。若图/clock/8相关ID未齐或shape/reqIDs失稳，记录incomplete而不自动延长/补跑；若GPU持续忙，则不因CPU局部省时继续堆缓存。官方231746仍root唯一owner，本轮仅源码/网页和交接，无SSH/设备/新测试/模型改动。
root授权独占最薄离线reader已落tmp/q-gqa-puredecode-native/read_puredecode_native.py（当前93e310bb5d14897a561e02fa473e0d34570a83a017c3745192d947aa8b38708c），与team固定native-events.jsonl start/stop/incomplete+8行execute/sample schema；CLI --run-dir ID/绝对目录 --output 新JSON。只复用25c已核SQLite schema/event_query/列解析，不重跑算子排行；同pid+correlationId唯一GraphLaunch API→真实GPU graph、latency一致，再用actual ixsys V4.4.0 ns和MONOTONIC clock_snapshot转换CPU端点。phase归属必须被snapshots bracket且在全部已观察offset选择下仍完整位于该CPU作用域，不放宽边界。舍首2步，只分析内侧相邻graph区间；GPU kernel/memcpy/memset/graph并集、host API覆盖及由correlation证实sample作用域发起的GPU活动分别报告。未覆盖绝不叫CPU/GPU idle或可兑现预算，不证明graph内部节点完整；API覆盖不加到GPUbusy。第1/8步缺失/截断令complete=false/unsupported，但仍保内侧有效step的partial唯一关联/间隔与原因，不因此自动要求重跑。只有syntax与--help检查，旧042609仅一次必要schema/各view1–2条样本及metadata版本读取，未运行新reader/旧run完整分析/设备；framework正只读新增关联风险。官方231746仍root唯一owner，部署六件由team独占，本reader不混入任何runtime。
puredecode reader最终冻结93e310bb，framework已核完整SHA并全文只读新增映射/union逻辑无阻断；其未执行reader/SQL/旧run/测试，未改文件。CPU syntax/help边界不冒称真实新结果。完整八步不成立时CLI返回1但仍独占写出内侧partial事实；root据其完整度判断是否够用，不由reader自动要求重跑。已给root最终完整SHA和CLI，本阶段该文件不再增量。
2026-10-23与compute-order不同的新框架候选再筛，结论NO-GO新增实现/设备。新核GC静态堆点已由actual27b Core:230–234在构造末尾freeze_gc_heap处理，runner6f:6434亦只围绕capture临时freeze，不能重复包装为新机制。uniform Full42准入只看free数量，物理碎片不损失池容量；当前422 SAVE已Cbatch/pitched，FULL H2D仍线性，新425恢复pitch正确性已过但容量失配只属净益未定，绝不是性能负例。异步仅加线程而同步RPC/原ACK不变没有重叠；真正pending恢复需额外协议、源/目的与frame fence代际，当前422临界搬运/可独立batch预算缺失，不能由16SM/单copy engine或旧空白时间推出收益。

192308目标独占1.587s重prefill仍是最清楚的框架机会，但422 FULL正是针对这笔工作，不得再重复算作新候选收益；旧输入准备512步等待4.078ms/预处理10.849s亦不支持buffer所有权大改。当前稳定puredecode是否被6CPU供给卡住仍未知，先复用已就绪8步同钟graph诊断；未覆盖不是idle，若可见GPU持续忙就停止更多host缓存小改。算子/参数/框架升级不在本轮方案，不因暂缺新点否定已有swap/425或A+B；未读旧reader完整分析、无新代码/测试/SSH/设备，只向root说明本轮没有可信新增净预算。
2026-10-23限定社区核查（官方GitHub只读，最多三处，无新实现/设备）：没有找到可直接套用的“仅模型内部计算P、末logits用invP取回原采样序、持久InputBatch不变”的现成通用开关。①[vLLM utils.py cc1a6:938–1015](https://github.com/vllm-project/vllm/blob/cc1a6d31353205bf38b6dbecf4ad134ce3b2b678/vllm/v1/attention/backends/utils.py#L938)有decode/short-extend/long-extend/prefill分区，但最终input_batch.swap_states明确改变持久batch；不能再当一个只调threshold即可保原global RNG的机制。②[SGLang schedule_batch.py 5849:3262及3917](https://github.com/sgl-project/sglang/blob/5849ff5337b5e865518c72f5bd45ce79d21a2604/python/sglang/srt/managers/schedule_batch.py#L3262)的mix_with_running是prefill后拼running，merge_batch连sampling_info、req_pool_indices、seq_lens、reqs一起合并，output/cache位置按同序组织；没有独立保原输出序的自动invP。③[vLLM MRV2 sampler.py cc1a6:134–163、350–358](https://github.com/vllm-project/vllm/blob/cc1a6d31353205bf38b6dbecf4ad134ce3b2b678/vllm/v1/worker/gpu/sample/sampler.py#L134)显式用idx_mapping/expanded_idx_mapping、logits_indices对应的positions/input_ids及per-request seeds组织采样，是最近的映射构件；不能据其keyed RNG推本站旧global随机噪声在重排后等价。接口启示仅为：token级P必须同时对应position/slot/KV行/qstart，返回原N个logit行时仍使用原temperature/penalty/generator/reqID顺序；prompt-logprobs、spec/MM/encoder等未知消费者原路，不能只逆hidden便宽放全部模式。connector所报三文件modified_date分别2026-10-22/10-21/10-17，属于文件元数据而非PR合并日；不升级框架。已向root/framework反馈，原173003覆盖不替当前数据，当前只核机制、不承诺数值/RNG或收益。
root新增当前422在途证据（2026-10-23 00:08:00 UTC，非最终）：同Engine0 Prometheus vllm:num_preemptions_total=11；同一约80ms只读窗口的protocol日志SAVE/RESTORE/PUBLISHED/output均11，last counts saved/restored/published均11、rollbacks0、save_skips0，fast_rejects=restore_skips=3710，single_victim=true、host cap1GiB。这里只转录root在途观察，不独立重读原件；metric发布可能滞后，不能替代终态逐事务/字节/consumer/清理完备验收。当前没有单slot漏SAVE的实证，因此不以“多slot可容纳更多victim”先推进实现或上卡；3710暂态恢复拒绝亦不等于3710次漏保存/事务失败。保原负结果/未知边界，本轮停止新候选排卡，不再查source或资料，官方仍由root唯一owner。
固定231746官方多轮KV薄摘要tmp/q-gqa-kv-official/summarize_official_transactions.py SHAe91e2e02314ffe06dc0749263a655763401543ab7be9cc05c5ae8328a3db759f仅新增逻辑只读互审无阻断。同PID＋完整四元key串RPC/runner/output；SAVE_ACK_FREE/RESTORE_ACK/RESUME_PUBLISHED本身无key，明确仅按当前单slot、前置stage与同prefix推断。DROP真ACK才释放active，后到runner/output按显式旧key匹配，可与新SAVE交错；HostSlot serial全程递增、reserve/release不重置。echo/成功/完成/字节、42层描述/VERIFY0无ZERO无回读、六runnercheck/原output、缺链/重复/逆序/计数/rollback/errors均保留。passed_logged_chain_checks仅覆盖已记录key链，不独立证明全部preempt都SAVE（busy旁路亦不记save_skips），不取代原官方CSV/源/清理或213134 VERIFY1双向字节资格。未执行该摘要/历史数据/SQL/旧suite/SSH/GPU，已回root/framework可冻结；无新候选排卡。
新tmp/q-gqa-mixed-coverage-only仅mode/接线只读互审无阻断：helper8c5b1e2d34d223b068dfd468e2015572871a286cdaf8c19d61ddc63a4e8ae02e相对637550a0只显式冷传mode，install在任何Core/runner绑定前核白名单；mixed_coverage_only不进_shape/ProfilerStart，finish_impl先return不sync/ProfilerStop，不绑定sample_tokens，原execute/metadata/shutdown保原调用和稀疏CPU计数。footer75f43944固定literal，prepare4002824d以8251完整422仅append init/helper成423、cc442/911不变；launcher1739c232直接原bc51 --context-screen 16K/128/32req/c64/seed721201，独立events/Qartifact、VERIFY0/finiteunset，原唯一driver owner/清理，无ixsys/native参数。只核源diff/哈希/静态凭据，不重跑syntax/旧链/套件/SSH/GPU。当前只本地准备，未上传且暂无本包启动授权；SSH外部拒绝不由本任务处理，待root完整002156 raw后决定，不自动排卡。coverage plan仍非forward/确认decode或性能结论。

002156完整窗口已由root执行冻结reader，本文仅解读现成analysis/q-gqa-puredecode-native.json（SHAce2ed28ae7397d8ba5f3f33eac67a774bdcffd2af6b88b72a0d6696c6eeb192f）及analysis/q-gqa-puredecode-mixed-coverage.json（SHAde02083075576149e0bd81f608068fbf7b7326794c378dc021f4979934e0ec62），未重跑reader/SQL/设备。Engine390300、N31/M31，8个真实graph/API唯一相关，complete=true；graph52.320708–52.427100ms，中位52.394716ms，内侧API已提前50.798–51.199ms提交，故不是GPU等Python供给的证据。五个内侧gap依次2.062017/2.102016/2.117931/2.065407/2.085391ms，可见GPU并集1.903497–1.933217ms，其中sample相关0.877497–0.900596ms，另execute内LM-head linear0.929311–0.941984ms；每gap6次H2D合计55.647–56.013us。剩余未覆盖158.205–198.519us，最大单段15.940–29.527us，仅为可见活动未覆盖，不是CPU/GPU idle、可删预算或节点完备性证明；约47ms host EventSynchronize与已排队GPU工作重叠，不能反推host starvation。主要成本在约52.4ms graph本体，当前不支持继续堆host线程/launch缓存大改，也不能把CPU几ms submit直接折成E2E收益。

同一已出mixed摘要末snapshot2109/shutdown：4032个q1计划中outside/not-in-plan各52，仅N29、M259与M2048两步各26，即1.28968254%；这是CPU metadata-plan计数，非确认decode的forward覆盖、非K加权耗时，不能替代128输出官方多波次负载。原compute-order候选只保留待已审coverage-only短门判别，不提前实现或排新候选。root反馈SSH取回后再次连续认证拒绝，128输出短门未启动；保存本地准备态与明确外部阻塞，本owner仅交接收口，不处理连接、追加资料/测试或设备任务。上述精简数字已直接同步root和team_view_final_check，CURRENT/registry由其独占更新。

当前compute-order mixed的active-width页表再判：本轮只读既有SQLite新版cuda_memcpy_data/view与冻结Plan.copy_block_table，不运行旧reader/设备。更正旧“cu_memcpy空表”的证据边界：192308的cu_memcpy虽0行，cuda_memcpy实际有7次N30×8192×4=983040B页表H2D，各38.311–38.746us，合计269.589us；相对该QGQA恢复窗2.855519772s仅0.009441%，只是这项GPU活动即使全删的同窗比例，并非E2E净收益上界。原件experiments/framework/20261022T192308Z-q-gqa-resume-native-diagnostic/native-trace.json，按bytes=983040/correlationId查询；114435旧6f的N2 mixed为3次65536B、5.811–6.000us（不同版本仅说明规模，不移用性能）；002156 puredecode的1015808B稳态约39.7–40.1us，mixed并没有较puredecode约0.073%更大的GPU上传预算。

compute-order当前helper的Plan.copy_block_table仅把一次原full-stride上传的CPU来源换成P staging：np.take原页表全8192列到私有pinned后一次copy_原GPU，不是额外第二次H2D。新可删工作仅CPU P staging对死尾列的读写；当前N17一份557056B，裁列的字节比例不等于6CPU临界成本，尚无其独立耗时/不可隐藏证据。普通strided切片copy_仍有packing/额外GPU copy风险，不能沿用原连续一call成本。故此轮NO-GO新active-width实现/上卡，不另提宽候选；只有已有有价值诊断顺带证实P staging临界，才保留一次“活动已分配列CPU gather＋显式native2D、固定GPU地址/8192stride”的局部门，计入宽度求值/CPU gather/提交成本，并覆盖row reuse、有效列界、padding/capture与原event所有权。已同步root/framework，无新算子、参数、SSH/GPU或GitHub写入。
compute-order pair容量失配只读复核：054306基线KV521936、060425候选521840，两server.log均缺本轮before/after profile、torch/nonTorch/weights/graph原分项，不能把96token=6页=4128768B payload逆推成已证4194304B allocator差。确定可排除的是新增staging直接消耗启动GPU池：冻结helper _cold:77–86的六份tensor均pin_memory=True的CPU缓冲，仅make_plan首次合格mixed时创建；runner唯一plan调用在execute_model:4234，profile_run:6419走_dummy_run，后者不调用plan/_prepare_inputs。新GPU logits_indices N×int32 .to仅实际命中后发生、替原同N减法临时结果，非新增启动常驻GPU buffer。候选log:91先定KV、:133完成engine初始化，:207才FIRST_SELECTED N17/M2048，与静态时序一致。worker本地单文件核仍exact a8de1780…；其595–598预算是requested−weights−torch_peak_increase−nonTorch_increase−graph_applied。两侧同f7af编译cache/7a516 AOT路径不是分项相等证明。

存在与compute-order新增buffer无关的既有启动残差先例：analysis/current-kv-memory-smokes.json的201344/201518，同weights/torch_peak/graph0而before_profile nonTorch已差4194304B，最终521936/521840；更早observed-pair-two-pairs-comparison.json亦分别共同521840/521936。这只证明同类容量离散此前已出现，不回填054306/060425或归因具体allocator；新增Python模块/启动时序的间接影响亦未证。最小可区分缺失证据就是一次原determine返回时既有NoNewCuda observer的before_profile/after_profile、weights/torch_peak/nonTorch/graph原字段（如需再附runner.__dict__中staging是否存在，仅CPU读），不需新模型测试或改SERVER/显存参数；若后续必要服务自然复用再取即可，本轮不另跑smoke。当前same_KV=False、gain=null继续保留，不因已排除直接buffer路径而豁免可比门。无测试/SSH/GPU、旧原件和实现未改。
root授权的Math4混合诊断owner/load已CPU冻结在tmp/compute-order-math4-owner-load/：run_math4_load.py SHA03a0c9027063b239dad66b8d15d87bb867d6e93a1ccf0286882284140d9030e6；prepare_owner.py fab1502cea2751c7b21fb84779f785cf64c062f72e34f56af0d9761a34da3cc8，实际只CPU生成run_math4_gate.py SHA4552fb7f8f92e27af417239488198c01407f0f5474875740d38b5b60decb246a，两切口逆回exact bc51、syntax通过，owner-check c578bd4c…不称运行门。原SERVER/锁/smoke/监控/240s与清理原字节保留；新增CLI仅--math4-capture/--math4-capture-output。只423候选诊断，无baseline臂，背景原621ded脚本32×16K/128/c64/seed721201先启动，按本轮server.log byte边界等待新增完整FIRST_SELECTED，才调用作者冻结capture9e1f6bcf的--output DIR -- eval原6e045参数+limit4；无ready/start、额外HTTP、observer或时序重试。总deadline210s含等待/import，背景先结束记uncovered，四题长生成超时记inconclusive；finally仅终止/等待本次两独立进程组，自有清理最坏约20s，总计约230s，仍小于未改的240s外层期限。

命令/进程/原参数与失败写context-16k/math4-load-summary.json；背景原results在context-16k/background/，EvalScope原work-dir在context-16k/math500-level3/。原batch8/temp1/top_p.95/max32768/timeout3600/ignore-errors/judge未改，官方脚本与105验收器未改；rc0仅两进程完成，原题index0..3须按实际prediction metadata.question_id对原105身份后验，答案前outside/RID/token关联由作者capture与root原件另核，不先称覆盖或准确率通过。team_view_final_check已只读终审03a0/4552/fab150及root部署入口闭包无阻断，未执行代码/旧suite/设备；本owner仅CPU syntax/argv提取/owner生成，不SSH/GPU，runtime文件冻结，README为短接续入口。
104132背景32/0且Math4有4个raw返回、outside题事件0，按root决定收口，不调时序/换题重试。本轮回框架只核一个新机制：partial-prefill无效logit/采样行。原runner（冻结compute-order副本:2243–2255/4471/3687/3728）确为每req保N行logits→采样→discard，不是结果有用；但192308已存分析中整个LM-head仅7call/6.641897ms，采样名称归属全部84call/5.361390ms，合计12.003287ms相对2.855519772s窗仅约0.4204%，这是全阶段可见活动比例而非因果收益上界，可去的只有其中partial行；002156稳定puredecode则无此scope。混合少量dead行并不保证LM-head减少实际GEMM tile，收紧行还新增index/gather/scatter/采样metadata与原N RNG保序成本，不能以被discard推出有净收益。

此次只核一个官方社区对应：[vLLM MRV2 sampler cc1a6:154–199、350–358](https://github.com/vllm-project/vllm/blob/cc1a6d31353205bf38b6dbecf4ad134ce3b2b678/vllm/v1/worker/gpu/sample/sampler.py#L154)，2026-10-23通过GitHub官方源只读验证（文件元数据modified2026-10-17，非合并日）。其亦先sample再按prefill长度算num_sampled/rejected，并采用request/position seeds，不是可直接套在本站global RNG上的跳过机制；不升级框架/换采样算子。现有证据不足支持该行裁剪在保持原随机序列后的净正预算，结论NO-GO新增实现/设备门；没有另泛列方向。本owner只读原源码、现成分析JSON和这一primary链接，未重跑reader/测试、SSH/GPU或写GitHub；已与framework交叉说明并回root。
下一框架方向限定筛选已收口，未形成值得实现/上卡的新候选。检查的“固定2048预算下有界交错多个partial-prefill，以提高后期decode并发”与旧tmp/next-context-prefill-opportunity/PLAN.md及community-interactions第2项重叠，不能重新包装为新方法；原来只是缺真实多prefill状态，未上卡、也非已测负例。新044216现成覆盖有250个mixed计划，其中249个M2048，仅1个M952；已有30步N−Dall>=2，并非没有多prefill能力。q1累计3000只为计划计数、非已确认全部decode/forward，但足以否定“原来大批decode都在空小批执行”的无据假设。framework交叉核到002156亦有249/252个mixed为M2048，双方一致不因高N看起来更高效就实现新调度。

在32请求、每题128输出、noSpec下，最后完成prefill的请求仍需127个后继输出依赖步；把已搭在满M的早期decode搬到尾部不能自动减少这些调用，可能反增图中有效行、延迟结束释放KV。prompt总因果Attention数学量不减，新增细分终界/CPU调度与更早KV峰值均须扣账，不能拿旧1.587s重算或图未覆盖当此策略收益。唯一社区对照本轮已只读核[vLLM当前scheduler config:79–91](https://github.com/vllm-project/vllm/blob/main/vllm/config/scheduler.py#L79)（文件元数据modified2026-10-15，读取2026-10-23）：fair-share floor仅当long_prefill_token_threshold非零才适用，单请求不限cap；这是避免长prefill饿死其它请求的机制，非本站等长16K输入的吞吐实证，不改SERVER/阈值或升级分支。当前缺的是能减少实际总forward/2D工作或证明净重叠的具体提案，不是只缺graph内算子排行，因此不为它单开诊断；以后若有明确框架决策由节点归属判别，再可按最短诊断原则处理。本轮仅源码/现成JSON/一个官方链接，无新实现、reader重跑、SSH/GPU或GitHub写入，已回root收口。
PR15准确率在root设备队列期间，CPU社区窄查仅保一个机制并完成去重：[vLLM官方OffloadingConnector:154–181](https://github.com/vllm-project/vllm/blob/main/vllm/distributed/kv_transfer/kv_connector/v1/offloading_connector.py#L154)按request及已本地computed位置查询新增外部命中，并限制可加载范围；2026-10-23通过官方GitHub只读核源，文件元数据modified2026-10-06，非合并日期。它对应“保留本地真实有效前缀，只从host恢复缺失后缀”，确可少H×688128B/42层GPU搬运，但与analysis/2026-10-22-kv-surviving-prefix-reuse-plan.md完全同点，不算新方法/新收益。旧plan所见source/destination物理ID交集不是H或原bytes未变的证据；当前422仍显式cached0、整R ref1/unhashed/fresh证明，不能直接塞入hashed/shared前缀。ref0命中只减少copy，不减少R前缀所需free下界；省多少时间还缺当前真实H、原页来源/生命周期及copy临界预算。结论仍为条件保留、NO-GO新实现/独立设备门，不将社区成熟接口或旧2944 cached长度当本轮命中，不引入新connector/框架分支。已与framework交叉说明并回root；本轮只读这一官方源和既有计划/协议，没有新算子、调参、旧reader/测试、SSH/GPU或GitHub写入，未另造报告。
112356准确率期间CPU几何判断：002156真实events的start/8步/stop仅N31/M31/reqIDs/时钟，没有seq_lens或逐req生成位置，不能从graph/grid或旧恢复窗口回填精确长度；31个ID均为bench请求，原load固定16384输入/1024输出，原汇总32/0、524288输入/32768输出。以下仅按负载L=16384..17408的保守范围作条件逻辑footprint，不称实际seq_lens测量或HBM流量下界。归档model-config（experiments/framework/20261022T124358Z-last-layer-tail-v2-gate/source/model-config.json）为42层、H2048/MLP6144、16Q/2KV/head128/BF16、vocab130560/不绑embedding。主体QKV+O+MLP dense矩阵共1981808640参数=3963617280B（约3.964GB），一次step跨N行共享，不乘31；两norm/层加末norm仅约348160B。graph外LM-head矩阵另534773760B，不能把其字节计入仅按52.4ms graph时间计算的比值；embedding每步只查所需token行，不把整个embedding矩阵当每步读取。原model_memory_usage约5.101GB是分配账，不等于graph权重读字节。

KV逻辑操作数每seq-token跨42层为2(K/V)×2KV头×128×2B×42=43008B；N31时上述长度范围为21843935232..23209181184B（20.344..21.615GiB）。它已计GQA共享，不能再宣称可省8倍；也不证明每个元素只从DRAM读一次，实际L2共享/物理页共享/重复load均未知。主体权重+norm+KV约25.808..27.173GB除以graph中位52.394716ms，得到492.6..518.6GB/s的“逻辑footprint/活动时间”比值，不是实测带宽或瓶颈证据。实际SDK L2仅16MiB，不能容纳这些GB级工作集；memclock1600000/bus2048按常见DDR约定会得819.2GB/s，但本SDK裸字段没证实有效频率约定，且无本实例实测HBM峰值，不能报带宽利用率、近roofline或套完整64GB板卡规格。

框架含义只限本窗：31个有效q1都需新的42层dense与全有效上下文Attention，历史KV不能因已驻GPU就免去新query的读取，N31→32 padding也不能再当整行GEMM可删工作；不能将这些逻辑必需操作标成重复调度浪费。确能由框架删掉的大块仍是已证重复prefill（192308 target独占1.587s），当前FULL正针对它，不能重算为新点。本窗没有额外preempt/重算或可丢行的证据，因此不从字节估算新开候选，也不宣称当前kernel/框架已最优。最小缺项明确为本窗逐req真实长度及当前实例可靠HBM带宽/DRAM事务证据；本任务不为补齐它们上卡或新增profile。仅原JSON/源码/SDK字段只读及CPU算术，无SSH/GPU、测试或新报告，已回root。

42层重复metadata窄核收口：当前cc442 runner（experiments/framework/20261023T002156Z-q-gqa-puredecode-native-diagnostic-control/plugin-source/vllm_fl/worker/model_runner.py）在1979一次commit_block_table、2199一次compute_slot_mapping；_build_attention_metadata单组build后将同attn_metadata_i对象分给42个layer_name，_get_slot_mappings:4103–4112也分配同一Tensor引用。C3 mixed builder只生成一次suffix_cu/子metadata，forward复用plan，不是每层GPU构建；BF16无quant/cascade额外路径。仅对既有SQLite两名称作只读聚合：192308 slot kernel共7次/63.086us，002156共8次/62.042us，均每step一次而非乘42；002156图内writer不单列，不据缺行称没有writer。192308 reshape_and_cache_kernel_flash为294=42×7次/8.294284ms（约2.85552s窗的0.29%可见活动），其中是各层不同K/V写入，不能整段算可删metadata预算。

每层确有相同页表读取/slot除法和地址算术，但它们在实际GQA1a814:123–178、Attention54c的resolve_seq_and_query_len及writer f182:60–84消费者内部；各层cache基址与KV payload不同，现接口没有预计算offset/fragment入口。框架入口额外生成表而不改消费者不会省这些工作，若要复用须交队友修改算子消费者，当前不新增实现/设备门。页ID逻辑字节相对KV payload很小只能说明字节量，不能排除依赖延迟或当作时间上界；现有轨迹没有独立地址算术/页表依赖耗时证据，不能把整Attention或writer时间归给它。结论NO-GO纯框架metadata复用候选，已与root/framework同步；未重跑reader、旧suite或任何SSH/GPU任务。

原2背景→原四题→事件驱动余30背景的质量诊断，仅CPU闭包核到条件可行而非到达顺序必然覆盖。实际InputBatch源 experiments/source-audits/20261021T170854Z-scheduler-kv-c3/source/vllm/v1/worker/gpu_input_batch.py:310–318先pop_removed填最小空位，否则append；:684–731 condense以最高活行填最小洞。当前P runner tmp/compute-order/files/vllm_fl/worker/model_runner.py:1207–1245先移除finished/unscheduled，:1503–1508先add新req后condense；实际Triton builder继承None reorder阈值，没有另一个自动decode排序。冻结make_plan:156要求scheduled[0]==1，:165要求0<prefix<dall<n。

因此若首背景row0完成同一worker更新恰有新增长prefill，后者直接填0，q0>1即原路；若两背景在余30进入前均已移除/压紧，四Math q1形成完整前缀，新prefill只追加尾部，prefix==dall，至少某Math退出前必零outside。一种可行相位是首洞先被末Math压到row0，第二低位背景仍活；其退出时尾部q>1或同批新prefill填入非0洞，且后面仍有Math q1，才可能形成[q1,prefill,q1…]。首背景客户端完成/两类输出长度差不能保证此相位，还须保原q0与prefix/outside的实际worker标量后验。已将确定约束与反例直接发root/framework；没有改runtime、调时序重试、测试或SSH/GPU。本条仅设计因果审阅，不称四题已覆盖或质量已验证。

事件质量诊断客户端已CPU冻结于tmp/compute-order-math4-event-load/：run_math4_event_load.py f7013086ceb89d2924c9921b8f3898a919c0d694448f30200005de7d0ee4c368；gate_benchmark_requests.py 7cf010d7cf123e51abfc32dc1a51a8c4bee835a413b50bf0747b38f37653214b；warm_capture_evalscope.py f630f5e50248deb772c641c289578e710c9ab630b7f98424d4767064ee51bba1。先让原四题到原generate/generate_async入口且4调用到齐，再启动同一次原vllm bench serve；原get_samples仅一次生成32 payload并旁存全部原对象/身份/SHA，首2原发，尾30在原request_func入口等真实几何文件。原endpoint readycheck保留，不算32样本；不拆CLI、不重置seed、不改payload/题/采样/judge/capture9e1，原generate_async实际AST不调用generate，无4→8双计。四并发预热能否实际成立尚未运行，达不到即inconclusive，不缩小要求或重试。

来源已区分：621ded为run_diagnostic_load.sh，0813为外层官方wrapper；真实installed serve.py b09e85及endpoint5fd4b6是门控入口。root只读取回actual completion/serving.py582b86，完整链为原header→顶层cmpl-header→单prompt子请求cmpl-header-0→Core追加8hex。background-request-ids.json严格只有engine_input_request_ids；完整三层身份与config原bytes SHA写benchmark-original-requests.json。author7f929c信号both-q1/release必须同PID/configSHA，observer-error/uncovered即停止；服务启动前root薄launcher先建全新空CONTROL/events，load不复用旧信号。ENV为原MATH4_DIR加绝对BIV150_COMPUTE_ORDER_MATH4_EVENT_DIR，CLI沿旧load的run-dir/capture/capture-output/seed721201。总210s包含预热/等待/生成，独立两进程组finally清理最坏约20s；原240s owner/SERVER/锁/清理不改，无新controller。root已生成6999477 owner/33f2e7f3 launcher，team受托只审新增联动；本owner只做新syntax/原argv与AST/参数名静态核，未导入框架、运行mock/客户端/SSH/GPU。进程exit0仍仅待报告审阅，原题身份、实际outside早于答案及token关系不能预先认定。

team已完成f701/7cf0/f630三客户端新增窄审无当前阻断，actual readycheck未传request_id→dataclass None、主32显式sample ID均定点核；未执行客户端/设备。root继而要求仅准备回收接口，本owner只读archive/ai/20261022-framework-kv/compute-order-math4-event-load最终稿、tmp/import_math4_longpath.py、seal_framework_screen.py及旧seal_failed_answer_baseline.py，未改工具。新摘要路径RUN/context-16k/math4-event-load-summary.json；原背景结果为RUN/context-16k/background/results/*.json，原EvalScope产物为context-16k/math500-level3/*/predictions/minicpm/math_500_Level 3.jsonl及对应reviews/reports，CONTROL/client-capture存原raw响应，CONTROL/events存信号/原32payload及结局，CONTROL/math4-artifacts存原outside/sample证据。外层root仍回收整个run/control及独立tgz，不只挑结果。

现importer封包/全seal/路径/拒覆盖检查可原样复用，但尾部硬编码104132且assert恰1背景结果不适用于新run/失败；最小展示适配应输出精确glob pattern、实际匹配列表与可选event summary/exit-code。exit1、预热/几何丢失可没有结果/报告，不能使原始证据导入失败，更不能补空结果冒充成功。success sealer严格exit0不应强行接受1；失败只需独立薄适配旧failed-answer入口：锁本轮terminal exit1，去掉旧run/32题/4正确等特定断言，保原fullmap与归档源、双栈端口闭、严格GPUidle、DB后态和实际Attention源码。summary的failed/uncovered/timeout分开保存；exit0也仅两进程完成，非四题覆盖/原judge或准确率PASS。

原success/failed sealer现只验runner/server/日志Engine PID，尚不覆盖新两客户端。建议唯一新增清理附证是读取summary.jobs里实际已启动math4/background PID（start_new_session故PGID=PID），各查/proc状态并扫描这两个PGID的非Z成员，记录后才接受封存；summary returncode及cleanup_errors空只证明清理函数未报错，不替代组存活检查。预热早失败可能只有math4被启动，按实际jobs核，不能硬凑第二PID。若摘要在前置失败未生成，也保原owner exit/log并明确缺少客户端证据，不称完整清理验收。已直接发root最小建议；无工具改动/执行、SSH/GPU或重复审核。

125330 event单臂实际exit1由root回传：背景未发出主32请求，原sample校验即失败，events original_requests/entered均0；仅Math4 ready4且未go，不能称四题/结构质量失败或有效覆盖。独立CPU回收稿已落tmp/compute-order-math4-event-recovery/：seal_math4_event.py SHA8f96cd8b8eab1bc6d913f2528a4b5c234c5d23a95ac2b8c026bedc8ef1163649（原eab7仅5切口）；import_math4_event_longpath.py d6828adb6c3f7358995ec6f3279f71671d0190c6a15d9e787aced0c27bc4822c（原aa00仅根目录多层parents2及尾部展示两切口）。prepare_recovery.py实际仅CPU生成/compile/精确逆回，preparation.json明确未执行两工具或设备；.diff供root审。固定本run terminal0/1并保真实可选summary，缺失只记录未创建/原因未推断；从实际jobs加入原owned PID并扫描PGID==PID所有非Z成员，原source/归档、双栈/68MiB0、Attention和DB后态门不放松。输出仅evidence_sealed_not_quality_pass；importer仍全tgz大小/SHA/全seal集合/路径/拒覆盖原样，结果为可选glob列表和可选summary，不造成功结果。root负责实际执行/封包，本owner没有执行工具、读实际run验证或SSH/GPU。

随后只读actual benchmark源已确定是新增guard误判：experiments/source-audits/20261021T230224Z-benchmark-datasets/source/vllm/benchmarks/datasets/utils.py:67–73（SHA14efee4c…）先从CLI input_len扣tokenizer.num_special_tokens_to_add，再采样；root本次原log[16383,16383]与原CLI16384一致。RandomDataset.generate_token_sequence:760–771以调整后token序列len写SampleRequest.prompt_len，serve get_samples/alignment不把special重新加回这个字段，所以sample.prompt_len==16384不可作为原payload身份条件。MM构造:657–664未传，dataclass:85默认None，alignment的replace亦保该字段；没有实际{}证据，不需宽放MM。向root建议最小只移除错误长度等式，以固定原CLI/source/seed+整原列表/原payload SHA证明同负载，若保类型检查仅正int，不再把16383硬写成通用常量；未修旧冻结稿、未改已部署资产、未调时序或重跑。新修正由root明确批准后另留身份，不覆盖本失败。

root已实际封存并导入125330，489原件+seal共490、DB561/20721三hash相同、五owned PID为退出/僵尸且两客户端组空。按其授权已仅写analysis/compute-order-math4-event-125330.json（SHA374e58f2a0745a784b342031879359d1a3780d669a8af4ff4487a14813034d48）及experiments/registry.csv一行，status=client_validation_failed_before_requests：主背景original_requests=0/entered=0，Math4 ready4但未go，outside/题目质量/性能均未评估，不能计优化负结果。读取的实际summary/outcomes/ready/postflight与DB原manifest仅用于登记，未重跑seal/importer或设备。130351已由root修正该客户端16384→16383另run，原失败部署字节保留，本条不包含新结果；按要求未运行build_team_view、Git提交或发布，待新run结束集中处理。

130351实际原件已由root核531+seal共532，本owner只汇总已保存math4-review-decoded/原报告/postflight：原四题4/4；index0/1/2在输出token0基94真实outside、首完整boxed前，总长1123/744/1651，index3原row0未outside、总733。Engine18855 N5/outside3同原sample，背景32/0；只是三题新路径有限质量信号，不是性能、105题或稳定收益。DB561/20721→565/20919保留，候选可推进独立Draft PR但不自动集成。已写analysis/compute-order-math4-event-130351.json、registry一行，并更新build_team_view中compute-order说明/链接及archive/ai/20261022-framework-kv/compute-order/README.md；125330客户端失败保留，不评价优化。按root授权只生成一次团队视图，结果202登记/199run、243文件，registry_unchanged=true。未提交/发布、未动CURRENT、未重跑reader/原门或设备；root负责本组批量同步。

当前main短对照140324/141159已由root执行reader并登记：445→446仅runner/P helper两路径，32/0，DB565/20919三hash四端相同，但KV521840→521936，33门仅same_KV失败、gain=null；约+6.589830%只记表观变化，不重启凑容量。baseline/candidate launcher、seal/import/reader、root-run-receipts及record_pair和两路径身份材料共34个小文件已归档archive/ai/20261022-framework-kv/current-main-pair/（archive-receipt.json），tmp与原包保留，Git完整tar不重复复制。准备时receipt的未执行状态由root实际回执/analysis/compute-order-current-main-pair.json补足，record_pair已执行不再重跑。

CPU已准备tmp/current-main-combined-official/launch_combined_official.py（871790d6ef6abee9c0d114be2538be3d9883a6db8b496e59c2c5d9d5ab31f166），固定141159源446/tree5c77e68c，沿原79119官方driver/35d唯一owner、0813两负载各4轮/首warmup/原均值与SERVER/DB/清理。相对已审c5ec仅10切口，精确逆回和syntax通过；只有固定142019完整105题valid/pass及已封存同源清理附证才允许派发，未完成必拒。当前准确率仍root owner22265运行，不能预称通过；新官方单臂亦不证明受KV失配干扰的短pair因果或稳定收益。三部署件为launcher及同目录candidate-git-blobs.json/candidate-manifest.json，CLI无参数，root审后独占决定启动。本owner未执行launcher/旧reader/测试、SSH或设备，未改生产源/CURRENT/登记或发布；prepare_assets.py只为本次CPU生成留痕，不在远端重复执行。

447单RID抢占/恢复CPU诊断新增互审收口：tmp/current-main-resume-cpu/biv150_resume_cpu_observer.py 0268b058…与launch_resume_cpu.py 800a4fa8…只读无当前阻断，targettree cd50086e、446→447仅init+observer。实际df780 preempt原request/timestamp、同对象/preemptions+1 epoch、WAITING APC/准入与最多16成功target execute记录保持原call一次；观察异常只禁用/归还instance及class+cached step_fn双identity，不读future或设备、不加sync/profiler。runner183de/P5bc/normalized24a与原bc51长负载/seed/唯一owner不变；CPU issued/execute返回不是GPU完成或可省重算秒数，缺覆盖单次停止。已通知root/作者冻结0268/800a，未执行脚本/旧suite/设备，未改该候选文件。

当前P后C3将q1 GQA与prefill分stream：结论为NO-GO直接实现/性能上卡，暂只保留可判别的并发假设。analysis/source/biv150-resource-query/124857-review.json真实SDK concurrent_kernels=1、16SM/shared128KiB/regs262144/warp64，只证明能力；actual tmp/current-biv150-loader-source/driver.py:321以64*num_warps发block，不能把逻辑warps当线程。CPU只读192308原native-trace.json的cuda_kernel视图得GQA grid(29,2,8)/block64/regs93/srfs64/shared8192，reduce block256/regs22/shared1024；该窗2D是旧Qhoist block512/regs114/shared32768，不能套给当前PR16 normalized。135941原54c实测2D为block512/regs102/shared65536：两个CTA用满shared，1个prefill+1个GQA粗计72KiB/576threads/58176向量regs可容，但最大CTA、SRF池/粒度及当前normalized实际资源未知，不构成occupancy或混驻证明。192308 GQA319.573598ms+reduce2.528606ms=322.102204ms，仅占2.855519772s恢复窗11.28%的理想全隐藏上界，非当前P/normalized或全服务可省预算。两段都已有数百CTA、读取大量不同KV；16MiB L2容不下GB级工作集，重叠可能争用HBM/SME而非省工作，42层还需生产依赖及fork/join/event开销，当前无其净收益证据。C3输出切片独立与prefill不消费GQA partials只是语义可并发前提，不是性能依据；须先有当前资源/可见重叠或内存未饱和的定向证据才重判，不能因两个stream就承诺隐藏322ms。本轮无新query/profile/编译/源码实现/控制器、SSH或GPU。

切API收尾（root明确不再启动新实验）：447 CPU抢占observer及回收均仅准备，未部署/未运行，没有runID。tmp/current-main-resume-cpu-recovery/seal_resume_cpu.py 9f3e42eb…与import_resume_cpu.py 500e9e52…新增只读审已封口：固定446 map+64e8两delta重建cd500/447，原exit0/1、DB/Attention/端口/PID及唯一link/全seal/拒覆盖保持；/proc读取owner PGID/SID成员，非Z或未知失败拒封存、不发信号。FINAL/抢占/APC/16execute原字段独立保存，缺覆盖/无FINAL不伪造成功，causal_chain_reviewed=False/gain=None。importer末端只将半写JSON展示解析失败记parse_error，不改已seal原字节。RUN保持None但严格UTC/后缀，下一API决定是否运行及单点锁ID，不应自动执行旧脚本。

root已回传142019同446完整105题103/105通过（98.0952%、105请求成功无transport/empty、index83一题max_tokens），P0且Normalization实际命中；这是组合完整准确率及其实际覆盖边界，不证明P新分支被105题覆盖。144620原官方任务由root独占启动/回收及阶段同步，本owner的0a485b11 sealer/607d1e21 importer已准备并交接，未运行或另审最终成绩。所有设备/SSH与发布仍由root处理；本owner已停止新研究、实现、测试和队列，仅保留上述CPU静态回执与分stream短结论。
