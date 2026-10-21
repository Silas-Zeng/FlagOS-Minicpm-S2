# framework_innovation 接续记录

任务：实现独立、默认关闭的 BI-V150 MiniCPM5-2B mixed/NONE token M 分桶候选。只做 CPU 源码与文件工作；不 SSH、不启动 GPU、不修改冻结的 080656 source、任何运行 driver 或官方参数。

已读：`AGENTS.md`、`CURRENT_WORK.md`（最新 09:30Z）、`analysis/2026-10-21-mixed-token-bucket-plan.md`、`analysis/2026-10-21-mixed-token-bucket-source-review.md`、`tmp/remote-source/model_runner.py`、已有 `patches/framework/biv150_mixed_decode.py` 与 `biv150_decode_launch_runtime.py`。

当前进度：审查真实 runner 的 execute/determine/preprocess/slot mapping 接点，尚未新增候选代码。目标只在真实 execute 中 mode NONE、非 uniform、M>=256 时将 backbone 行数向上取整到128倍数；真实 Attention M、采样 N、RNG 和 slot -1 语义保持。输入 IDs 的新尾行需额外填合法0，positions沿原逻辑清0。

已修改文件：本接续记录。SHA 在实现完成后填入。

已知风险/未解：actual installed KV writer 尚未有本地 exact hash，先寻找已有 source archive；attention padded output 尾未初始化需要明确只行内隔离；改变 M 会改变 autotune 配置，不承诺 bitwise/accuracy；官方 skip1 可能去掉冷 shape 收益。

验证：尚未运行候选测试或设备验证。已有设计并非已验证性能结果。

下一条操作：读取原 runner 完整方法及配置字段，决定准确 scope/guard，寻找 actual KV writer；然后实现最小独立模块及安装 footer，并交其他 owner 审阅。

## 最新进度：独立初稿与最小 CPU 检查完成

- 已新增 `patches/framework/biv150_mixed_token_bucket.py` 和专用 `patches/framework/mixed_token_bucket_footer.py`，未接入冻结 source、默认补丁或任何运行 driver。仅真实 execute 建立 ContextVar；determine 保持原返回 mode/reqs/uniform/DP 信息，只对 NONE/nonuniform 合法行数替换 descriptor.num_tokens；preprocess 保留原 positions0 与 slot-1，仅额外同流清 input ID 尾。
- root 已只读取回 actual KV writer；已逐行审核 `slot_idx<0` return 位于任何 key/value load/store 之前。持久副本在 `analysis/source/mixed-token-bucket/triton_reshape_and_cache_flash.py`，SHA `f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb`；候选 writer guard 已填。
- runner guard 锁定完整080656前缀 `e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1`；允许的附加 footer 也精确 SHA `21074c950f7ebfec73215f8db746f13b6980779277b084cec6c79e27b706e620`。backend guard `1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605` 加缓存函数 alias 守卫。
- `python -m py_compile` 两文件通过；纯 Python `analysis/source/mixed-token-bucket/check_contract.py` 七项合同通过，含259→384/952→1024与uniform/FULL/容量/eager/out-of-execute fallback。这是 wrapper 合同，不是实际 tensor、KV、RNG、accuracy 或性能证明。
- 负结果：本地 `python -c "import torch"` 因重复 `libiomp5md.dll` OpenMP runtime 退出，未设置不安全绕过；轻量检查使用纯 Python，无 GPU 工作。
- hardware_innovation 已收到初稿并在独立只读审阅。当前继续补实现说明、精确SHA与其审阅反馈。下一条可执行操作：读其反馈，并为 GPU owner 准备最短真实 M259/952 污染尾 gate 的明确接入方式。

## 最终交付（CPU-only；无运行 source/driver 修改）

- 实现：`patches/framework/biv150_mixed_token_bucket.py`，最终SHA `d2620ff750beb3fab97f372d64a1ec0e5550ee133cc6ca33adb8ba3f43de4605`。
- footer：`patches/framework/mixed_token_bucket_footer.py`，SHA `21074c950f7ebfec73215f8db746f13b6980779277b084cec6c79e27b706e620`。
- 完整实现说明：`analysis/2026-10-21-mixed-token-bucket-implementation.md`，SHA `a647af697dd3794f09020a487066c1627f18994dcb596136d357969c353c4713`。
- 最小检查：`analysis/source/mixed-token-bucket/check_contract.py`，SHA `a3a954d89cc68aeb2f7aecd9d6c20210d7351d6a704cff467c11ef54a2b0dfe1`；stdout `analysis/source/mixed-token-bucket/cpu-contract.log`。最终为八项合同通过，补含真实frozen prefix+footer允许、分别扰动即拒绝。py_compile通过；不扩大CPU测试框架。
- 独立hardware审阅已通过86b24旧稿，无设备门阻断。随后唯一代码变化是在已有两个cross_layers guard后加 `not runner.shared_kv_cache_layers`，显式排除runner的跨层KV alias字典；已请其确认最终d262版。scope用语已改prefill/mixed，明确允许纯prefill尾步，不要求存在single-token prefix。
- 不承诺真实行bitwise、KV/RNG/stream/device正确性、暖性能或accuracy；原SQL+C3的103/105不自动继承。默认补丁与当前official run原source完全未变。

下一条可执行操作（唯一GPU owner负责）：在新隔离source副本复制模块、以原始字节append专用footer，先确认expected源与安装marker，再最短真实M259/M952污染tail/下一真实step gate；比较有效hidden/logits/KV/RNG，同N采样形状。当前official run未结束时不可执行设备门。CPU审阅的全部结论在以上文件内，无需依赖子智能体聊天。

## 追加任务：准备无权重最短设备门（仅编写，不执行）

root要求复用 `scripts/remote/validate_mixed_decode.py` 的实际 Builder/Impl/KV，只有M259→384与M952→1024两个case，31天然decode+1prefill；污染padding IDs/positions/out、slot-1，验证同流zero与真实M/KV有效行隔离，并接下一真实decode步。不得加载2B、开服务或profiling。当前正在编写 `scripts/remote/validate_mixed_token_bucket.py`；复用已有lock/preflight/监控与证据helper。全模型MM数值、实际完整runner输入生命周期和accuracy不属于该无权重门的结论；后续最短服务screen仍必需。

## 无权重门脚本交付，未执行GPU

`scripts/remote/validate_mixed_token_bucket.py` 当前SHA `12b4c421325e209aeab5eb14ba27b91250c0404d3289087252c5164b6f2cac4e`，py_compile/--help通过；已发root与hardware快审。没有导入torch或启动设备试跑。仅两case，真实CUDA buffer与actual Builder/Impl/KV/C2+C3，input/position尾毒化后调用候选wrapper清尾，padding QKV/out NaN/slot-1，核有效Attention/整KV逐位与尾输出不写，再在同布局cache接下一32decode。显式记录Harness不是完整runner；无全模型MM/LM-head/采样等价结论。原锁/preflight/GPU采样/原始源码指纹/退出清理均复用既有helper。

实现说明新增脚本章节，其文档SHA因此更新（旧a647只代表加脚本章节之前）；module d262 与footer21074未变。下一条操作：等待root/hardware脚本快审，如无阻断就仅由root在当前official结束释放后上卡；本agent不执行GPU或改当前source。

当前实现说明SHA为 `25a2f89b54d9058621a33e5dde8c99c25d9bf05e4130a5efed816509068cc637`。已逐项核对脚本case布局：初始KV长度1023、64blocks/req，后继1024仍同64blocks，避免门本身错误换布局；新metadata仍32请求与真实M，padding仅扩大Tensor与slot视图。尚无GPU结果，不用源码推断冒充设备通过。

## root 最终审阅与冻结

root完整审读GPU门12b4，确认actual writer grid取slot_mapping.shape[0]，所以后继step的K/V backing大于32但slots只有32是安全访问；未发现阻断。**冻结实现d262与设备门12b4，不再增加测试或实现**。root可准备隔离source，须等当前official结束并真实清理后才上卡；本agent始终未SSH、未GPU、未改冻结080656或运行driver。当前无新实现任务。

最终交付摘要（与发给root的最终回复一致）：独立token bucket模块/专用footer、精确source与scope守卫、8项CPU合同和实施说明均已落盘；无权重M259/952两case门已编写并由root快审，只有语法/--help通过，实际设备结果尚未产生。下一步由root独占设备执行，门通过再原参数最短screen，性能有信号后独立accuracy；不把原103/105或cold-shape收益继承给新候选。

## 新任务：独立review growth admission（以及随后hidden gather）

root委派只读审查 systems_innovation 的 `patches/framework/biv150_growth_admission.py` 与CPU合同 `tests/test_biv150_growth_admission.py`，对照 `analysis/source/growth-admission/` 的actual scheduler/manager/coordinator/block_pool。当前已读候选与测试；接入transformer仍由作者编写，尚不存在其源码文件，不能误记已完成或通过。审查重点future预算、同轮新准入running列表、prefix/free/已allocated页、FCFS break、empty-running兜底、exception cleanup和EngineCore进程安装。不会改作者文件或GPU。

hardware_innovation另请审BF16 hidden gather独立草稿，待本root指定任务完成后读其两文件并把意见落盘。当前两任务都只读review，原bucket d262/gate12b4继续冻结。

## Growth admission 独立细审结果

已审 runtime SHA `9245dd089a310620840a1c056544e66fb2dd0ea24f41ef8f0e4b22721bac7e49`，transformer `b0d5516684e4092dd643836c7bf43ffcd3681d855a32033d6745f13fda0cb709`，tests `da154cbf431257ab3350f4f935b11da5fb32f9965c332f37f986f6f8df0b9122`。独立运行 `python -m unittest tests.test_biv150_growth_admission -v`，7项全过、0.030s。第一次6项后再运行是因为作者新增exact register_model+重复install合同，并非无理由重复。源码与测试均未修改。

- future取prompt+API max_tokens/current+async placeholders/computed最大值并cap model_len，不识别4K/16K或比赛常数；目标全attention预算用实际coordinator/sizing，apply_admission_cap=False。
- actual scheduler waiting成功路径append到self.running、设置RUNNING均发生在下一次allocation前，同轮刚准入者会计入后继future预算；running先前已分配/本步分配/预分配页由原predictor减去。
- ref_cnt==0 prefix hit从free queue被touch占用的费用由原predictor计回，live共享prefix不重复计费；没有touch/修改KV或新增reservation ledger。
- 拒绝只return None，沿原waiting FCFS break、不pop/reorder，active请求未删除；running为空回原路，避免候选空队列自锁。future超过单请求物理cap/unsupported请求回原路，取消/完成/ID复用无陈旧ledger。
- schedule ContextVar finally reset覆盖异常/嵌套；install exact source/原方法binding与双装idempotence保持。非当前scheduler/非waiting/full_sequence不true均走原allocation。
- transformer exact frozen init e043只在register_model函数末尾append显式install(enabled=True)，不改platform register()/runner；原文件EOF确在该函数内，7合同含编译/二次拒绝。通用plugin在model-inspection/worker也可装，但没有schedule即无行为；需要真实FIRST_CHECKED PID匹配EngineCore以证明生效，不能仅INSTALLED。

**未发现阻断最短服务试验的问题**，已向作者/root报告。局限：本地没有actual async_scheduler/core loader源码，仅有AsyncSchedulerFL继承_AsyncScheduler且不override schedule；公开v0.24执行顺序不能冒充actual身份。可通过真实FIRST_CHECKED PID、candidate scope命中及原参数短测确认，不为此铺新框架。默认仍off、无GPU/性能/accuracy结论。

## Hidden-row gather 初审（待作者定稿）

已只读 `patches/framework/biv150_hidden_row_gather.py` 与 `_source.py`。exact e155 transformer只替两处final hidden gather，helper不满足scope返回None恢复原式；non-spec logits_indices原生产点为query_start_loc[1:]-1，CPU lengths+cumsum对query_start_loc与hidden rows的证明足够限定有效index。M/N为runtime参数且do_not_specialize，BF16 kernel纯load/store、2048固定行，无数学或RNG；output新分配不alias，输入contiguous/stride/device/shape守卫一致。

graph输出可按B行但只采原N行，CPU proof应允许sum(lengths)<=hidden rows；copy保持原H2D/forward同流依赖，record_stream用于分配器生命周期而不冒充readiness。broadcast/PP/spec/aux/MM等仍fallback。未发现草稿阻断；建议真卡bitwise门用BF16的int16 bitview核NaN payload/signed-zero，不能torch.equal含NaN浮点tensor冒称bitwise。已向hardware作者发消息；待其最小CPU合同/实际GPU脚本与最终SHA后终审，不运行GPU。

## Growth actual AsyncScheduler 继承确认

root只读取回 `analysis/source/growth-admission/async_scheduler.py`，本owner已读完整并复算SHA `da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884`。actual `AsyncScheduler(Scheduler)`没有schedule override，只override初始化、`_update_after_schedule`与`_update_request_with_output`；结合actual插件 `AsyncSchedulerFL(_AsyncScheduler)`也不override schedule，支持已审base Scheduler.schedule wrapper确会被继承。原“actual async source未本地审”局限已解除；未新增测试。真实FIRST_CHECKED PID/生效scope仍要服务证据。

root将后续screen driver仅新增init+六scheduler/KV source hash留档，SHA `f6b3bfe4de4d373481b711bd74ff1361e1f0253b4f1af68d71d33dc8db987c28`；负载/参数/timeout未变。后续paired baseline/candidate都用新driver，当前officialdriver未改。本owner没有修改driver。

## Hidden-row gather 最终独立审阅

已审 runtime `109905b3d276d6e4ff6cc74a7b97dfe6e8ee31a517b0ac7c4fdb163cc37ad8fd`、transformer `881f2cf209da11842577aab01cca3830e985ad7c9030554156757a5de7e791f2`、GPU gate `scripts/remote/validate_hidden_row_gather.py` SHA `980f83bbf3c7518ab3503728ffafa39936817f5becbb7b1cc4a7eecf43ed6064`。独立py_compile三文件、gate --help通过；独立执行已有 `analysis/source/hidden-row-gather/check_contract.py`（SHA `670636a9aea1642afb289ef868239040c7c6aa4320643b373488104b3cc10547`）通过：exact e155、两挂点可逐byte逆回、fallback、语法、变动拒绝、CPU query ends proof及M/N runtime声明。未新增测试或修改作者代码，未GPU。

实际runner已对照：非spec logits_indices=当前query_start_loc[1:]-1；CPU query_start_loc来自同num_scheduled_tokens_np累和，execute在sample_tokens前不能重入，因此该seam的有效index证明与life-cycle一致。pure decode graph输出B行但只复制N个query末行，索引范围<=hidden rows的契约正确，未把padding采样或改变RNG。纯BF16 load/store没有float归约；stride/device/alignment/fresh output/no-alias守卫足够限定这一个copy操作。current stream沿原forward完成依赖，record_stream仅延长allocator生命周期，不增加/冒充producer readiness。

无权重gate用BF16 int16 view比较所有payload（含NaN/±0/infinity），固定backing地址变M/N观察cache、int32/int64、unsupported fallback、私有重复/乱序/合法负索引与显式跨stream。controller无CUDA导入，独占child+lock、完整source指纹、pre/postflight无进程、300s timeout和owned process-group清理，未见明显设备门阻断。fixture配置不是完整ModelRunnerFL，不能继承103/105或声称整模型速度。

**终审结论：可作为默认关闭的独立候选，由root排队最短设备门；无明显阻断。** 已发作者/root。若Triton cache introspection不可用，这只是动态specialization能力门inconclusive，不能误记数学copy不正确；当前脚本error文本可区分，root须读原error而非只看reject。此项不是要求扩测试或修改代码。

本轮最终review摘要：growth 9245/b0d5/da15的7合同与actualAsync继承链审查完成；hidden gather109905/881f/980f的源码、现有CPU合同和语法/帮助完成。两项都无GPU/性能/准确率结论，全部重大意见已记录在本文件供新API恢复。

hidden gather作者采纳能力门分类建议后，gate最终SHA更新为 `93fd88ae797fe2f377bed7beb244279889881847df0497d7e347ef32e3079dd1`：只补runtime版本/FlagGems metadata指纹，并把cache能力检查延后至其它copy门完成；copy正确但cache不可读为inconclusive_specialization/exit2，真实新增specialization为reject_specialization/exit1。本owner只读核过对应分支，未重复已过CPU检查。runtime109905与transform881f未变。

hardware另独立快审bucket gate12b4的metadata/slot/后继KV布局，无阻断：1023/1024均64blocks、next slotmap长度32限制padded K/V backing只更新前32、真实M和未写输出尾保持。bucket模块d262/门12b4继续冻结，两方意见都未产生GPU结论。

## 新任务：三候选隔离source包装工具

root委派编写 `scripts/remote/prepare_innovation_source.py`，CLI限定exact080656 base→全新ROOT/code目录，variant bucket/growth/hidden-gather，锁base runner/init/旧SQL+C2+C3与已审asset SHA；只复制后改选定挂点，保留manifest。当前开始实现，不运行远端/GPU、不改冻结source或当前official。仅做compile/hash包装核对，复用既有screen launcher，不造新流程或测试框架。

## 三候选包装工具已完成（仅本地）

实现 `scripts/remote/prepare_innovation_source.py`：严格CLI四参数，exact080656目录与5旧源码SHA，候选6项assets按已审SHA，output仅新建ROOT/code直接子目录，资产只读ROOT/scripts。copytree排pycache/pyc/pyo、拒绝其它symlink；复制前后全文件hash核对，只改variant指定挂点并新增对应runtime，原source不动。bucket以原字节append21074 footer，growth/gather只exec固定hash纯bytes transformer（不import候选runtime/vLLM），变化文件和runtime均compile。innovation-source.json含UTC、路径、命令、工具/输入/资产/全output hash、两项变化、prepared_not_executed标记；不复用既有output，失败新目录留诊断而不自动递归删除。

py_compile/--help通过；使用workspace/tmp下已验证绝对范围的新临时root，复制实际090505归档plugin，分别运行三variant的本地packaging/hash检查，每次输入213文件，完整输出只允许对应两文件改变，重复output拒绝。日志 `analysis/source/mixed-token-bucket/prepare-source-check.log`。三项结果：bucket runner `0681b13cf11fcf2d5f707475361cc98e97b1855e0532933f6b0a020fbf55204c`；growth init `d9e2caf40f8d126ec4344b6c98605847f9b4be438eb9961a2eb3bb0f40671ef9`；hidden-gather runner `e68d6886d788a2f56d470fccaee62558d4622545eede2a59fbeb083a5264016e`。本地临时tree已正常清理，无远端/GPU操作；没有构建测试框架。

包装核对后仅加一行目标seam再次hash验证，避免读copy之间source变动；py_compile过，未因此重复全部包装操作。当前待root快审代码，工具不得在当前official活跃时远端执行。下一步root审过后在任务释放时上传现有已审assets+工具，用既有screen launcher，不造另一套运行流程。

包装工具当前精确SHA：`fa61e5e2662cb465937bdc7d24e316382a30176891edeef1f79cbdb67c339983`。最终发root摘要与本交接一致：已准备三独立候选source包装，所有本地结果仅compile/hash，不代表安装、生效、设备正确性、accuracy或吞吐。新增runtime/transformer/门均默认off，未改当前live source/official driver。

## root修复后的真实版本与设备证据（覆盖旧“尚未上卡”状态）

- `20261021T105526Z-mixed-bucket-row-kv-gate`失败于source归档hash，`cases=[]`；导入runtime创建`source/__pycache__`后，iterdir把目录当文件hash报IsADirectoryError。已读本地原results.json确认，发生在任一Attention/KV比较之前，属于留档脚本错误，不是候选正确性负结果。root最小修两处 `if p.is_file()`，新gate SHA `65fcc4de41b62ede39c0ddee67ba44e2a328cb6712e3d23491fdf5061ed63b66`。本owner不竞争修改。
- 经验：source目录经Python import后可自然多出pycache，后续hash必须只取regular files。先前本地仅compile/--help不会覆盖这个运行期目录变化。
- root发现真实080656 base含一个合法MoE内部JSON文件symlink；090505 accuracy archive的copytree已经解引用，因此本地复制归档检查没有覆盖此布局差异。新preparer SHA `0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca`只允许base内部regular-file别名解引用并在manifest记录link/target/hash，继续拒外部和目录link。root报告实际三个隔离source `code/{bucket,growth,hidden-gather}-20261021T105930Z`生成成功，变化hash符合；本owner未远端执行或修改工具。
- 独立复读0ecf实现：`resolve(strict=True)`先解完整链；`is_relative_to(directory.resolve())`必须为True且最终`is_file()`才读hash，外部文件/目录以及内部目录alias均拒绝，dangling/循环链接解析失败也先于copy。非cache链接均检查；资产文件仍禁止任何symlink。copytree默认解引用，copy前后完整bytes hash再次匹配；manifest记原link值、内部resolved相对路径及sha。对于冻结base，未见越界/目录link放行问题；只读审阅，无新测试框架。
- `20261021T105930Z-mixed-bucket-row-kv-gate`已真实两case通过；本owner读取本地results.json：M259→384、M952→1024，各有效Attention finite且逐位相同(maxdiff0)、整KV逐位、out尾仍NaN、后继32decode有效输出与KV逐位、未用out尾未写、padding-only RNG保持。结论仅无权重单层actual Builder/Impl/KV+小Harness；不证明完整runner H2D、全模型MM/hidden/logits/真实sampling/accuracy或性能。

## SQL+C3正式吞吐文档更新

root完成 `official/20261021T092944Z-sql-mixed-official` 原8raw/2summary与230源SHA验收；本owner另读本地result.json及原summary核值：4K 355.88s /3683.65 total tok/s；16K 816.48s /2729.07 total tok/s，原脚本四轮丢首、取第2–4均值，官方参数未变。准确率090505仍103/105。

仅更新 `docs/candidate-usage.md` SQL+C3的“official still running”陈旧段：写绝对官方成绩、链接原CSV，保留原13eb matched总体增益待测、default未覆盖和所有新innovation均未进default。不改README/CURRENT。README73–75仍叙述早期official被停止/无完整score，已向root定位供其统一编辑。

## 新任务：growth scope诊断与Attention双流门只读review

root报告growth110747真实服务已有25running但只见EngineCore INSTALLED，没有FIRST_CHECKED；这不是候选生效/收益证据。systems正在准备新隔离诊断模块，在constructor稳定后AST逐_eligible guard JSON及异常、首次WAITING allocation kwargs/stats一次日志；拟--smoke-only最短定位，旧运行source不改。本owner已主动联系作者，只读review调度/RNG/source identity、scope false时诊断可见性与异常清理；不SSH/GPU、不重复旧tests。

hardware另准备当前a129同流串行decode/prefill的双流overlap最短single-layer门；仅共享只读KV、写disjoint output，尚未实现/集成或有收益结论，作者完成后再来独立CPU审阅。原默认与当前source均不改。

## Growth descriptor-once 95578独立审阅

已完整只读 `patches/framework/biv150_growth_descriptor_once.py` SHA `95578df168cb4fbf1df4efa5c879524075a24d0522f78bb7cd1d650b502e1df7`。精确9245 growth文件与5原源hash后解析可信_eligible AST，分setup assignments与29 AND leaf；每条单独捕获异常，保留原_eligible结果和group count。合并growth globals与descriptor bindings并同传eval globals/locals，正确避开all(generator)只见globals导致假NameError的问题（本owner预先指出，作者已处理）。没有从请求/日志/环境接收表达式，没有设备读取或额外_growth_demand。

constructor原init先执行，actual base初始化已设scope字段，再一次JSON/weakref；wrapper幂等、partial安装拒绝、原constructor绑定和growth已安装marker保留。inittransform只接d9e2增长候选的新隔离副本，不改在途source或9245。正常有效descriptor下，仅日志/读stats，原allocation返回与异常保持；无调度、RNG、KV/队列修改。

已发作者/root的两个具体边界：①capture要求constructor eligibleTrue，若scope False则不会输出首次WAITING kwargs；constructor逐guard足以定位scope，但这项日志缺失需如实解释，建议去掉此只读诊断的eligible gate。②payload属性/format读取在原allocate try之前，诊断本身若出意外可阻止原调用；建议diag读取独立try，失败只记DIAGNOSTIC_ERROR后原调用照走。未竞争改文件、未重复旧tests。root已有同稿正常路径无阻断审阅，正决定/等作者最小修正。

最短设备决策（root指示）：待112021结束清理后smoke-only单请求先看constructor；若29guard全true但无waiting allocation日志，原因可仅是单请求无非empty-running waiting场景，下一步最多2并发补诊断，不直接32请求long。此稿只作诊断，不入性能baseline。尚无该诊断设备结果。

descriptor-once最终SHA `4a6eaefa0b40358307f48c586b9be7dc4a801f4b8eeeda752ff2db5275619b99`，本owner完整复读确认审阅意见②已落实：payload读取独立try，出错仅记diagnostic_read_error；原allocate另一个try只调用一次，原返回/异常照旧；stats与emit错误不覆盖原结果/异常；constructor weakref/report均进diagnostic try。意见①由root明确接受：constructor false时不捕alloc，先用逐guard定位，constructor true才必要时2并发。精确source/AST/scope/RNG未新增问题。**最终只读review无阻断，可作新隔离source smoke诊断**，已发root/作者；未新增或重复旧tests、未SSH/GPU，旧source/9245与当前运行保持未动。

## Mixed Attention overlap初稿独立审阅

已完整只读 `patches/framework/biv150_mixed_attention_overlap.py` 与 `scripts/remote/validate_mixed_attention_overlap.py` 初稿，未定SHA，gate EXPECTED_OVERLAP仍None因此不能直接执行。仅single-layer显式对象，不install到服务。锁实际a129/1219/54c/helper/e5文件及C3→base `__wrapped__`绑定，不改原类/源码。

- current先plan.prepare_consumer保证suffix metadata准备完成，ready event在当前流既有KV update/Q/metadata生产后record；side.wait ready，再decode及3D reducer，side.done记录在reducer之后。prefill当前流执行，然后current.wait done，后续O/MLP消费必须排在join之后。
- 对actual unified_attention的use_3d分支另做只读核对：prefill max_query_len>1强制2D，segm ptr仅以out作为未使用占位，IS_3D=False，不写decode的三份3D scratch；decode prefix才写scratch。输入KV两分支只读、输出prefix/suffix disjoint，原cache writer已在外部先执行。
- pending frame在任何split enqueue之前保存ready/done与layer/QKV/cache/output/metadata/plan/子metadata/各GPU存储强引用；按storage去重record_side，done.query才释放，异常后不半途fallback。连续不同Q两call的current join也串联同一scratch复用；producer readiness与allocator lifetime分开处理。
- gate用D29/P2019/16K一个shape，对同C3 serial逐位、有效finite、padding sentinel、整KV/RNG与两不同Q连续主流clone消费；ABBA每组4call，regular event及完整host wall计时，包括record/query/submit/join成本。source hash只取is_file，沿用child独占/lock/pre-postflight清理；不用external event/profiler。

**初稿未见single-layer门明显阻断**，已发hardware/root。须定SHA并填EXPECTED_OVERLAP后终审；尚无GPU结果或硬件实际并发证明。全模型pending强持有/跨层activation内存峰值尚未设计，严禁凭此门直接服务集成或宣称E2E收益；目前只排设备候选研究。无新增tests/SSH/GPU或作者文件修改。

## Overlap最终独立review与接续

最终runtime SHA `93c3124ccab9311cb98f319d9f786f7aae571f9c1d976d1a9f1d623adca378db`，gate SHA `914f7eb3abee25f05af8cb1a7a78eb96ede7b8c88aaf427014e16b3f745ae291`，本owner复读并核SHA，无single-layer设备门阻断。新补actual KV writer f182文件/alias守卫、single GPU count、sync后pending必须0。regular timing事件创建/record/elapsed或非positive/nonfinite只记录event能力错误，完整host wall仍可得；callback或device同步失败不吞，真正reject。source hash两次均过滤is_file，不再受导入pycache目录影响。

hardware作者报告最小CPU packaging合同35244e5c通过，runtime导入不载torch/triton、pycache后hash过滤有效、语法/hash与--help通过；本owner没有重复这些已过检查或搭模拟流框架。**可由root排唯一设备的最短单层门，不能直接服务集成**，已发root/hardware。默认不安装、全模型retention峰值/实际并发/准确率/性能仍未知。

本次root派发两review已结束：growth descriptor-once4a6e可用于隔离smoke定位scope，scope全true时必要只补2并发；overlap93c3/914f单层研究门可排。重大结论与下一步均已落盘，本owner未SSH/GPU/改live source/officialdriver/作者代码或重复旧测试。

## 新任务：growth V2与overlap计时摊销修订独立review

root/作者交办CPU-only review：growth新revision支持actual builtin AsyncScheduler(use_v2=True)，runtime72d6与transforme5ba，原9245不改，不叠旧growth/diag；仅审新一项actual placeholder合同，不重跑老7。另overlap113727实际4call wall约+2.5%而event约慢0.8%，需一次32/64call ABBA排除固定host/Event构造开销；作者只改timing-loops传播与Event构造移wall之前，旧914f原字节保留。本owner开始只读diff与actual证据，不SSH/GPU、不改作者文件。

## Growth V2最终独立审阅

最终runtime `72d6f3822c96be028f6ab3cd818de1da6bafdb38d52a50a12633851717332803`、transformer `e5bad3d863a36d0d24bc3650c513600e23909d2224fb315bb8eb99943f8b0d9a`。已读112603原server JSON：actual `vllm.v1.core.sched.async_scheduler.AsyncScheduler`，use_v2=True是旧9245唯一False guard，其余28项True、setup_errors空。因此此前growth110747不能作生效或性能归因证据；这是新scope修订的直接依据，未靠猜测放宽。

对9245逐diff：future预算、coordinator predictor、free/prefix/已allocated页、WAITING allocation kwargs/返回/FCFS break与ContextVar finally均未改。新增exact builtin Scheduler/AsyncScheduler类型（FL/MTP或未知subclass拒绝）、async实际第6源SHA、async继承/无schedule override和3个原method身份、defer_block_free必须False；use_v2只允许真实bool的True/False，不再全拒True。

actual scheduler1013之后才V2重组new/resumed request payload，此时waiting/running allocations已结束；实际Base/Async _update_after_schedule推进computed与output placeholders，PP1 next=current+1不跳过步。future原式max(prompt+max_tokens,current+placeholders,computed)已覆盖这些量，deferFalse排除异步connector延迟free；不能据此声称更广V2模型/多卡支持。

仅独立运行新增 `tests/test_biv150_growth_admission_v2.py`（SHA `2ceeb15965b43ccb60228b07882776b7c31405ef7e68fedc2711b5a70cf0d2a9`）一项必要合同，0.017s通过：actual Base/Async两步placeholder/computed/cadence、预算、6源SHA、unknown subclass/deferTrue/defaultoff。未重跑旧7、未修改作者文件。transformer只接原e043 init，从080656新隔离source创建，不能叠v1或descriptor。**无短screen阻断**，已发root/systems；仍需真实FIRST_CHECKED/DEFERRED及独立accuracy，旧103/105不继承。

## Overlap计时摊销修订最终审阅

最终gate `ab1cd95e2f0582e1efa1deb1321887a041a88a068c655627360bb6eee4817eba`，旧914原字节副本 `analysis/source/mixed-attention-overlap/validate_mixed_attention_overlap_914f7eb3.py` hash已核仍914。已读113727实际结果：correctness全true、pending0；旧4call wall saved2.497974%，event反向慢约0.77405%，不能把wall小优势当设备重叠收益。

逐diff仅：`--timing-loops choices4/32/64 default4`从CLI传controller manifest→worker argv→worker函数/result→每个ABBA窗口；Event Python对象构造在wall begin前，record/submit/collect/final synchronize仍计时，能力错误不吞实际callback/sync失败。runtime93c/kernel/shape/correctness suite未变；v2计时方法在manifest/result明确标注。

**无一次32/64call ABBA设备复核阻断**，已发hardware/root；无新增测试或重复旧suite。旧914与新ab1窗口不要合并数值或冒称稳定收益，只在新单次同方法serial/overlap内比较。移动Python Event构造不保证去掉底层lazy-first-record初始化，增加loops的目的是摊销固定成本，不是假设收益成立。全模型retention/accuracy/E2E均继续未知。

## 新任务：full-visible causal mask specialization独立review

root授权hardware只实现actual54c的普通2D完整可见prefix省causal-mask，不做w16/sweep；固定BM128/T64/w8/s1、dot/softmax顺序，3D与未知feature保留原路。本owner已协调作者，将只读审runtime/source transform及最短P2019/16K和Q2048/16K门，不SSH/GPU/重复旧tests，不改冻结source。

预先已对实际helpers复读：resolve_seq_and_query_len按虚拟CTA解析local block并在qblock起点>=query_len早退；query_pos=localblock*16+offs_m//8。对有效首query，最早绝对位置为context_len+localblock*16；完整tile只有在(j+1)*64<=该位置+1且完整落seq bounds时，才能对所有有效query免causal mask。partial最后qblock的query_mask0与query_mask1不能因causal满可见推断而不审地去除。C3 suffix重新cu从0开始、query_len2019而cache seq_len仍16K，context应由子metadata自身推导，不能用整mixed total或全局query_start偷代。

源码当前只读，无新候选文件/SHA，尚无该优化GPU结果。历史已测记录主要是BM/T/warp/stage、directCTA和C3 split，未见已完成同类full-visible mask specialization。root补充growthV2已真实EngineCore162561 FIRST_CHECKED，旧scope问题解决；设备始终root唯一owner。

## Full-visible prefix草稿安全审阅

已读runtime/transformer合一 `patches/framework/biv150_prefill_visible_prefix.py`，初稿SHA `148a33ec56494fadd44965469f7cb231edd0970841d83c875dc0b16389c46626`；对actual54c与派生整源 `analysis/source/prefill-visible-prefix/triton_unified_attention_visible_prefix.py`（`a6d3604aaf3896dce150b8ef56253a3d0fa12dd89095740bb1ec99ce975ddaa2`）逐diff。未install任何服务source，候选仅显式create proxy，由门临时换kernel global。

实现较拆两个loop更小：保留一个原range(loop_lo,loop_hi)，仅当j>=full_visible_tiles才构造并使用原mask。full query block与ctx>=0成立时cutoff=min(loop_hi,max(loop_lo,(ctx+local_qblock*16+1)//64))，否则0。QK scale/dot、softcap、online softmax、PV及遍历/数据load地址未改；只把整数mask构造移到原where前。

安全证明：complete_qblock确保first+16<=query_len、ctx=seq_len-query_len>=0，故该block所有128行与固定16Q/2KV/8GQA head均有效；对j<cutoff，tile最高key=(j+1)*64-1<=最早query绝对位置ctx+first，而complete又推出ctx+first<=seq_len-16，因此整个tile仍在sequence内。partial block一律cutoff0沿原mask，不移除其query_mask0；virtualCTA仍先原resolve/early-return，另有localidx/qpos>=0保护。cachedprefix不必对齐64；C3 suffix使用自身seq_len/query_len/cu局部qpos，不把mixed total当ctx。

runtime严格BF16、HEAD128、GQA16/2、BM128/BQ16/T64/block16/w8s1、2D1segment、普通causal；MM/window/chunk/alibi/QQbias/sinks/FP8/TD等回原对象，3D仍经原C2。kernel端重复static_assert限制；输出与read storage alias拒绝，真实seq/cu/table的dtype/shape/device/stride守卫存在。强source/alias/C2 proxy身份与精确transform anchors保留。

**草稿无mask安全阻断**，已发root/hardware；这仍非Triton JIT或GPU bitwise证据。等最短actual P2019/16K与Q2048/16K门/最终SHA审阅，只有正信号才考虑服务；未增加旧tests或CPU模型框架。

额外数学边界已告hardware：不能把“每qblock仅1个masked tile”推广到所有cachedprefix。P2019/16K的ctx14365，local block2首query abs14397(mod64=61)，16query跨KV tile边界，cutoff224而loop_hi226，需要2个masked tile。当前动态cutoff实现正确保留两者，非代码缺陷；P2019门正好覆盖此边界。Q2048/16K ctx14336对齐下的一tile统计只适用该shape，不是通用安全假设。

## Full-visible prefix最短门最终review

最终policy `148a33ec56494fadd44965469f7cb231edd0970841d83c875dc0b16389c46626`、派生整源 `a6d3604aaf3896dce150b8ef56253a3d0fa12dd89095740bb1ec99ce975ddaa2`未变；完整审并复算 `scripts/remote/validate_prefill_visible_prefix.py` SHA `c1a0122042209081977a95afaeed9a9a254bc714440d5c9105e4342f72ed52f6`。两case为actual Builder/Impl/C2/C3 D29/P2019/KV16K与纯Q2048/KV16K；前者验证实际suffix2019/cu2。原proxy与candidate同metadata/QKV逐位比较、有效finite、out tail哨兵、整KV不变、RNG不变；2D selection分别1/1、3D原C2 fallback分别1/0，避免空测。

随机physical table用randperm每页唯一后，只把P的前16旧page指向D0同页；所有新token位置D0=16383、P>=14365都超过共享prefix位置255，其他rows新页仍唯一。slots按同一pages映射生成，未clobber共享旧KV；末3slot=-1与K/V/Q NaN tail，actual writer f182先负slot返回。KV快照在真实writer后取，证明attention只读；writer负slot本身已有前105930实测，不重复铺套。

只保留P2019一次32calls ABBA，第一caseq/k/v/cache/metadata强引用用于timing，第二case构造不覆盖其cu/table存储。四对timing Events全部提前record/sync后重用，避免首次record惰性初始化；计时记录record/提交/最终sync，global选择在窗口外，finally恢复原kernel proxy。原单for遍历/dot/softmax/读地址仍固定，3D保持原C2，controller独占child/lock/source文件hash/300s超时和组清理沿已审路径。

**最终CPU review无最短设备门阻断**，已发hardware/root，可由唯一GPU owner排队执行。作者报告最小CPU source/非kernelAST/FP表达式/边界算术合同9710528f已过，本owner不重跑或建立模拟框架。没有该候选GPU/服务/accuracy/收益结论，只有正单层信号才进入独立服务筛选；当前冻结source/default未改。本owner未SSH/GPU/改作者文件或重复旧tests。

**最后定稿覆盖前述148a/c1a：policy为 `87c6a31075939c551402d7007b491546a215584a58ec82caddc08fc7249998d6`，gate为 `d3dbf65a9a711360c92ca7c6a01a4ec23046926ee753cd37f836ad33a3bf1996`，generated a6d不变。** 作者仅收窄3项layout guards：q/out row stride>=2048，K/V尾stride=(256,128,1)且block stride>=4096（actual interleaved8192仍过），table row stride>=columns；这些保证行/page不重叠并排未知布局，不改kernel/math。gate唯一改policy pin字符串。本owner只读核新guards/SHA，未重跑旧检查；最短设备门无新增阻断，上传须用87c6/d3db而非历史148a/c1a。

## Original13eb依赖恢复helper独立只读review

systems请求最小事务/inspect边界审阅，已全文读 `scripts/remote/prepare_original_attention.py` 并核SHA `8b3337e06e4dc083b5f99cafd785c6d5a49b64c86a10d721d47c76c304c8eda6`。默认inspect仅读三个输入、可信AST literal反变换和stdout JSON，不导入Torch/Triton/vLLM，不建目录/锁或调用ixsmi。exact retained attention54c/runtimea0c、独立original bab2以及41176字节逐byte比较共同守卫，不能接受近似或重复恢复状态。

apply只允许Linux精确installed regular source；同一framework-device.lock非阻塞独占后核IPv4/IPv6 9031、单卡<=68MiB/0%与空process表。record resolve后限定ROOT/dependency-restores内新目录，写三份原始输入并fsync/读回相等；备份后重新idle/source身份检查，再同目录临时文件保owner/mode、fsync与bytes核对后os.replace，随后核installed原始bytes和postflight。失败不盲目回滚，manifest标failed；没有缓存/SQLite/pycache改动。未见此固定源码/协作锁边界的恢复阻断。

这里只审辅助代码，未运行apply/SSH/GPU，未重跑作者已过CLI/compile或增加suite。锁只覆盖依赖准备，**必须释放后由未改official driver重新取得锁**；不得在锁内嵌套启动driver。source恢复也不等于baseline已成立：后继source须确为original13eb、不导入retained a0c（否则会再次改写attention），正式driver的实际archive/启动后installed SHA须再次是bab2；在途root设备工作不受本review授权影响。下一可执行操作由root待当前job清理后决定，仅准备/inspect或空闲恢复，随后核真实baseline archive与源身份。本次结论同步systems/root，作者文件未改。

## 新任务：SQL+C3候选从original13eb一步复建的完整补丁

root授权本地CPU-only artifact包装：在新tmp scratch中用已存在pristine13eb本地Git对象/归档、retained performance.patch与联合delta4b3e复建exact080656，独立输出 `patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch`，不覆盖default或旧delta、不commit/push、不改GitHub reference、不SSH/GPU/远端import。当前root唯一设备为official122607 original13eb baseline runner166637，installed attention已恢复bab2；包装不能触发任何retained运行时。

开始仅查本地输入身份：`tmp/src/vllm-plugin-FL`、既有 `tmp/patch-check/sql-mixed-decode-20261021T085307000737Z`、`tmp/080656-evidence.tgz`及正式092944归档。先证实13eb Git tree与080656全部plugin files；内部symlink必须保留Git原语义，不能因Windows copy解引用产生无关JSON diff。身份不能证实则停在精确需求并联系root。下一步：只读Git rev/tree与archive manifest，随后新scratch应用两补丁、完整hash/模式对照再产full diff。

## SQL+C3完整补丁已复建，等待独立包装回执

已交付 `patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch`，SHA **`4aba147aa0bd3ec8dd1c12b6ae94bf39537a4cbad449e68e2fcdbfbdc0f8def6`**，43396 bytes；普通git apply格式，从原13eb一步应用，只9个预期Python文件/988行新增。完整diff已保存，default performance仍6e8d、jointdelta仍4b3e，旧文件均未改。未加入任何未选创新或更换官方脚本/参数，未commit/push/修改只读reference，未SSH/GPU/框架import。

本地Git reference HEAD与13eb commit object精确确认；base tree `649161e62191e81a4b367e0e19dc37e32e745099`。080656 screen原件不含完整plugin tree，仅核心SHA，不能虚称直接拥有该时刻全部源码archive。故采用source_dir明确仍为原code/sql-mixed-20261021T080656Z的092944官方完整归档，全部212个repo文件逐byte+SHA一致，并另外核原080656全部六个plugin核心SHA。base-revision.txt归档元数据另核d60，非原Git源码，不入完整patch。

MoE别名仍是原Git120000/link target，link blob SHA c978f595…；按指向target的JSON bytes对照归档copytree解引用副本，不产生无关JSON diff。新scratch `tmp/patch-check/sql-mixed-full-20261021T124036892175Z`，stacked用原6e8+4b3e复建；另一fresh clone一步apply完整patch，全部index blobs/modes和candidate tree **`5c14cfb8d3a452e97a67758873bf18039e1bf989`**相同，reverse apply精确回原base tree，变更Python仅compile。全流程3.57s，本地CPU无新设备/大tests。

持久复建工具 `analysis/source/sql-mixed-full/rebuild_full_patch.py` SHA `7b0acbcd3c7805342f69b85d2222a27a3c6db372f97c633a4ad9cc84e2068349`；全部逐文件SHA/模式/命令 `analysis/source/sql-mixed-full/rebuild-manifest.json` SHA `911a1b08913f6d3603182c7592449fb0254b4562476fa022bcb364fa1aa58dbe`；简短说明 `analysis/2026-10-21-sql-mixed-full-package.md` SHA `b7c910ac4c050e03cc37f55ff22c01b14a86d177964bef070190a9c87b90c83e`。可用 `python analysis/source/sql-mixed-full/rebuild_full_patch.py --verify-existing` 在另一新tmp scratch重复CPU包装检查，既有patch/报告不会覆盖。

已发root与hardware做独立包装快审；尚等回执。本包装是已103/105准确率及092944两档绝对official的fallback可复现交付，**不代表原13eb总体增益已通过**，不覆盖default。下一步仅等cross-review/修具体问题，不加新suite；当前original13eb official122607仍root独占，严禁任何retained远端import或设备操作。

## SQL+C3完整补丁独立包装审阅通过，任务完成

hardware已实际独立执行一次 `--verify-existing`，exit0/3.69s，新scratch `tmp/patch-check/sql-mixed-full-20261021T124556037704Z`；full4aba完整bytes deterministic、212归档repo文件+080656六核心、one-step/stacked全index blobs/modes/tree5c14cfb8、reverse回649161e6均通过。独立numstat为9Python文件/988新增/0删除，无JSON/config/symlink diff，MoE120000/linkblob c978f595与base一致。default6e8和joint4b3e仍原SHA，无新创新。其回执已在hardware handoff/root，未修改本owner作者文件、无SSH/GPU/远端import。

root确认full4aba视为**CPU包装审阅通过**并要求收尾、不做新实现；复现说明已补独立回执，最终 `analysis/2026-10-21-sql-mixed-full-package.md` SHA改为 **`195f71e96f0ba5a7b61743e61e59e2fc7f7a560f8cb7433d69762b7193597a21`**，覆盖前述b7c910初稿doc hash。patch4aba、工具7b0a、canonical manifest911a均未变。

最终可交付的完整候选patch与source复建/回滚证据已齐，不覆盖原default，仍不代表总体性能通过，不上传/commit/push。当前设备依然root original13eb official独占，root将核实其进度/完整结果后再决定总体比较与团队GitHub交付时机。本owner本轮结束新实现；下一API从本节、full-package说明及hardware独立回执接续，不能把包装CPU通过当作新accuracy或总体加速成绩。

## 新研究任务：冻结SQL+C3后的剩余host重复工作

root再次授权仅本地CPU源码/原件研究，不接触original official122607设备、不SSH/远端import/GPU、不改冻结source/default。目标找一个未重复验证、可能明显降剩余框架开销的具体host/cache执行路径；tokenbucket/growth/gather/overlap不重做，不泛提CUDA graph。当前先复读host-gap、SQL后收益基数、系统/内存/图/shape历史负结果和actual SQL+C3执行源码；只有证据支持才提一条最短可否定验证，没有大收益证据也如实记录。

已读 `analysis/2026-10-21-{decode-gap-framework,next-framework-research,memory-lifecycle-feasibility,innovation-systems,large-gain-framework,hidden-view-plan}.md`、candidate-matrix、官方092944归档SQL runtime/ad84和C3/a129、actual SQL module6dc1及 `tmp/remote-source/decode-gap/libentry.py`。旧061506的13.4s SQL profile是修复前窗口，不得挪作SQL后可省预算；已有async/decode图/piecewise编译/共享pool/模型融合也不能重新命名为新创新。下一步精确追 warm LibTuner/生成wrapper缓存和runner CPU元数据的重复路径，并对照现有负结果后收敛。

研究中途纠偏：重新看到SQL新建pool[name]与读取short_name不一致后，曾先发root称“此前未提”；完整rg反查发现hardware旧 `innovation-hardware.md:55` 与handoff:20已有记录，已立即纠正root，不能作为本轮新发现。LibEntry热命中绕过LibTuner/SQL、旧profile172次LibEntry仅12次进LibTuner也已独立核实，故既有“single SQL get”/正缓存/绑定计划均不包装成新大收益。新读queue全部既有实测负结果，含block/batch/prefix/sampler、bucket/gather/growth/overlap/prefix-mask，旧结论保留。

本轮唯一新具体挂点收敛到C3 mixed eager frontend：a129 forward221–225先Q/K/V/out共8个slice，再调用两次actual1219 backend.forward；每次又在604 unbind产生2个KVviews、623–624 expand两scale、643/646再sliceQ/out。故split layer总12个slice+2次unbind(4views)+4expand=约20个view对象，42层约840对象/step。actual backend566起明确警告piecewise eager下view/slice CPU开销，但它不是本项目SQL后占比实测。

拟议最小折叠只一次公共decoder准备、4个Q/out子视图、1次KV unbind，保留两个子批原scale.expand以保证scale pointer/dtype/descriptor与编译specialization完全原样；去掉4个未消费的K/V子片、4个backend重复Q/out子片、一次重复unbind(2views)，可少10个view对象/层。仍按原decode→prefill同流调用同一个已审unified_attention，不改C2/tiles/FP/KVupdate/RNG，不跨step缓存views、不改builder/plan。风险/边界已先发root：长kwargs转发必须逐项等价，不能顺带将未用scale改None或删stream准备；无关键路径预算，最多是具体小候选，暂不实现。下一步写新analysis，附最短“先host前端recorder/submit计时反证，只有成立再actual一层”路径与降级判断。

## 用户停止探索后的最终收尾：C3覆盖审计草案已保存，所有实现冻结

用户要求“停止探索、现有收尾后GitHub协作”，补充“已开始的做完”；root令只把已开工C3 coverage审计/诊断草案交接，未编码就不扩成实现。本owner立即冻结方向，**没有新增runtime、诊断脚本、测试suite或设备任务**。仅新增 `analysis/2026-10-21-framework-research-closeout.md`，SHA **`f25c31d99816befd24f1ffc93edfa3999e9c03c8c9baafdb99c0050e51f16aef`**，并更新本handoff。

准确e155 runner已核：1499新增/恢复请求填较小空位→1505condense→1507_may_reorder_batch→1509refresh。1125–1148只在threshold非None时调用reorderhelper；7025–7043从builders取threshold最小值，无硬编码decode-first。准确1219 Triton builder与C3a129均未显式设threshold/重排。但**安装父类AttentionMetadataBuilder、InputBatch.condense、reorderhelper完整精确源本地缺失**；不能把公开同版默认None或方法名字当actual运行保证，也不能反向声称大量遗漏，按冻结指示不再远端补取。

C3原_prefix实际只拆连续query_len1前缀、受3D阈值/scope限制；服务080656/054922日志只有INSTALLED，没有D/prefix命中数。054501真实Builder/Impl gate及后来D29/P2019是显式synthetic，不能当真实服务coverage。**没有已测natural-prefix覆盖比例，也无剩余host大收益占比证据。** 原SQL13.4s是修复前；LibEntry热命中绕过SQL，pool-key不一致旧hardware已记，不再当新发现。view折叠仅源码量级、root明确保留未实现。

已落的诊断草案（未编码/未运行）：新隔离source exactpin、原method原样、每real execute step仅首目标builder计一次CPU offsets/已存在plan，聚合D1单query请求/Dprefix/Dselected、mixed步数和遗漏，避免42层重复计步；D1不未经阶段证明称全是真实decode。稀疏聚合含step覆盖/完整性、观察失败不影响原返回/异常、不含prompt/token文本、不改RNG/KV。未来若再授权，只考虑原SERVER/同来源4K64req128out一次短诊断，若无明显遗漏直接停止；覆盖量不等于性能。当前所有这些执行步骤都标**未执行**，不因草案新增上卡需求。

本轮结束状态：只读静态审阅完成，无新syntax/code验证需要，无SSH/GPU/远端retained import/冻结candidate/default修改。fallback完整补丁4aba此前CPU包装交叉审通过仍有效，未commit/push/上传；当前original13eb official122607仍root设备独占，root只继续其验收与GitHub交接包。本owner到此终止新实现；下一动作由root处理已授权official/GitHub收尾，不执行本研究草案。未来API可从closeout本文的证据边界/缺失actual源/未执行门直接接续，勿把潜力当收益。

附：完成冻结前已开始的hardware MLP grouping文档交叉审阅，仅只读一次，无新suite。全文读 `analysis/2026-10-21-mlp-cta-grouping-evidence.md` SHA f815344972eec96744476b0e224de6e89551b2aedb0b356e3fd09fd40b4de213、对其evidence875f2662与actual source4c2e/SHA/文件清单。目录确只有evidence.json与original.py，没有runtime/transformer/GPU gate。原PID N-fastest源码与被注释grouping一致；M2048/BM256=>8Mtiles，gateup N12288/BN256=>48Ntiles/grid384/w16warp64=>1024threads，down N2048/BN128=>16Ntiles/grid128/w8=>512threads，均与其旧trace摘要一致。只核摘要一致性，没有重算整个raw trace/DB，不能冒称当前compiled身份关联已证实；文档已明确旧trace与当前DB非同manifest因果证据。

尾组公式以W=8C、g=floor(pid/W)、h=min(8,R-8g)、u=pid-gW，row=8g+(u mod h)、col=floor(u/h)，在合法pid范围每组u=0..hC-1上一一覆盖，末组必须用h与局部u；静态数学审阅未见设计错误。固定全部tile/Kloop/FP/SPLIT_K1、只改整数CTA枚举的草案边界清楚，不能跳bitwise门。**CPU bijection与GPU均未执行**，回执仅“文档交接无阻断”，不是实现/性能/精度通过。已发hardware/root，完成这条既有收尾后停止所有新实现。

## 新收尾审阅：offline archive完整性与Git恢复边界

root仅授权CPU审阅已写 `scripts/build_handoff_archive.py`，不改代码、远端或设备。开始已全文读脚本、gitignore与当前root git status：root仍main，9个tracked modifications、数千untracked工作文件；本owner不commit/push。脚本os.walk不受gitignore影响，可含ignored SQLite/trace/tmp scratch；但全排.git（含nested repos）会丢失历史/refs/index/modes，不能把worktree ZIP说成完整Git恢复。初步发现已发root，正核当前实际inventory/排除与hash/CRC/凭据扫描范围，再写最终精确结论。

### Archive初版实际只读检查与遗漏（root修复中）

本owner审阅脚本SHA `972fb9ed475b6f6b18ffc6d8ad803bc3496eb80cb4bedca9ebe5d2066b48f7f5`；执行一次 `python scripts/build_handoff_archive.py --dry-run` exit0：ready18744files/626034706bytes/17659text扫描，108个目录或链接排除；不建ZIP、不做设备操作。实际inventory包含38个SQLite、3261 scratch文件、14509 tmp文件，未选择output/handoff自身。它按os.walk而非gitignore，raw/ignored确可保存。

确认遗漏：tmp/pdfs14文件被整体跳过，其中有build_proposal.py、build_simple_proposal.py两份源脚本；两个合法内部MoE文件symlink（110149及114713-control/plugin-source/configs/moe/...nvidia.json）仅在exclude保存target，未入ZIP。若称“全部工作”，这些需保留或提供明确恢复语义。ZipFile.open(filename)的原流写法没有保存原mtime/可执行mode；需ZipInfo或恢复metadata补齐。

凭据检查无报警，但范围仅固定文本后缀且<=16MiB，当前13个jsonl、其它extensionless/large/binary以及内嵌压缩包内容不在扫描范围；不是对secret-free的证明，本owner没有发现实际泄露。命名规则拒常见私钥、env、key扩展且不打印命中内容，.git/.codex/.agents排除合理；不能为补历史直接加入.git/config或credential store。归档读到的逐文件SHA+整ZIP SHA、CRC testzip足够验证字节完整性（恢复端再按manifest核SHA）；本owner尚未建ZIP/执行CRC。应先停止本地writers再最终inventory/scan/archive，mtime/size只能检测单文件读期间变化，不是整个工作区原子快照。

### 最小Git恢复依赖已核，不需要所有重复scratch bundle

- 根repo：HEAD `c07eea19d88ce3f7f57d49f7fcb624fb3e3a3489`，tree `4d1d5498c4bf6478fdf5cba413275d10f14aad5b`，symbolic `refs/heads/main`，非shallow，HEAD可达9commits；观察时9tracked unstaged/3935untracked，无staged。ZIP只有最终worktree，不含历史/refs/index。
- `rebuild_full_patch.py`真正硬依赖 `tmp/src/vllm-plugin-FL` 的本地Git对象；HEAD `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`，tree `649161e62191e81a4b367e0e19dc37e32e745099`，symbolic `refs/heads/codex/biv150-framework`，**shallow=true、仅1可达commit，.git/shallow边界为13eb**。commit/tree/blob齐；另3项unstaged修改为init/vendor/platform，重建使用Git base对象而不是这些dirty bytes，ZIP保其最终bytes。完整13eb以前历史原本就不在本地，不应虚称可恢复。

最小恢复清单：根allrefs+HEAD bundle；nested13eb/HEAD对象bundle与shallow-boundary；二者HEAD/tree/symbolic-ref、refs、porcelain-v2 NUL status、staged/unstaged full-index binary diffs、index entries/modes及Git版本。保存于纳入归档的 `recovery/git`，不能放整体排除的output/handoff。bundle不含workingtree/untracked，须与ZIP共同使用；恢复时不要将ZIP最终文件和同一diff重复应用。无需逐一bundle本owner两轮重建的重复scratch，原补丁/manifest能重新生成。

root回执已保存两bundle及metadata，root离线恢复9commit通过；nested普通clone实际失败missing489d22 parent，失败保在offline-restore-first-check.json，印证shallow恢复必须单独处理。root正采用空repo先放shallow边界，再unbundle/read-tree并验证13eb/tree，尚等完成回执/本地读审。本owner不创建bundle、不修改源码。root同时修archive保tmp/pdfs、ZipInfo mode/mtime与合法内部symlink entry+manifest；最终结论等这版只读审阅，当前不能把初版称完整恢复已通过。

### Archive修订与恢复对象终审完成

root修订 `scripts/build_handoff_archive.py` SHA **`2c5195e4d7f13783c3aa0665fbafe0356d79b9c13ec4fdae13ec78baf58cbf40`** 已全文只读并AST parse语法通过：tmp/pdfs不再排除；普通file ZipInfo保存Unix mode/mtime，manifest另存mtime_ns；内部symlink真正入ZIP为link entry且manifest记录target/resolved路径，外部target拒绝；output/handoff整目录仍防自身递归。针对当前实际目录的14文件/两link遗漏均已处理。凭据扫描的后缀/16MiB/压缩包内内容局限仍如上一节，不把dry-run无报警说成全面secret-free保证，没有发现实际凭据。

已独立读取root的 `recovery/git/git-state-manifest.json`、两份offline check JSON与两bundle实体SHA：root bundle **dbfdc6659cde22163c7baa3a3c0c87acf7552f06e039f4b8b4768bc9cc82e721**，plugin-base bundle **924c19e96acec38d12bbdf1e2b574c0d707d65ae3f68a18a536b8d2d2f9937cd**，与manifest相同。初次普通clone失败原件保留不改；`offline-shallow-restore-check.json` 明确空repo放boundary后unbundle/checkout成功、HEAD13eb/tree649161e6、shallowtrue/count1、fsck exit0。本owner额外只读实际 `tmp/plugin-shallow-restore-20261021T145755Z`：rev-parse HEAD/tree与.git/shallow均精确匹配，不仅依赖owner口述。根离线恢复raw记录也确为HEADc07eea/count9/nonshallow。

终审结论：**当前归档逻辑与recovery资料可交付，无需重跑受测候选212文件复建/旧设备门**。补丁/源码没有变，恢复base tree/对象与既有full4aba确定性及212对照证据足够；新任务是归档传输/恢复完整性，不是重新验证优化。root仍需实际生成最终ZIP、CRC与整包SHA，并在恢复端按manifest核文件SHA，本owner没有创建/宣称已验实际ZIP。

已发root的必要恢复说明：普通ZIP extractall不保证重建symlink/Unix权限，应按manifest kind=symlink重建两个相对link并还原文件metadata；nested先写shallow边界再unbundle，不能普通clone失败后忽略；root最终冻结本地writers后刷新Git status/diffs，避免收尾文档晚于状态快照。ZIP含最终worktree+ignored/untracked，bundle保历史/refs，不要二次apply同一最终diff。所有Git/source恢复只在新目录，不改现有GitHub reference、不携.git/config/凭据。

本owner仅更新此handoff，代码/冻结candidate/default未改，无SSH/GPU/新优化。审阅结束，交root最后归档、official验收和GitHub协作安排；不为交接重新运行性能/accuracy或展开探索。

## 新授权收尾：三份说明文档中文化

root转述用户已授权并行远程任务与GitHub私有协作，所有文档中文；性能探索仍冻结。本owner仅翻译 `docs/candidate-usage.md`、`docs/profiling-plan.md`、`docs/baseline-plan.md` 英文叙述，保留命令/路径/哈希/历史数值，区分历史pending与SQL+C3已完成准确率/官方绝对结果；README/AGENTS/CURRENT与发布由root维护，本owner不改。先已读三文及CURRENT顶端14:47Z进度，原版official尚未完整结束；不因翻译改原实验或启动任何任务。baseline旧1%筛选线将明确为历史目标，保留原数字而避免覆盖用户小收益也保留的现行要求；既有smoke/profiling计划也标历史用途，不向在途official追加负载。

三文中文初稿已写；只读保护检查确认candidate原6段bash命令逐字不变（仅注释翻译）、5个完整40/64位哈希集合一致，三文全部原inline技术标识保留、code fence成对。用户消息中断后继续仅文档任务，未恢复性能探索。新明确平台边界已加三文开头：候选/全部本页已测数据仅天数BI-V150，沐曦－曦云C500由队友单独负责，双平台总索引交root README，不移动raw。公开fork按用户选择保留；root维护新private插件仓库FlagOS-S2-vllm-plugin-FL、FlagGems及总仓库FlagOS-S2-Minicpm-throughput，本owner不发布、不改远端或安装命令。

### 三份中文文档最终交付

- `docs/candidate-usage.md` SHA **`14b0152caa71190494db5efeb42f8bd0759bbff99fb0ef095fe8daf6b659d5b1`**：全文叙述中文化，明确仅天数BI-V150；完整4aba一步应用入口保留。两个独立增量“当时待准确率”与后来SQL+C3自身103/105/官方两档已完成分开叙述，SQL-only/SQL+C2不继承联合版结果。原13eb完整对照/团队复现仍以CURRENT/技术报告实时状态为准，不提前报总体收益。原英文锚点通过显式id保留，既有链接不因中文标题失效。
- `docs/profiling-plan.md` SHA **`15b96b15ecdaf3d16030de5be9ca7f589804c96b8f8cd2747ee1bac3cb9d2149`**：中文保留64并发/五迭代、CPU与CUDA/CoreX和所有脚本名/参数，前置历史用途与天数平台边界，不据旧计划新开profiling。
- `docs/baseline-plan.md` SHA **`a8af68efa44d49c48735a7ca315ea0f2cc69250c166ed2fffdb55bcfae02e2af`**：中文保留官方两负载/RUNS4/SKIP1/85%–90%及旧1%表述，将1%明确为已被用户后续指示覆盖的历史筛选目标；当前小收益保留、最短必要验证。旧HTTP smoke步骤标历史，实际是否smoke按冻结driver/manifest，不向在途official补发负载。

最终只读保护检查三文全通过：candidate六段bash实际命令（排注释）逐字不变，五个完整hash集合不变，三文原inline标识全部仍在、fences成对，均明确“天数BI-V150/沐曦－曦云C500”。没有改命令/路径/哈希或实验数值，没有改README/AGENTS/CURRENT/发布文件、runtime/patch/source/raw，没有设备/SSH/远端操作；本轮仅三份授权文档与本handoff。已报告root，交root双平台索引/三个private仓库协作发布，性能探索继续冻结。

## 最新收尾：共用代码库表述审阅与本地private插件副本

用户纠正：仅记录/分析总库按BI-V150与C500分平台，两个private代码库 `FlagOS-S2-vllm-plugin-FL` 与 `FlagGems` 团队共用，不要求平台目录或平台分支。root授权只读审README/AGENTS/团队交接/platforms页，精确改句建议已发root，本owner未编辑这些根代理文件。README18“代码库按平台分支协作”、C500页10“本平台分支”需取消强制；README3/8及C500页5的实现/代码分支用语需区分记录与共用代码。README15/AGENTS7的公开fork待私有化陈述过时，应按最新决定保留公开fork、另用新private协作。`docs/team-handoff.md`不存在，实际审阅 `docs/team-github-handoff.md`，其12:58“仅准备/等待官方后交接”应明确历史、当前允许CPU上传协作与在途测量并行；已测候选段应前置仅BI-V150。BI页无强制代码拆分句。

root随后明确授权本owner独占新目录 `collaboration/FlagOS-S2-vllm-plugin-FL` 本地准备：离线复制已有13eb Git对象，应用完整4aba，中文README并保留README.upstream.md，配置新private origin，提交main；不联网push/建仓，不导入模型，不GPU，除文档外代码精确匹配candidate tree5c14。目标已核不存在；只读source `tmp/plugin-shallow-restore-20261021T145755Z` HEAD13eb/tree649161e6且clean；完整patch仍4aba。Git全局user.name/email已配置，未打印凭据。本地浅源仅有原13eb这一已保存基点，不会伪称包含其缺失父历史；新增commit将以13eb为parent。本owner接着仅写新协作目录与本handoff，root负责API上传。

### 团队共用private插件副本已完成（UTC 2026-10-21T16:17:17）

交付本地目录 **`collaboration/FlagOS-S2-vllm-plugin-FL`**，branch **main**，新增commit **`70d04f38382e900949ddeb34d2ac75aacdc93af4`**，parent精确为原 **13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0**；最终Git tree **`82e37f8f263eeb09563a4790359ec95a0de1ca17`**。origin仅本地配置为 `https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL.git`，没有联系远端/push/建仓，也没有改公开fork或原参考库。

从clean已恢复浅库离线 `clone --local --no-hardlinks --no-checkout`，新目录显式autocrlf=false/symlinks=false/longpaths=true。新main在13eb上应用完整4aba，加入说明前先 `write-tree` 验证精确为 **5c14cfb8d3a452e97a67758873bf18039e1bf989**。保原README字节与mode为README.upstream.md，再加入中文README并本地commit；最终与5c14逐Git tree entry（blob+mode）比较，**只差README.md与README.upstream.md**，其它 **408** entries全部相同；candidate409entries→交付410entries。工作树clean，fsck exit0；浅库可达2commits，13eb之前的父历史原本缺失，没有伪造或宣称完整迁移。

关键SHA全部保留：runner e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1、init e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff、runtime a0c09c51826e0b9e0e5c4f320e68451359db44001d56fd68e1e78de8dda2c9b4、top-p da77c411a88ad4ead072c99cdc4edb52b5bef5b8e5990b9cc8e04db08ed31ca9、SQL ad84c9affe0c3f4b9a4432dd2cbb3861306726f07d53328e129af41c74ea8e8e、C2 e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f、C3 a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42。没有再跑模型/性能/accuracy，只有本地Git包装身份验证。

中文README SHA **abea568f69f1eaef8b1f3de928602974cbf85fbff78a21d6d256720e94510545**，明确两个代码库团队共用、不要求平台目录/固定分支；本文全部实测仅BI-V150，C500无验证结论；包含13eb/4aba/5c14身份、已应用勿叠加、103/105与两档绝对结果、安装时依赖污染限制、总库报告/当前工作/候选说明链接。上游README.upstream.md SHA **6cea2d2844f9edb8fe2b30e2151034ef5b4fef65494199f4c106da6ea86eb2b5**，原文/许可未改。详细本地操作报告 `.git/team-preparation.json` SHA **db5fc40d243aab621a7c1c1bb1a39debafdcd829a8d7a0db034a09d4225a6e78**，本节为持久摘要避免只依赖.git被归档过滤。

已发root的上传关键点：Windows symlinks=false使MoE120000链接在工作树看似普通target文本，**API上传必须读取git ls-tree/git cat-file并保120000 mode**，不能一概100644；代码之外只变两份README。root负责private API上传/团队邀请，未由本owner执行。最终offline归档会排除新副本.git，若需精确保本次新commit历史，root须更新recovery资料加入此repo的bundle/shallow边界或引用最终private对象；旧仅root/base两bundle不包含70d04f。所有新Git操作仅新子目录，根README/AGENTS/平台页仍仅交改句建议，未编辑。性能探索仍冻结，本任务交root接续发布。

## 最终正式报告收尾：原版完整结果已取回

root授权本owner仅更新 docs/technical-report.md、docs/official-comparison.md、docs/candidate-usage.md 及本handoff；不改实验/代码/README/CURRENT、不SSH/GPU。性能探索继续冻结。已读原报告方法结构与现有说明；systems已完成e9dc只读最终比较并回执，接着读取 analysis/2026-10-21-official-final-comparison.json 与独立验收原件后更新。最终叙述仅天数BI-V150，C500由队友在分析库另存；两个私有代码库团队共用，不强制分平台目录/分支。将如实保留实际KV/DB不同、原2–4均值、103/105与无官方总分/非cache-matched边界。root负责PDF与发布。

### 最终中文报告、比较和候选说明已完成并冻结

本轮只编辑授权的三份文档及本handoff，root已读报告并确认数字/边界清楚；按其末次意见移除“PDF生成仍待”旧状态，PDF由root立即生成，不在本文假称已产出。最新用户范围纠正已保留：**全部本候选实测仅天数BI-V150，沐曦－曦云C500由队友在分析库另存；两个private源码库团队共用，不强制平台目录/分支**。root回执两个private源码库已上传核验，精确版本指向 docs/github-collaboration.md；本owner没有联网/push或修改该记录。

最终文件：
- `docs/technical-report.md`，SHA **45bb0e4bfb823897af28a8efafb35a54a9778edeb95ab9529804676693d0f2eb**，11545bytes。标题明确天数BI-V150，保环境/方法/优化机制/短测证据与负结果，补完整原版/候选两档均值、比与TTFT、实际DB/KV差异、结束封存与复现交付边界。
- `docs/official-comparison.md`，SHA **5390a042025d68367b57022524689fa4abe627c54f8e44809057c716546f71dd**，8298bytes。最终完整比较置前，保e9dc只读复算命令/退出语义/身份门，旧pending和12:57Z只标历史，不改smoke原件。
- `docs/candidate-usage.md`，SHA **5fa916426fa0bc9dc55602ba07a80dce575da8341fb8fde01b63512a81331282**，15722bytes。完整4aba一步安装命令与历史独立增量原命令均未改，补5c14 tree、原版完成/分档结果/实际KV和DB/封存边界，保原英文HTML锚点。default补丁未覆盖，所有新探索未混入冻结SQL+C3。

已实读并核对：analysis/2026-10-21-official-final-comparison.json SHA **52f8da4bea6ba7caf4f517edccb9c3c0ecbe85db89f79372b0e5c1c4fc74d832**；双方summary；原版source-review/postflight-full/postflight-process-review/independent-final-review及result。systems完成e9dc真实比较exit0，本owner不重复运行旧门。原2–4轮：4K原1905.46→候3683.65total tok/s，**1.933208x/+93.3208%**，TTFT12310.56→4781.64ms/−61.1582%；16K原861.9866666666667→候2729.0733333333333，**3.166027x/+216.6027%**，TTFT636429.44→185063.65ms/−70.9216%。耗时原687.94/2584.99s、候355.88/816.48s。比例从未再次舍入raw均值计算，不从平均耗时反推。

边界写入三文：KV原521840/候521936（+96）；DB原512/19130→516/19270，候489/18384→501/18789，三种fingerprint均已重算但初始不同；不宣称cache-matched/稳定因果收益，不合成跨档官方总分。准确率仅SQL+C3自身103/105，随机101→103不宣称质量提高。双方CPU配额6/显存32768，同官方协议8raw2summary；原225归档+live全部通过、候230归档SHA通过。

封存真实状态写入：原benchmark 16:14:45.731362Z/driver16:14:50.001906Z完成，benchmark/server返回0、cleanup_errors[]、monitor−15；9031IPv4/6闭、无GPU进程、68MiB0%，server/benchmark/EngineCore退出。runner166637已Z/PPid1未reap，不持设备；首次seal仅末/proc缺席assert失败，失败与独立说明保留不改driver/raw。两server日志shutdown清理剩余1进程警告保留，不写完全无告警。

最短文档静态核对已过：最终JSON SHA/status/cases和source/KV数核实；三文全部本地Markdown目标存在，code fences成对，关键分档数字/比例/边界齐全；全文检索只剩明确历史pending，无当前“原版仍在途”。未修改实验、raw、代码、运行时、补丁、README、CURRENT或GitHub引用，无SSH/GPU/modelimport/新性能验证。下一动作仅root生成PDF/commit/同步实验库与最终归档，本owner三文现在冻结，不再探索或修改。

## 用户重新授权后的框架探索（2026-10-21T16:40Z起）

用户明确“不断探索优化”并要求“小收益也要上卡测也要保留”，覆盖先前性能探索冻结；历史冻结记录保留不删除。root归档写锁现已解除，本owner可写独立analysis/patch/gate与本handoff，但不SSH/GPU、不改stable080656/full4aba/default。root刚取回9份精确安装源码于 experiments/source-audits/20261021T170854Z-scheduler-kv-c3/，归档当时GPU68MiB0%、Attentionbab2，e155/a129未变。本轮先完成actual基类/condense/reorder审计；无覆盖保证才做低侵入C3真实step聚合（plan不冒称forward执行），同时准备CPUmetadata直接复用候选与真实方法最短门。已有async-token整数融合保留小收益上卡队列，不重做已过12case门，不拿修SQL前13.4s当剩余预算。所有新实测仍限天数BI-V150；共用代码库/分析库分平台边界保持。

### 重新探索首个重大结论与coverage冻结（本地CPU）

已逐段读actual c524父类、f137reorderhelper、de1econdense/长度字段、4e4cCpuGpuBuffer，并核1219/e155/a129：父thresholdNone/构造不初始化，Triton不调用_init_reorder，runner最终None，因此helper不执行；condense仅尾填洞，不保证decode-first。helper四区即使启用也不是无条件all-query1前置。真实服务遗漏数量仍未知，D29/P2019不能代替命中分布。actual computed CPU NumPy=cpuTensor.numpy视图，补齐CPUmetadata等价关键源。

新analysis已落 `analysis/2026-10-22-c3-coverage-and-metadata.md`（仍随本轮实现推进更新）；包含actual源SHA、证据边界、coverage最短诊断、CPUmetadata与async-token两候选计划。coverage独立模块 `patches/framework/biv150_c3_coverage.py` **29137c16ceb1d811b6b29b28782e2dcdf3463fce154917b16871d3157f7466b3** 已冻结供root上传；exacte155追加footer生成runner **a39a894a67771e724fc198ea1c3720d1504806cc3d07723a2e3f36fe4d6e6675**。stdlib导入不载torch、compile、精确append逆回、扰动/二次transform拒绝通过；3个CPUoffsetfixture分类/共享layer不重复/多build去重/capture排除通过。systems独立审无阻断。仅observe原metadata返回后的CPUoffsets和plan，不包装forward/不改请求或GPU值/无GPU同步；ctx finally保原返回异常。每64exec+first+atexit cumulative，始终workload_complete=false，plan_is_forward_execution=false。root拟16K32req128out --context-screen真实诊断，必须EngineCore快照metadata_steps>0，计时不是基线，本owner未上卡。

CPUmetadata draftruntime **0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f**、transform **0096cdac2c63544b5e3e62766168dc3df22f6ab63c09231bf9c6e93abaf29835**、变换runner **50493fb68b194ed935650a3a743d2f56696d7379b702f4d7717eecac0325a9de** 已写。exacte155保原计算为fallback，scope nospec/text/单并行/async原event/无未知feature；两个H2D用已有CPUpositions/optimisticseq，保原GPU地址、computed原copy、host镜像、slot/采样路径。systems只读审未发现阻断，特别要求连续换host值+按原event调用/消费测试不要每步强sync掩race。模块导入不载torch、compile/精确反变换/source拒绝已过；真实方法GPU门正准备，尚无GPU正确性或收益。

### CPUmetadata四件冻结、真实coverage回执与重复adapter纠正

systems全文终审runtime0e9615/source0096/gateb124与actual5method/Buffer，未发现执行或生命周期阻断；原event内再写CPU、连续4步无逐步强sync、defaultstream H2D→graphcopy→clone正确，固定GPU地址不换，32call hostwall含event与最终drain，controller/sourceguard/独占child/清理边界明确。最终四件已发root冻结：runtime **0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f**；source **0096cdac2c63544b5e3e62766168dc3df22f6ab63c09231bf9c6e93abaf29835**；变换runner **50493fb68b194ed935650a3a743d2f56696d7379b702f4d7717eecac0325a9de**；gate **b1240720b588dae25d92cc1c173d64c1ea5f6e34fcdcab5dd0156407ebbcb757**。本地7assetSHA/5actualAST抽取/compile/逆回/扰动拒绝/help/no torch-numpy import过；本owner未GPU，root可在现job清理后串行最短门，尚无正确性/性能通过。

root实际coverage run173003已exit0，17:33:27Z fullpost68/0；本owner已实读本地coverage-snapshots.json SHA **f51c9981156d4fcaa1122030e719b8727d9428bc3d370e89a8bccf75d8747554**。最后周期384calls/305metadata/250mixed，Dsingle=Ddecode3000、prefix=planned2241、outside759=25.3%；77padding_or_unsupported单列，无观察错误/多build。它是未完整观察前缀、非forward计数，首1req8tokens来自既有driver smoke，总exec计数不能冒称纯主负载；不改原统计、不作性能基线。初次256回执739/2434只作较早快照，最终正文已用384原件。真实遗漏支持新分区设计，不等于25.3%E2E可省。

本owner另写 `biv150_async_token_update_c3_source.py` SHA123d7f1d34404ae2f7069800de70cbd8f88c490377a97c8aab4daf45b08d013c，证明e155 startswith原446f、_prepare_input_ids全文字节相同SHA7dc35754、ORIGINAL/REPLACEMENT不变、变换f0d0可精确逆回。但root同时已有canonical `biv150_async_token_update_sql_mixed_source.py` **cfd378a494c0ccbb5aece861527cdf59ccd148afbe53ac229a09bb43162bdb6f**，hardware已审、生成同f0d0。现明确本owner123d是重复准备，只保留交接、不作为新候选，统一root cfd版；不再实现或重复12case门。原1bb runtime/e5a旧adapter未改。

root新委派真实请求重排candidate。本owner已定位关键RNG边界：actual swap_states正确搬request/KV/采样参数/generator，但全局随机噪声仍按物理行分配，不能只交换就说每request RNG相同。首版拟strict all_greedy才稳定分区，random/mixed sampler原路，不改温度/参数/采样；actual e155先_may_reorder再refresh再按新req_ids构造scheduled数组，prev_req映射按ID查旧sample rows。接着准备actual swap_states CPU逆序/乱序/async请求映射合同，hardware已预留独立审。没有直接上卡、没有改稳定candidate；当前root唯一GPU为CTA173921。

### greedy路线反证已闭合；mapped Attention只到CPU设计

root取回174453精确bench源（serve b09e85eed6f5f7a9075b40a19fc1dd8e94a1c449665c2c6510f349e0409e77b7、endpoint5fd4b66d9ac6a88a278c2b7d65dcd17b8a9424279859ade14bddb69e342a312d、sampler1a2f18ddc91c89f3744ab5a93624be056bf20b7a8b2e6e13d0236182718a2253），本owner实际读原件：temperature默认None，非None才进extra_body，endpoint无temp默认；official/diagnostic无override，归档modelgeneration temp1/top_p.95。coverage173003 server.log96还明示模型这两个参数覆盖默认，clientNamespace temperatureNone+警告不再默认greedy。因此greedy状态交换仅可能命中driver smoke，不能作为官方吞吐候选。root已明确取消greedy专用GPU队列，本owner未为它继续写runtime/服务补丁/上卡，不改温度让其启用；策略边界存analysis第5节。随机路径仍保request/RNG物理行。

CPUmetadata174115已由root实卡执行19秒exit0，本文作者独立复算10份归档sourceSHA、读results **50b631e28c83ea1861624bc51b2d23222470444ee5ed9bc99790add2ba15b99d**：5形状全部字段/slot/ID/镜像/固定地址true，连续4步换host值+原event+graphconsumer通过、selected75。方法wall0.712748078125→0.65646540625ms，少56.282672us/7.8966%，仅fixture输入准备方法，非E2E。root已进入同来源服务短pair（baseline174402）；本owner没有服务结果，四件源码仍冻结不改。

按root建议，新的真实缺口路线改为Attention内request-index map，设计已写analysis第6节。没有新GPUkernel/runtime/安装器/服务。三种地址严格分离：compact d→map读取request r→cu读取原token t；r仅seq/table，t仅Q/output，d用于三份scratch全部读写（尤其54c :596输出及:608store_scalars、reducer686）。BM16/GQA8的第二无效queryslot继续mask，scratch向量d+query_pos而非改全局query_offset；首版TD/未知feature回退。2D先原resolve/invalidCTAreturn再skip querylen1，map必须含全部single-query唯一一次，避免漏写/双写。外部token/request/sampler/RNG/整批GEMM/KV写不动。一次mapH2D≤256B，42层无Q gather/scatter；若原C3 impl实际选中prefix计划步，源代码三launch→三launch，但原coverage只测plan，不能把248/250当真实launch占比（曾在消息中措辞过强已立即纠正并告root/hardware）。prefix0额外两launch，early-returnCTAs仍有调度/整数成本，收益未知。

新增唯一CPU地址proof `analysis/source/c3-mapped-decode/check_address_contract.py` **4c4fe093f2f7e4b2c38c4025d404ce8931d1cb1c84f4a044c87afbdd89dd4a0c** 已过：锁54c/59d9，11定向+600随机/逆序，2D原virtualCTA覆盖、skip与mapped输出不交不漏、map唯一、compact上界、N256/D64、pure/自然prefix/D65回退。纯整数数学模型，非Triton模拟，不证明FP/stream/compiler/performance。hardware已只读actual地址给同一风险清单，正等最终文档/proof交叉审；没有要求或执行GPU。下一步root/hardware对设计取舍后才决定最小真正kernel实现/门，先别把它计作完成候选或收益。

### root授权下一阶段最小mapped实现（进行中）

root已接受上述direct request-index设计，委派本owner继续独立runtime/54c源码变换/e155元数据安装/短单层gate，hardware交叉审。当前开始实现准备，不做请求重排，不GPU、不改稳定SQL+C3。三个行号/compact scratch/2D skip/真实N对D/C2显式w2s1边界继续硬约束；纯decode/未知feature原路，默认不开。门至少非prefix D、D1尾/中、D64、长KV及后继decode，oracle为原2D覆盖后用同配置原C2 compact3D回填，并保原C3差异说明；地址CPUproof不当GPU正确性，正信号后仍要独立accuracy。此条为开始状态，新的runtime/变换/gate尚未落盘。systems另请求我独立审其KV只观察probe(a4de3a...)，会按owner互审规则仅只读，避免阻塞root已有设备队列。

### mapped 首稿已落盘，尚待真实单层门

当前最新实际状态：已写 `patches/framework/biv150_mapped_decode_source.py` **0433a8de0d1e42962d8c8c1ef671f2937107dfb5ae144447cd5f13df9b10811e**，由实际54c/59d9精确变换生成 `patches/framework/biv150_mapped_attention.py` **67a9830eaa976e79d9d21f5f34ec4bbfe0215d3082d6571d415c1c8f33a85f47**；exacte155仅追加footer生成runner **3566099b2f336f3e7ae768adeca5b0da169748324fec26fc00b150b26b246a73**。运行时初稿 `patches/framework/biv150_mapped_decode.py` **32f40e78afe63e4066e93d966eb8ec24fd9b146dde485e2d32b5483d08048827** 已写，后续仍会收紧guard，不是可提交冻结版。三件syntax通过，runtime纯stdlib导入不加载torch；没有执行GPU或模型导入。hardware已逐挂点只读审source0433，未发现d/r/t、compact scratch、2D skip和launch明显阻断；派生身份与runtime/gate还在收口，不能据此报设备正确性。下一条操作：收紧runtime严格回退与安装顺序，写最短真实Builder/Impl单层门并交互审；稳定SQL+C3/default未改。

systems 的 `biv150_kv_completion_probe.py` **a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6** 已完成本owner只读互审并发回root/作者：original allocate先调用且仅RUNNING返回None观察；get_num_blocks_to_allocate/free只读，不future.done/result/wait；preempt/resume按真实对象epoch，ID重用清理，ctx finally复原；无干预阻断。terminal仅容量假说、processed floor非GPU完成、gap exposure非真实重算量、周期/weakref不完整边界保留；未重跑作者测试、未改其文件。

### mapped runtime/门已齐；独立审阅进行中（最新接续点）

runtime已收紧到 **7bf4e1337b0afe7a425204a4424ff76e05ebd143feed9d00d809daf9c5d61d47**：exact原C3 wrapper codefile/unwrap原build，固定threshold64，原execute_model qualname+filename先校验后安装。source0433/derived67a/runner3566未变。最短设备门 `scripts/remote/validate_mapped_decode.py` 当前 **c2ded9b854608aedb15b6279d5c84195f0a0698b49117d2b05d155216b4e98bd** 已写；四shape/16K/独立C2 oracle、显式2Dskip哨兵、KV writer整cache oracle+负slotNaN、三行FP32误差、D1中间跨stream释放/churn与capture原2D回退、同cache真实append到16385后puredecode。默认不timing；root要求先仅正确门，等CTA服务结束由root唯一owner执行，本owner无GPU。

`analysis/source/c3-mapped-decode/check_source_contract.py` **57d4a866c386c6f2e365c3226c23d4abaacf119be4bfff3048894687063d1266** 实际exit0：精确派生/runnerappend、4种扰动或二次transform拒绝、32份FP表达式AST不变、gate三asset pin、syntax/纯stdlibimport不载torch。之后只加qualname guard与对应pin，待最终manifest统一；不会把这些CPU检查称设备正确性。hardware已审transform/source首稿与runtime大部无明显阻断，当前最终门正在独立只读审。其曾误称base_forward含KV写，已据actual1219纠正并撤回：writer在独立do_kv_cache_update；mapped不减少writer launch。原C3 build未移除，仍保留unused suffix_cu准备开销。依赖路径/下一命令已写analysis第6节，controller复制全部helper进新run/source，不依赖tmp；最终SHA待互审后冻结统一文档和packaging manifest。

两个小收益服务结果已实读systems独立比较JSON **38f3170c5c0b47edac7af285553abc1d29b00b7f5bb02b027fa4e7e4f0ec849a**：async174741对A1 174402（KV521840）TPS+0.7036569%/TTFT−0.8656382%；metadata175049对A2 175441（KV521936）TPS+0.2867234%/TTFT+0.2344306%。各64/0、262144in8192out、CPU6/32GiB、同DB三hash516表19270行、preempt0→0、真实EngineCore FIRST_SELECTED与fullpostidle核验。单次固定顺序小信号保留、未final合并/未accuracy；A1/A2容量不同不跨pair称matched漂移。analysis第7节已留边界。

### mapped 四件已互审冻结，可由root执行最短正确门

hardware已实际核四个最终SHA并全文只读审，未见进入最短correctness设备门阻断；未跑suite/GPU：

- runtime `patches/framework/biv150_mapped_decode.py` **7bf4e1337b0afe7a425204a4424ff76e05ebd143feed9d00d809daf9c5d61d47**。
- exact transform `patches/framework/biv150_mapped_decode_source.py` **0433a8de0d1e42962d8c8c1ef671f2937107dfb5ae144447cd5f13df9b10811e**。
- derived `patches/framework/biv150_mapped_attention.py` **67a9830eaa976e79d9d21f5f34ec4bbfe0215d3082d6571d415c1c8f33a85f47**。
- gate `scripts/remote/validate_mapped_decode.py` **c2ded9b854608aedb15b6279d5c84195f0a0698b49117d2b05d155216b4e98bd**。

最终source合同因新增qualname guard/pin做必要一次短复核exit0，stdout `analysis/source/c3-mapped-decode/source-contract.log` **22c36a73f0b049ce1a6ab206894f53869e46a4adc04d603d84bf46cd62ecf400**；完整候选/helper身份、精确runner产物和独立审阅 `packaging-manifest.json` **82d03c89c583cdf56576f29427ac3d38ea2900297871115ab5998048e66fd38e**。没有重跑旧CPU suite，全部新文件只在独立candidate/analysis/scripts，stable/fullpatch/default不改。无SSH、远端import、GPU或模型权重加载。

可执行下一步已写 [`analysis/2026-10-22-c3-coverage-and-metadata.md`](../../analysis/2026-10-22-c3-coverage-and-metadata.md) 第6节完整bash命令；root等CTA服务结束后唯一owner执行，**不带--timing**。controller将全部5个候选asset和5个既有helper/monitor复制到新run/source，worker只使用这些归档路径与hash锁定installed源码；绝对derived loader+exact transform双核，不依赖tmp。不执行生产runner install，故门FIRST_SELECTED real_execute=0是预期，不能假称真实模型命中；服务后才应另核real_execute=1。设备正确性、后继decode、capture/stream门均尚未执行，任何失败保留；即使通过也只是单层synthetic，整模型误差/accuracy/服务性能仍待。未经root后续授权不混入final。作者本轮交付完毕，代码冻结等root设备反馈。

### mapped 首次设备门编译失败，服务准备暂停（最新）

root串行启动 `20261021T183421Z-mapped-decode-gate` controller203015/child203018，18:34:44Z exit1；完整原件已回本地对应 experiments/framework 目录，原件不得改写。本owner独立核results记录的17份source SHA全部相符、cases[]/statusfailed/manifestexit1一致，故**没有任何correctness case完成**。原full2D、原C3/compactC2在失败前已调用，首次derived skip2D JIT在compiler.py294 `add_accelerate_matmul(pm,opt.use_sme)`拒绝参数68954357763（0x100e000003，37bit），不是数值门失败也不是策略收益负结果。post9031free/free32700MiB，root已封存并转baseline183543唯一GPU。

已实读actual retained a0c runtime和e5 C2：只设BM/TILE/warps/stages，没有use_sme处理；当前source0433/derived67a新增三个JIT形参但未显式传use_sme。需要actualcompiler parse_options/JIT选项提取/cache元数据分清默认/ABI/缓存命中原因。root将在baseline结束后一次只读取回三源码和cache，不在测量时扫描，本owner不SSH/GPU、不直接设use_sme=0、不改模型/全局编译默认。hardware与我分读compiler语义/JIT参数来源。独立失败复核落 `analysis/source/c3-mapped-decode/first-gate-compile-failure-review.json`，包含原件SHA和边界。

root曾授权并行准备CPU隔离servicebuilder，本owner刚读现有prepare_innovation_source/prepare_mm_cta_group_source和driver，尚未写任何builder/服务代码即收到失败，现已暂停，优先定位编译阻断。四候选和失败run源码尚未修改；下一步读root取回的actualcompiler/JIT/cache，提出最小有证据修复并交hardware审，失败原件保持不变。

### mapped 编译根因已定位，最小两行修复已备（待末次互审）

actual源码已由root取回 `experiments/source-audits/20261021T183920Z-compiler-cache`，本owner实读spec JIT **66a168ae959e719186771e66815e807f1e449e66c5283ef596ec3eb0e35cb775**：get_corex_sme31–71排constexpr后按真实operand位置给符合SME layout的>=2D BF16/FP32等tensor置bit，run761在freshcompile自动覆盖kwargs.use_sme。新派生在未mapped的skip2D里给未用decode_req_indices_ptr传out，多出operand index36，因此额外置1<<36；实际错误0x100e000003=原0x0e000003+2^36。backend默认0不代表实际selector值，显式猜0也会被JIT覆盖。hardware独立读源码确认同一机制；prefix旧派生只新增constexpr，因此不增加operand位，其旧门pass不矛盾。

最小修复仅两launch dummy表达式 `else out`→`else cu_seqlens_q`，仍原1D int32 GPU metadata，分支不读、无新buffer、不禁SME、不改数学/模型/全局选项。当前source **919e80abf5b95c55ea63aa8619fa3202cd78b0c4cc0e303df7b4197bf1898316**，derived **72713a90584bc6567706fb881188afa04335230afc13e021c10f862f88d054a1**；runtime仅derived pin更新为 **d085ad6dcc0fd5dc26188d3e0f5801b8e394dc07a79c05a376192ec9e1e95b4b**，gate仅三asset pin更新为 **ede4519424d467bb4f47f52cb57429c5e489ee2324070c482225cc0499b0dc2f**。旧四件仍完整保存在183421/source，失败不改；旧packaging manifest另保pre-sme-fix原字节。

新增 `check_sme_operand_contract.py` 运行actual selector AST、只把torch/os import换CPU描述符，原/prefix/fixed掩码均234881027、broken精确68954357763、唯一差bit36，exit0；不是native specializer或设备模拟。新两行后原source合同必要重跑exit0，32FP表达式/精确变换/扰动拒绝/pins保持通过。日志/最小diff存同source子目录，hardware正核最终两行与hash。root计划当前baseline184244完成后只重跑正确门，新run/launcher，不加timing。servicebuilder仍无新文件，本owner未GPU。

systems的只读KV取证collector cd0c6a...已完成全文静态互审：固定site内部文件/AST不exec、已完成run证据原字节copy、SHA/missing/mismatch、无类型/布局就unobserved，不subprocess/设备API；post是保存证据非实时idle、PCIe不是DMA实测。未跑suite/未改文件；缺RUN_FILES会留partial且抛错不是成功。回执已发作者，当前优先mapped修复收口。

### SME两行修复已终审冻结，等待root重试（最新接续点）

hardware已将source919e/derived7271与183421 raw做全文diff，确认只有两处未用dummy out→cu；runtime d085仅derived pin、gate ede451仅三pin，无其它逻辑差异。actualJIT机制/bit36复算边界也已独立读，未发现进入修正版最短correctness门阻断，未执行suite/GPU。四件现在冻结，最终SHA已全发root；五helper完全未变，原第6节命令flags不变，仅root给新run/launcher名 `...-mapped-decode-sme-fix-gate`，**不带--timing**。root在baseline184244退出清理后串行操作；本owner不设备操作。

CPU selector proof **cff7be424f9967f200a52f64b7b939b291ae2eb9268ac2565b5a472d7df940d3**，stdout **6ee410ab56c09a766392be5233b6239e7612c00e46aa46036653ca10f94b04dc**；derived最小diff **ceaa696012e8e07d6a6f76035fb3b2b380bd7ec4a840418f76d4af17cf6b1599**，原source合同log仍 **22c36a73f0b049ce1a6ab206894f53869e46a4adc04d603d84bf46cd62ecf400**。最新packaging-manifest保存当前四件/全helper/proofs和终审，旧82d... manifest另存pre-sme-fix原字节。首次失败eb13结果/eba5 manifest/17份raw source未改。尚未有正确性通过、性能或accuracy结论；servicebuilder继续暂停且无代码。下一条是等root新门回包后只读独立分析，失败保留、通过也不继承整模型准确率。

利用等待只读互审hardware新 `biv150_visible_prefix_service.py` 7258ad79与transform464b9ea7：exacte155footer SQL→C2→C3后、原ctor后启用、strict模型/并行/no未知feature/safeKV、ContextVar finally、capture/非scope原C2和原87c6/a6d策略均无阻断；FIRST compiled与REAL_LARGE分开、scheduled>=128仅几何机会而非GPU省mask统计。未跑suite或改作者文件，提醒必须有真实REAL_LARGE/shutdownstatus而不能仅INSTALLED；最终builder/CPU合同交作者后续收口。不会与mapped/CTA叠加。

### 修正版设备门与短计时已独立验收；servicebuilder已备

root串行完成 `184809-mapped-decode-sme-fix-gate` 与 `185023-mapped-decode-sme-fix-timing`，两次均exit0。本owner实际读原results/manifest/exit/source/postflight，全17source SHA逐项复算、四形状全部correctness/nextdecode/crossstream/capture布尔门通过；real_forward_selected0是无runner门预期。原2D最大差0.000732421875、三行FP32最大差0.000314325094223，原C2 compactoracle整输出bits相同，不继承SQL+C3的103/105。第一次坏门183421完整保留。纯只读复核脚本 `analysis/source/c3-mapped-decode/review_device_gates.py` 已实际exit0，结果 `device-gates-review.json` 包含原件SHA。

185023单形状D29/16K的32call ABBA复算：wall14.344921375→12.435507453125ms，省13.3107311777%；event14.216219902038574→12.401883125305176ms，省12.7624416985%。包含真实builder（旧C3 suffix仍创建）与新mapH2D，无profiler。两run post9031free/无GPU进程/free32700；只有单层一轮/一形状信号，非E2E、稳定因果或accuracy。

已恢复并写 `scripts/remote/prepare_mapped_decode_source.py` **a41c3858ac5d19ffbb385d9ad075635b560fb272af2c2d6b5c490f04713d2459**：reuse owner0ecf sourcefiles规则，要求原080656目录/核心7SHA/既有5BIV模块精确集合、无innovationmanifest；pin修正版四asset。只改全新code目录，runner精确追加3566，新加runtime/source/derived三module（runtime相对import需要source）；gate只作为前置证据pin不装入包。所有其它输入/输出文件逐项SHA一致，内部regular-file别名可解引用并记manifest，外部/目录link拒绝；不读写installed、不执行runtime/JIT/modelimport。

CPU真实213→216完整copy、原base不变、runnerbytes逆回、现存output/多余BIV模块/漂移asset拒绝、无torch/triton/framework import均通过；原件scratch `tmp/patch-check/mapped-service-pack-20261021T185137122043Z` 保留。报告 `service-pack-cpu.json`。hardware已收到a41c全文快审任务，尚待最终回执；当前四件不变，不启动任何服务。root拟沿现driver context-screen/seed721201/原SERVER；post必须FIRST_SELECTED real_execute=1，不仅INSTALLED。下一条：hardware审通过后发builderSHA/完整两条prepare+screen命令，再等root真实短服务回包。

同时已完成prefixbuilder a4e97877只读终审：相对已审builder仅替三asset names/pins/variant，原0ecf/5basepins/路径/全copy验证不变，213→215与runner+policy/service两module一致；原87c6运行时生成a6d，不引入新内核。未重跑suite/修改作者文件，已告hardware可交root冻结。

### mapped 服务包装已终审冻结，交root唯一设备短筛（最新接续点）

hardware全文只读审 a41c builder与root `launch_mapped_decode_screen.sh` 3455b8d，无阻断：7core/5BIV exact、修正四件pins、运行时需要的三module入包、0ecf内部filealias/全copySHA/全新直接目录/失败保留边界；launcher仍driverbc51/原SERVER/contextscreen+seed721201，idle/端口与driverflock，不以INSTALLED当实际选中。未重跑suite/GPU。builder现冻结 **a41c3858ac5d19ffbb385d9ad075635b560fb272af2c2d6b5c490f04713d2459**，runtime/source/derived/gate d085/919e/7271/ede451继续冻结。

独立设备复核脚本 **04ffbdbab26e4c3420640e0fda331e270e0002a2794fb2b3dd1b053062a71f82**，结果JSON **d1b3eab61ffd3bc08251068ffa034429a49d794b575cbcd9ba297e115489e751**；CPU source-pack报告 **9bfc8005519c3ac1624fca2650ce73c5cc95facc4e2aa1ad453ed126282f4fdc**。latest packagingmanifest已更新设备已过、servicebuilder审阅通过，旧74c...预设备manifest另存原字节；原raw不改。完整prepare/screen两命令在analysis第9节，root将沿自有launcher执行，本owner无SSH/GPU/服务。下一条仅等真实短服务回包，另核FIRST_SELECTED real_execute=1、实际KV/DB/CPU/来源/完整请求与postidle；正信号后仍要独立accuracy，不以单层13%外推。无需继续改代码或重复已过门。

### prefix服务最终三件身份确认，沿用已完成独立审阅

root在mapped真实服务185627加载/INSTALLED成功期间再委派prefix三件终审；本owner先核作者确认与本地SHA，三件与此前全文审阅完全未变：runtime **7258ad7929ad22676201fec045184f0038be4689f2eef3a51b21e30c658029da**、source **464b9ea73f6961097c1cde2c92d97bdf9ed50909e9da1ecbb65f1dd437bccaba**、builder **a4e978770e98aa3c5a245de96470916aae570ef63a55083534465309ceaf615f**。原87c6 policy/a6d generated与runner4467保持，作者仅新增中文说明，不改代码；故沿用上文独立全文终审，无需重跑旧CPU合同或单层设备门。

结论仍为可做独立最短服务筛选：scope只受审execute/dummy、原ctor后enable、C3先装、capture与非scope原C2、finally复原，无跨候选叠加；FIRST compiled/REAL_LARGE不混淆startup与真实推理、几何机会不冒充省mask GPU计数。实际服务选中/最终shutdownstatus必须另验，本owner未GPU。当前等root mapped185627完整原件做独立source/命中/数值/性能和清理核对，不修改任何candidate。

### mapped 首次服务已独立验收：小幅负结果，KV不完全匹配

root取回185627完整原件后，本owner已运行新纯只读 `analysis/source/c3-mapped-decode/review_service.py` exit0，结果 `first-service-review.json`；414份candidate和410份184244基线归档source全部逐项SHA复算；remote live报告414/fail[]、post installed54c通过，原SERVER/负载/seed/packages/installed源均同。DB四snapshot physical实体及schema/logical三hash复算同（516表19270行），CPU6/32GiB/preempt0→0、32/0、524288in4096out。真实EngineCore207423 FIRST_SELECTED real_execute1/D15成立，但不是全程计数。无accuracy或内部数值新证明。

候选121.79016383597627s/4338.478439947034TPS/TTFT62258.128146859235ms，对最近184244基线120.7632626676932s/4375.370359560136/61145.73857927462，耗时+1.026901168283075s/**+0.8503423521%**，TPS **−0.8431724993%**，TTFT+1.8192429978%。最初聊天“matched184244”称呼已撤回：KV候选521840/对照521936，少96，是同参数/同DB而非完全matched。systems另取更早183543分母约−1.07166%，双方会标清基线，不挑分母。首次负结果完整保留，不能因为单层13.31%而解释掉它。

机制仅可限定：marker无时间戳，夹在02:58:42–52周期日志；不估算全程coverage，原计划/forward最终统计缺失。两边各有一个3276左右prompt低窗，不能单独证明coldcompile；启动torch.compile/AOT cache消息不是新mappedJIT命中证据。CPU计划/小H2D/逐层guard/ContextVar成本和真实batch几何未知，未测不能扣掉后报正。root明确暂不加cache取证脚本/observer，仅等prefix/KV最短门后一次未改runtime/参数repeat；本owner未改任何代码或运行设备。

post19:00:37.354668Z 68MiB0%/9031双栈闭/无GPU进程；runner207242Z/PPid1不持设备。候选shutdown SIGTERM后出现AsyncLLM/EngineDeadError和资源清理告警，保原件、不写完全无ERROR、不修改driverexit0/请求成功。报告边界已补analysis第10节。还只读快速审root `launch_visible_prefix_screen.sh`：原preflight/bc51driver/原SERVER/contextscreen seed/driverflock保留，仅buildera4e/READY/env/suffix变更，env只为artifacts目录；无新阻断，已发root，post仍需REAL_LARGE/status。下一步仅等待一轮不改代码repeat与prefix原件，候选不final/不继承103/105。

### mapped 一次原代码复核独立验收，正负并列；本批文件冻结

本owner新写纯只读 `analysis/source/c3-mapped-decode/review_repeat_service.py` **9304a2f47513ae0360b98ee86714b78d0649a7092c188fc950643d2fe42e58e2**，实际exit0，结果 `repeat-service-review.json` **81b6cacfa34cfbb619cd7be77228e07941e91bf8ed21fdcc709ca0bcaf4603d5**。四run183543/184244/185627/191131共410/410/414/414归档文件逐SHA复算，八份DB实体/schema/logical同（516表19270行），原SERVER/load/seed721201/driverbc51/packages/installed源同；CPU6/32GiB/preempt0→0/live/sourcepost通过。两轮candidate **413非manifest文件相同**，innovation-source.json仅UTC/output/命令output路径不同，不能称全414逐byte相同。首审JSON **258793116a996974f9f92c2bf83dc721d9713e887726e9c64e541c480940806b** 未改。

191131为117.02865957096219s/4514.99659944072TPS/TTFT59836.11785736866ms/32-0/524288in4096out；185627首轮121.79016383597627s负结果完整保留。对184244，首轮TPS−0.8431724993%/TTFT+1.8192429978%，复核TPS+3.1911867661%/TTFT−2.1418021146%；对183543分别TPS−1.0716647543%与+2.9533979264%。两个baseline KV521936，candidate两轮521840，**均为同参数/同DB而非容量完全matched**。同candidate首轮→复核TPS+4.0686651308%不能证明全热/稳定或coldcompile因果；不挑正轮抹掉负轮，不再盲刷。

复核EngineCore210483真实FIRST_SELECTED real_execute1/D15，夹本地03:13:46–56周期日志，不是全程计数；无per-JIT hit/compile证据。post19:15:44.582675Z 68MiB0%、9031双栈闭、无GPU进程、414live source无failures；controller210306为Z/PPid1、其余owned已退。复核无ERROR/EngineDeadError行，但首轮shutdown堆栈仍保留。复核rawSHA568368e0a8feee4f80b851b11ce66aa58cdaa163bfcba3b6810e2a2a4502fb5c、manifest88ae91b1cd2c0d1bde7707230dea053035fb801fb73ab0440d1ce0052e6627b9。没有新accuracy，不继承103/105、不合stable/default。analysis第11节已补，文件SHA **2129ec3904c596b37be1be9902df0bd4911b5dea47bf4852649f77d2920fa991**。

本批下一框架CPU研究已落 [`analysis/2026-10-22-next-framework-priority.md`](../../analysis/2026-10-22-next-framework-priority.md) **c9539e2d16361358a4c1582dc656865cd4f5e0f41e415c5cd917cf54b9fe4170**。已读actual184108 scheduler/core/UniProc及旧closeout/memory/prefillgraph/host证据；优先接systems既有“抢占KV保存/恢复”后继，先一次真实executor/worker/KV descriptor，再审save-ack-before-free、zero-after-restore-before-consume、epoch/cancel/shared页与RNG/输出协议。**非新实现或已证大收益**；191545构造成本约0.12–0.24s只读作者已落盘结论，未独立重跑/冒称生产layout或纯DMA。fullreserve/terminal-drain已否定，不重做；13758只是gap exposure而非GPU重算。备选Attention compiled-handle/step recipe只列精确JIT737–790和C3挂点，缺剩余CPU预算不称大收益，未写候选/设备门。async/CPUmetadata小信号、mapped正负、prefix负结果继续保留。

**本批结束，按root要求现在暂停所有文件写入**，供checkpoint/私有实验库同步/完整离线包。未SSH、未GPU、未改任何runtime/builder/launcher/稳定源/default，也未新增模型导入或网络操作。下一条可执行操作由root统一授权：先只观察实际executor与42层KV描述符/host余量；若无法证明安全事务或可避免重算预算即降级，不继续铺实现。当前无本owner在途设备或后台任务。

### root已解锁：实际KV描述符观察器开始实现

root解除上批归档写锁，授权继续CPU-only实现一次性runtime descriptor observer及独立source preparer；原e155/080656、原参数，默认关闭。已开始读actual184108的Core/UniProc/GPUWorker与plugin worker继承，准备在实际KV初始化完成后读42层shape/stride/dtype/device/storage offset/alias，以及Core构造后实际可访问executor/worker对象；不读取KV值、不GPU同步、不分配大buffer、不更改调度/数值/原返回。此条是开始状态，新模块/包装尚未写，source链确认后再定最窄挂点；最终交hardware只读互审，root唯一owner以原driver smoke-only最短加载/一请求验证。本owner不SSH/GPU/共享代码库push。

### KV runtime descriptor最短实现与包装完成，待独立终审/真实smoke

重要时序已证实并经root接受：actual Core构造中109–110才load_general，所以不包装ctor猜当前对象；221绑定step_fn之前general footer已装类step/step_with_batch_queue，首step前只观察一次，phase明确first_engine_step_after_constructor。WorkerFL677–694原initialize_from_config成功返回后一次，避开runner profile_run minimal KV；原返回/原异常透传，诊断失败不改变结果。新取actualworker_base7da443确认self.worker直接引用与代理getattr区别，Core只读实际__dict__链，不RPC/GC/frame/代理getattr。

独立runtime `patches/framework/biv150_kv_runtime_descriptor.py` **fdf2c812edda098ce42c21915e2b9e912901bf681d02cf59a2bb7a236d559576**，builder `scripts/remote/prepare_kv_runtime_descriptor_source.py` **14a206e3416322d24bca9e3f989e071d79ddfcfab310c234325079c260ef03aa**，新init90fe0b381fd53ec5273c623d91b806a0fc21f5b84165beba0b015a1e07d53e74；runner保持e155。runtime默认off；六实际源SHA+方法身份+exact init/footer/vendor守卫。只读42层/runner平面KV/crosslayers的CPU metadata/storagealias，current_stream显式unobserved、不调用设备API；JSON O_EXCL唯一文件、指针仅内部alias key，缺项partial/unobserved。包装复用0ecf，8core+5BIV精确、只新copy改init+加module、不叠候选、AST读literal不执行runtime。

最小CPU合同 `analysis/source/kv-runtime-descriptor/check_cpu_contract.py` **8c4da05b45e123912f05474e2d5b797dfc8545d56da3d1a3a6fcb7e9b4bb4372** 实际exit0/末次1.73s；结果cpu-contract.json **7805ddad16e79b542ca43b8361040e417fbe9764d02fe741b7feadac9dd9e707**。actualWorker方法AST fake依赖证明原ensure/init/后置observe顺序、return/异常/once/失败原路；42packed metadataalias、精确append/拒二次、213→215全copy/base不变/existingoutput拒绝、compile/noTorchvLLMimport通过。故意缺配置fake负例ERROR是预期；不模拟设备，不扩大suite。scratch tmp/patch-check/kv-runtime-descriptor-20261021T194410802945Z保留。

中文实现/边界/精确命令已写 [`analysis/2026-10-22-kv-runtime-descriptor.md`](../../analysis/2026-10-22-kv-runtime-descriptor.md)。已发hardware终审最终runtime/builder两项SHA；此前3cf版本已全文审无阻断，最终只加新actualworker_base pin与stream unobserved/对应builderpin。root已收到launcher所需env `BIV150_KV_DESCRIPTOR_DIR=<unique ROOT/framework/run>/kv-descriptors`、原bc51 driver smoke-only/seed721201与预检marker BIV150_KV_RUNTIME_DESCRIPTOR_INSTALLED。退出必须另核完整worker-kv42/42+core-objects，不能把安装当完成；缺项/错误保留。**下一条只等hardware终审/root唯一owner真实smoke；当前未上卡，代码先冻结，不新增字段/取证或协议实现。** 没有SSH/GPU/installed稳定源/共享代码库修改或push。

### observer最终缺项纠正已互审；0c892/936c才是可上卡版本

冻结自查发现exact e155只有uniform分支创建cross_layers_kv_cache属性；normal可能缺项，之前data.get把缺属性误写observed_none。已在root上传前hold旧fdf2/14a，仅改该字段三路：缺属性unobserved_missing_attribute、实际None observed_none、存在Tensor原descriptor，未改hook/计算。runtime最终 **0c892ad02fbfe663d3f7c8f668cdd000c0c1fc7860ff915db8bce5949cae0667**，builder仅asset pin更新最终 **936c9260724f97b02dc1e69da2f4f0da7cdfaf7fdcb0e8ab866c26d9c028c59e**，init90fe/runnere155完全不变。上条fdf2/14a为过渡历史，不再上传执行。

hardware已定向逆换此单块精确回fdf2并独立终审通过，已发root：无新hook/API/计算，不扩suite。CPU合同只加一条缺属性断言，原合同必要末次1.73s exit0；脚本最终 **445cc886d5506537051dc3caa006d544c9858ef985a4f11c7a7c912b56f5a73a**，结果 **f0771d57a090466499bd48996636c41d198f1f3fe3abfd78618a40c98f0d189f**，scratch `tmp/patch-check/kv-runtime-descriptor-20261021T194709782780Z`。中文说明表与字段边界已同步最终版本。root可按原命令最短smoke；本owner不再改代码/加字段或运行设备。后续须真实worker42/core事件，不仅INSTALLED；当前没有服务布局、save/restore或accuracy新证明。

### 195012真实布局已独立验收；事实纠正与事务互审已落盘

root完成195012 smoke后本owner运行新只读 `analysis/source/kv-runtime-descriptor/review_actual_smoke.py` **8695c1791ab0ee0f4eb1096fea26779de4c6300a8cfeac33b80ea7fc010e18c5**，exit0；结果actual-smoke-review.json **be3f889f2227777f7eb623116ba77bfaf298011e98bf4f8c4bf33ac62421ac16**。412source全SHA/936cpreparer/0c89observer/90feinit/e155runner/bc51原smoke参数/live412/post54c一致；1请求8in32out非性能/accuracy。pid213942实际CoreProc→UniProc→WorkerWrapperBase→WorkerFL→ModelRunnerFL，worker/runner对象id与Core直接引用相同；AsyncScheduler/queue2。42层/flat42均BF16/cuda0、shape[32621,2,16,2,128]/stride[8192,4096,256,128,1]/offset0，42独立storage各534462464B=normal42，KV521936，cross actualNone/shared{}。

DB before/after实体/schema/logical同516表19270行；CPU6/32768MiB；cgroup20GiB限制，worker/core两个时点约4.37/4.64GB不是峰值或pinned保证。post19:51:39.482845Z68MiB0%/9031双栈闭/无GPU进程/412live fail[]，controller213760Z/PPid1。原smoke/events未改。支持继续独立CPU协议实现，不证明传输完成或恢复语义。

hardware纠正源码事实：e155 __init__:587已显式cross_layers_kv_cache=None；本owner此前仅沿uniform赋值检索，误称正常路径可能缺属性，现明确撤回。0c89 missing/None/Tensor三分是未知/部分对象保守处理，不是已证生产bug。中文说明及该纠正已同步；observer/builder冻结原字节未改。文档错误`--run-id`已改实际bc51 positional run_dir，root真实launcher本来就正确。

KV事务独立CPU审阅已落 `analysis/2026-10-22-kv-transaction-independent-review.md`，未改systems文件/运行其suite。关键反例已发：V2只把New移cached仍会因_make_cached_request_data仅notV2补all_token_ids而在e155异步resume KeyError；必须成套copy真实token列表/numoutputs/fullblockreplace/resumedset并保CachedState/RNG对象。pendingframe只在原Core FIFO→abort处理→update成功后按epoch释放，不动queued payload。FullAttention needszero=False，new_block_ids有历史ID，不可把before当活跃zero队列或drain；systems已接受按实际私有/追加尾证明调整。原streaming已有state保generator，但清output；原discard对非None generator退offset4，全局RNG变化仍需accuracy。

### root正式授权worker传输实现；31cc首稿正在跨owner终审

root确认本owner独占 `patches/framework/biv150_kv_worker.py`，systems独占scheduler/Core/transaction/transform；只CPU本地，不SSH/GPU。当前worker **31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf**：无install/框架topimport，显式rpc(wrapper,command)；actual normal42/e155/a8de/7da+受测c95f copy精确guard，SAVE匹配worker请求原prefix blockIDs，单1GiB payload+1GiB headroom guard/分配前后cgroup。device-wide producer fence→D2H→真实event ACK；ZERO仅本事务私有目标raw narrow.zero_（原Mamba helper/no-op不可用）；RESTORE同ZERO映射后H2D/event ACK，不能settle时保host/raw/event强引用返回completedFalse。stale/异epoch不改现slot，DROP支持实际0bytes/空pages、owner/key/serial/settled校验。

root要求的真字节证据：仅诊断env BIV150_KV_VERIFY_RESTORE=1，SAVE预算额外一个layer pinned校验buf；首个成功RESTORE后42层只读目标页D2H复用该buf、逐层eventsync+CPU uint8equal对原savedhost，全部通过才ACK，失败不publish；核验后释放buf/后续不重复，默认off无回读。完整ACK含readback/zero/copy字节与次数/预算信息，已要求systems._rpc记录原JSON而不只Receipt。此诊断不能用于性能窗口。

唯一最小CPU合同 `analysis/source/kv-worker/check_cpu_contract.py` 0.35s exit0，结果cpu-contract.json：命令/预算、0byteDROP、异epoch不污染slot、纯stdlibimport/compile；不模拟Tensor/GPU，不扩suite。hardware已收到当前全文审阅，root/作者已收到接口与SHA；尚未冻结、无真实设备协议门。下一条：回应跨owner必要修复/冻结worker后交systems集成独立源，由root最短实际抢占诊断；本owner不动其文件、无设备任务。

### worker31cc已全文终审冻结，root包装预审通过

hardware已全文审最终 **31cc7f8d48a57c8e6fef23a2200257750d830422b6e887cc4dacdbc2b602ffbf** 无阻断，确认包含_VERIFIED_ONCE；不重跑suite/GPU。runtime现冻结，root/systems均收到唯一rpc接口、DROP0bytes兼容、ACK完整日志要求和依赖c95f。唯一CPU合同脚本 **81b7b106f5f1c1ca5facce6e3d411bd528da3a92bb33d24fe5077d850dc8b94e**，结果 **a82786e055e6b8f770e46aaae3be52646f62704ec991ae93739e1cf814bc81d7**。实现/完整状态/预算/诊断开关/下一门说明落 [`analysis/2026-10-22-kv-worker-implementation.md`](../../analysis/2026-10-22-kv-worker-implementation.md)。无实际KV事务设备结果，不继承copy门或accuracy。

root已独占新prepare_kv_protocol_source.py/launch_kv_protocol.sh，本owner全文预审无逻辑阻断：8core/5BIV exact、helper0ecf、新目录、5asset AST compile/literal init append、只init+5module/fullSHA、无runtimeimports；原bc51/positionalrun/seed/Serve/idle/双栈/driverflock保留，ENV1与purpose/command记录。当前UNREVIEWED三pin/init/launcherpreparerpin会拒绝运行，待systems最终SHA由root填+一次CPUcopy。非阻断建议只补内部filealias解引用清单；owner已拒外部/目录link且fullbytes验证，本owner未改root文件或执行脚本。

下一操作：等待systems最终adapter/transaction给出后只读互审V2payload/FIFO/私有fresh页与完整workerACK日志；root负责最后包装、唯一真实contextlong诊断及封存。observer0c89/builder936c与worker31cc都保持冻结。本owner没有SSH/GPU/后台任务/共享代码库修改或push。

### root最终包装已定向终审，等待真实事务门原件

root最后包装builder **89191b57542e8c2e44eb03b8ebee876f083f3e399e1085149ff0b6a36b49fa42**、launcher **e738b736829172a6cbd525cd0d5e5f9dc343a21e0ffe8bcf1c113bbe4a5db47c** 已本owner实核SHA和最后小delta，无最短真实诊断包装阻断。五asset逐SHA吻合probea4de/copyc95f/transaction **616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13**/protocol **50375e899acbdcee15d3cdec2ecd77875fb355c56ccbfa663271509982ddc19a**/worker31cc；纯AST读取footer+原e043 bytes独立重算init **791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8**，没有执行任何candidateimport。

相对已全文预审只有pins和aliases_dereferenced（与observer同块）；owner0ecf先验内部regularfile，外部/目录link仍拒，原8core/5BIV集合/新目录/只init+5module/全copySHA未改。launcher仅填builderpin，bc51/ENV1/positional run_dir/原seed/服务参数/负载/idle/双栈/driver锁全部保持。root唯一CPU package-check.json已读：410→416、6changes/base+runner不变/noimports，与最终pin一致；本owner未重跑copy/suite/GPU。已即时回root可唯一owner串行真实门，中文worker说明追加最终状态，旧UNREVIEWED只是历史。

当前observer0c89/builder936c、worker31cc与父方最终包装均冻结；下一条只等实际事务SAVE/free/ZERO/RESTORE全字节回读与后继consumer原件，再做独立证据验收。不把CPU ACK链/包装通过当GPU恢复、accuracy或吞吐通过。本owner没有在途设备或后台任务。

### 200957真实首门已独立审完：SAVE→DROP，不等恢复成功

root派CPU协助_try_restore暂态拒绝分析，本owner未改worker/protocol/冻结源或设备。完整200957原件本地后，执行新只读 `analysis/source/kv-worker/review_first_protocol.py` **1ef7084c3e257c2ac2808146c40d7dc58fa3343f8294f28aef81fcaca90f4d23** exit0，结果first-protocol-review.json **3dfed5b2ad314aa9508b4837b0877b1999e9f44218804b45fb391a17203ca7ff**。416source逐SHA/8919builder/e738launcher/50375protocol/616040txn/31ccworker/791cinit/e155runner/live416/post54c均通过；source mapSHA910dd6ae11e6b07aa28cc3443dce790f85a7fca3589ebbc28905603f7c823079、rawSHAea111c6e9e8634f1b6ae224c740b4789aa6f7f918f7e2026402da847e968400b，原件未改。

实际四事件：FIRST_CHECKED true→SAVE serial1成功completed→SAVE_ACK_FREE→DROP serial2成功hostheldFalse。R16704/1044唯一非null页/24physicalruns×42层=1008calls/718405632B，命令与ACK同key/pages/bytes/serial，worker同pid215606。诊断额外pin17104896B，实际cgrouppin前后余量约15.88/14.43GB，guard通过非峰值；无ZERO/RESTORE/回读或consumer，SAVE内容也无新增独立byteoracle，不称恢复正确。32-0/524288in32768out/221.1178005039692s/2519.2725268176705TPS/TTFT62550.40631070733ms仅诊断原值，不作收益。CPU6/32GiB/KV521936/preempt0→1，DB实体/schema/logical前后同516/19270；20:15:43.088172Z68/0/双栈闭/无GPU/416live fail[]，shutdown AsyncLLM/EngineDeadError原样保留，不改exit0。

DROP restore_skips=1只把原因缩到复合precheck或external-prefix allocateNone，不能再区分guard，不能断言本次就是pending/容量。原注入在waiting while token_budget>0内，<=0常规不可达。已给systems/root最关键建议：暂态pending/placeholder/allocNone不应永久DROP；保留host继续原调度，原新output真正发出未恢复victim重算时再DROP，或真正cancel/epoch/digest失效DROP；不park/重排/提前future，不盲删discard导致slot持至finish。原已失败机会完整保留，建议尚非代码或收益。中文worker实现文档已追加完整结果/分支证据和限制。

当前worker31cc继续冻结。下一条等systems/父方新的最小协议revision定向互审及root设备安排；若下一run仍无恢复事件就只报未覆盖，不能因SAVE完成假称整协议通过。本owner未SSH/GPU/共享仓库修改或push。

### 暂态保留revision已独立定向终审，等待新隔离真实门

systems按上述建议写新protocol **a1b691f52f3724b95bbcb11f5702611a17103161001bb929096c71ab4fa74751**；本owner全文diff+最终SHA只读审完，无进入最短新隔离诊断阻断，已即时回root。worker31cc/transaction616040/init791c与footer不变，旧50375副本真实SHA一致，首轮raw/失败机会未改。不修改作者或root脚本、不跑suite/GPU。

新差异只限：临时pending/placeholder/budget/allocateNone保HOST走原waiting/FCFS，首个defer稀疏记理由/free/prefixpages；真正对象/epoch/终止/attempt/status/computed/digest失效discard。原本次新output.num_scheduled_tokens[rid]>0且仍HOST时才ordinary-recompute-admitted DROP，RUNNING本身不足；RESTORE_DONE仍原commit/rollback。没有跳过旧FIFO消费/提前future/改oldpayload，没有新增runner状态改动。output是dispatch前准入计划，非forward证明。极端same-id新对象只可能DROP理由不够精细，安全上不恢复旧host，已告作者作为归因限制，不扩大本批。

唯一新合同 `tests/test_biv150_kv_protocol_defer.py` **b1d8cbb3aece15bbe4bfe395e0586f516be8a839db95199ddc99e95447600254** 已全文读，作者实际1test/0.002s通过（我未重跑）：pending重复只一理由/noalloc、原FIFO后placeholder、allocateNone保留，output0即便RUNNING不drop/原output>0drop，以及identity/attempt/digest/terminal释放。最终互审详情已补 `analysis/2026-10-22-kv-transaction-independent-review.md`。

下一条root将protocol pin改a1b到全新隔离source/唯一设备门；原worker/COPY门不重复。等待实际ZERO/RESTORE、全byte回读、同CachedState/RNG与后继consumer原件再独立审；目前仅SAVE成功/恢复未覆盖，没有新accuracy/性能或默认合并。无本owner在途设备/后台任务。

### 暂态保留新包装最后字节delta已审，可由root串行真实门

新builder **ac18b84dfc2e9435c6984f05ddc084d24458d2b158003df29ec9fedc641b6429**、launcher **c4526fa0178989b47647acba2407025cfd04d54034c97c569451d8b77bc5a973** 最终SHA已实核；旧89191/e738两副本也逐SHA核同。只读git --no-index差异显示builder仅protocolpin50375→a1b与variant，launcher仅builderpin、全新run/source名、前轮protocol标记/variant与中文注释。原bc51/Serve/contextlong/seed/ENV1/idle双栈/driver锁/全copySHA/aliases不变，worker31cc、transaction616040/init791c不变。无进入新隔离最短诊断包装阻断，已即时回root可唯一owner运行。

没有重跑package copy/CPU合同/COPY门/GPU，没有修改root脚本或协议/worker。中文worker说明已补当前最新pending状态；首门SAVE→DROP/旧source/原shutdown证据均保留。下一步只有等root新run实际事件与完整原件，继续严格区分admit计划、GPU完成回读与后继消费；当前无新恢复/accuracy/吞吐结论。
