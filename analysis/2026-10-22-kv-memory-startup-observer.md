# 定位6块KV池差异：同资产、单次、仅现有标量的启动观察

仅针对本实例天数 BI-V150 16SM/32GiB、6CPU配额、20GiB host。此前 [容量原因审计](2026-10-22-kv-capacity-variance-audit.md) 的结论仍是**直接原因未知**。213616 capacity启动KV521840，而213016 stable为521936；最新214400 FULL原件又为521936。这反对“有额外protocol模块就必然少6块”的简单归因，也不能反过来归因FULL或VERIFY。

root已批准准备最小观察器及一项必要CPU原调用合同。设备、远端取证与串行启动由root独占；本owner不SSH/GPU，不改已受测a8de/e155/67e等源码或池参数。

## 已追到的实际调用链与组成

调用链来自本地actual源：Core27b2 `_initialize_kv_caches:283` → abstract `Executor.determine_available_memory:146–147`（SHA `419002195d13cf050c3ea9705d18a12456c890c27c470a1efadce7de27ded0b1`）→ UniProc4625 `collective_rpc` → serial_utils d75c `run_method:503` 动态getattr → WorkerWrapperBase7da4 `__getattr__:334` → WorkerFL a8de `determine_available_memory:495`。本模型是实际UniProc，external-launcher子类另有CPU reduce接口，观察器不把它混入。

a8de在init_device中先初始化分布式环境/随机种子，再gc/empty-cache，:451创建原init snapshot，:452计算requested；随后才构造runner并load_model。determine常规路径:536–545及原 `memory_profiling_fl:156–196` 自己执行原empty-cache/peak-reset与原前后snapshot。e155 `profile_run:6323–6417` 做原最大dummy forward、sampler（适用时）、原同步与清理；不是只测模型权重。原CM退出后，WorkerFL还会用inside-profile采到的peak重写profile_result的peak增加量，再组成non-KV并返回int。不能拿另一个时点的after_profile peak冒充那个采样点。

公式本身未变：

```text
available = requested − weights − nonTorchIncrease − torchPeakIncrease − graphDeduction
```

snapshot中的 `torch_memory` 实际来自memory_reserved；`non_torch_memory` 是(total−free)−reserved。它们是原API当次返回值，不自动等于某个具体分配调用的物理字节。若后来发现某项解释了available差额，也只是公式贡献项证据，仍不能没有allocation trace就猜其底层来源。

## 为何不直接开DEBUG或提前导入WorkerFL

已有log未给profile项，连WorkerFL的INFO available也缺失，尚不能判定原因。只看源码日志级别不够：需要实际logger/父链level、disabled、propagate、handler/filter与info_once函数身份。观察器用独立stdout JSON打印这些现态，不改logger配置、不执行过滤器、不调用isEnabledFor以写其缓存，也不dump环境。尤其a8de构造函数:235–237存在DEBUG遍历环境，不能用全局DEBUG代替这次定点观察。

初稿曾在general-plugin安装时直接import WorkerFL；未部署，自查发现它会提前模块加载，不能据“没有显式CUDA调用”声称没有间接副作用。root批准收紧为**只读取自然已加载sys.modules**：general footer仅武装已加载abstract父入口；到原显存测量调用时，实际UniProc/driver wrapper/worker已经创建，才临时接入原worker和原CM。缺模块、source或身份不符只明确NOT_ACTIVATED并执行原父调用，不主动import worker或设备模块。

## 冻结观察器与唯一CPU合同

模块 `patches/framework/biv150_kv_memory_observer.py` 最终SHA：

`6a772a741ac96ac1f9d7ef7c8cff7578117bbdc8cc97258afaeec88e1c5b436c`

默认 `install(enabled=False)` 无动作。显式启用后，只在原父RPC的一次调用内用ContextVar强持原CM已创建的profile_result，原with/enter/exit/异常抑制照跑；保留WorkerFL原managed包装、原调用次数、原返回和原异常。finally按函数identity恢复worker方法、CM全局和父方法三处hook，不留运行期hook。没有新MemorySnapshot、CUDA/统计/allocator/sync调用，没有settrace/setprofile或动态framework import；输出不读Tensor值。

记录内容为现有init/before_create/before_profile/after_profile各snapshot，现有weights/nonTorch/peak/nonKV，worker requested/available/graph estimate、原worker int与原parent list、原wrapper/__wrapped__代码身份、有限调用链和logger现态。`profile_torch_peak_reconstructed=before_peak+peak_increase`、`graph_deduction_reconstructed=requested−nonKV−available` 明确放在derived字段，**不是新采样**。分支没有profile context时输出unobserved，不能补0。

唯一合同 `tests/test_biv150_kv_memory_observer.py` SHA `0becd99b5de8c98926538a9e174ebe68b31476c3079a5c4703eea40f8dcd33d5`，最终1test/0.002s。四个必要子场景核原父/worker各一次、原list对象、同异常对象、原CM抑制、自然模块缺失回原路、三hook恢复及ContextVar reset。它使用CPU stub，不执行真实WorkerFL/profile/GPU；不能证明真实数字或事件。静态语法/禁止调用名审查及精确两init计划保存于 `source/kv-memory-observer/cpu-check.json`，SHA `137d77ce9d4128f4f1d8471af39e49e3c59d0f2167388cfb1f26cf158928cb5e`。

framework owner已全文只读终审6a772a/0bec，无当前阻断，未重跑合同。初稿b092已废弃且未部署；根因仍待原值。

## 精确接入计划与最短设备边界

同一观察器资产分别加到**全新隔离目录**中的stable080656完整410树和已受测capacity212106完整416树；输入要以原完整SHA清单验证。只在完整既有general-plugin init末尾逐byte追加模块内INIT_FOOTER，不能插SQL/C2/C3或协议footer之前，不改worker/runner或任何原模块。

| 变体 | 追加前init SHA | 追加后init SHA |
| --- | --- | --- |
| stable | e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff | 00e8def05ec16d3dcc01bcfe47c976dd4954402984b0a9ba1162d4b72547c3f4 |
| capacity | 791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8 | 39fb96f474c4bacc79ba4cdc1ae27ce877f9dd654825c792dc8446ac620b08e0 |

观察器自身会核完整前缀及最后footer；三个原protocol相对导入和source guard仍成立。原 `innovation-source.json` 保持原字节，仅作为历史基点证明，新包装应另写observer manifest，明确完整最终源/基点/变更。systems已获root后继授权准备该独立包装，本owner尚未审其最终产物；本模块/合同回执不等于未来builder也通过。

后继只需root串行两个原参数启动/最短smoke诊断，VERIFY0、同observer、完整源/DB/CPU/前后态，避免再跑5分钟性能pair。至少要同PID实际 `DETERMINE_RETURN`、`profile_context_calls=1`、原值齐备、`PARENT_RETURN`与三restored均True，并关联随后KV池token数；ARMED不代表观察完成。NOT_ACTIVATED/REJECTED/OBSERVATION_INCOMPLETE或缺profile字段均不能当原因证据。

原模型启动自身仍会profile/分配/同步，观察器不新增这些调用。stdout/CPU元数据与新目录可能有观察扰动，两个诊断未复现旧差异时仍要保留，不能把新值补写成旧轮历史原因。没有任何util/固定KV/假buffer/模型参数改变，未部署、未产生新设备或性能结果。

## 后继包装已准备并静态终审

systems最终 `scripts/remote/prepare_kv_memory_observer_source.py` SHA `0ab0ce3ab3d8cde4a8e725d9fdfd3e62726fcf95613fbc1e55b850b3e48a9029`、`scripts/remote/launch_kv_memory_observer_smoke.sh` SHA `5bdb67afe573d9ffc803e40bafcaee2e7e7fd85e8b831bb94137516e85c060fd` 已由本owner实读hash/全文终审，无当前阻断。固定73e5/5bef推导stable410/cap416完整输入，输出新412/418树；每份只精确append原init并加同6a observer，新manifest保最终全图，原innovation字节保留。原bc51/服务器参数/seed721201/VERIFY0/--smoke-only不变，真实DETERMINE_RETURN为要求marker，完整原值/父返回与恢复仍须测后另核。

`source/kv-memory-observer/wrapper-check.json` 只记录owner语法/heredoc/精确append/pins，双方没有运行shell、整copy、额外suite或设备。本回执不代替root后继真实启动验收，旧前文“待产物”是历史，当前包装已CPU准备。

## 第一轮215849 stable实际观察已验收，等待第二轮

root已串行执行 `20261021T215849Z-kv-memory-stable-smoke`，原包SHA `f9e37bd5b7f02d9d39fcad7291a27727e26efff7840ecf8c579f5eac10842044`。本owner独立读完整原件，源a8de/e155/6a及init00e8不变，412树；专项 [215849-stable-review.json](source/kv-memory-observer/215849-stable-review.json) SHA `1ce267ebd0224f1f7d9f8f2b5a57ad9755f71e184c9b0d96cf0c57846cbedb0b`，server.log SHA `66241222c8c3553c16d22187d27036406fb4c143daa583b733fd6276f56414f5`。

EngineCore231345仅一次实际DETERMINE_RETURN及PARENT_RETURN，同PID、profile_context_calls=1、原int与父list一致、三hook restored全True，无拒绝/不完整事件。API231177只有ARMED，没有实际profile，不把它误记成另一测量。真实caller也确认Core283→Executor147→UniProc92→run_method510→WorkerFL，wrapper/__wrapped__均原已审文件。

| 原有组成 | 本轮字节值 |
| --- | ---: |
| weights_memory | 5101233152 |
| non_torch_increase | 1000341504 |
| torch_peak_increase | 656424960 |
| non_kv_cache_memory | 6757999616 |
| requested_memory | 29205777612.8 |
| available worker值 | 22447777996.8 |
| 原worker int / parent list元素 | 22447777996 |
| graph estimate / 重构扣减 | 0 / 0.0 |

三组成之和、requested−nonKV及原int截断全部逐项成立；nonTorch增加量也与after_profile−before_create一致。profile snapshot的auto_measure=False是原CM先建对象、随后显式measure的原行为，不代表未观测。derived peak重构5774530048不是新增GPU采样。

当前worker/vllm_fl均NOTSET且无handler，propagate到root WARNING30，前后状态相同、manager_disable0；这解释当前标准INFO/DEBUG不输出，info_once函数链未被解析且旧轮logger现态没有证据，不能倒补历史。没有启DEBUG或dump环境。

最终KV521936=32621块；原返回减32621×688128余354508B，整数商也等32621。这是观测与算术一致，不冒称已取得installed配置生成器的floor源码/完整中间值。root确认DB519/19340三SHA同、post412/68/0/双栈closed。本轮只一个启动样本，不解释旧六块来源、不报性能；220122 capacity仍由root唯一设备owner执行，待完整第二原件后对照。

## 第二轮220122与跨样本比较：本次未复现6块差异

第二轮 `20261021T220122Z-kv-memory-capacity-smoke` 已完整封存，root包SHA `b2bab46a3cda84b0654354e7848af52b40711061d61992690bc233b01f6ff290`。本owner独立核capacity原67e4/31cc/616/c95f、observer6a、init39fb及原a8de/e155，Engine231998一次实际DETERMINE/PARENT、profile1、原list/三恢复全True，无拒绝/不完整事件。418源后态通过，68/0/双栈closed，root回执DB519/19340前后三SHA同。

本轮所有profile字节组成、worker字段、4个snapshot的非时间字段、derived重构、原int/parent list和logger均与215849完全相同；KV也为521936。限定在这些观测字段中，精确递归差异只有：

- `profile.profile_time`：6.896814823150635 → 6.929859638214111秒；它是启动profile时段，不是服务性能成绩。
- init_snapshot、before_create、before_profile、after_profile的4个timestamp。

PID、源目录/variant及相应代码路径当然不同，不能把上述限定比较误写成“整个run只变timestamp”。两轮实际loaded源码SHA身份相同，观测前后logger仍WARNING30；前文第一轮表格的字节数对第二轮也成立，原worker/父返回同22447777996，graph0，池余354508B的算术一致性同样成立。

证据：第二轮专项 [220122-capacity-review.json](source/kv-memory-observer/220122-capacity-review.json)，SHA `708079b2fdf6a9aec20ec2a5f99f8dd63d21336e6fbb4c214e5102e127de67e6`；跨样本 [startup-pair-review.json](source/kv-memory-observer/startup-pair-review.json)，SHA `0fc5509022de9d376996f11fcc8342800fc04c1410e11097a2ad9c1c4fff794a`。第二轮server.log SHA `9caa6aa1510891f7cc3ff3f03f40067ccfdf343410042161154a96fd70545ef4`、清单SHA `6254fa1f1c483f249af4f002bf6d090f8df02821e33fd583f4dcc7112f50b770`。

结论只到：**同一观察器下这两个启动没有复现旧6块差异，历史直接来源仍未知。** 不因相同结果而归因观察器、FULL/VERIFY、缓存，也不补造旧中间值；各一次启动不能排除罕见变化或观察扰动。按root明确决定，不无限追加startup样本。下一步仅计划把同一观察器纳入原参数VERIFY0对照，以实际负载同时携带启动分项，仍需容量/DB/CPU/源/参数共同条件；本阶段没有实现该下一包装或运行新实验。

本阶段原件/中文/JSON已完成，现暂停本owner文件写入供root一致发布/ZIP；目标仍active，这只是保存窗口。没有新研究、GPU或SSH。
