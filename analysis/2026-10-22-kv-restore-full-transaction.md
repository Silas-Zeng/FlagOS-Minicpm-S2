# 整页完整覆盖恢复：RESTORE_FULL独立事务

2026-10-22，天数BI-V150。本agent仅CPU实现/审计，root独占设备；新FULL214400现已真实VERIFY1通过（见下一节）。候选累计容量67e4/私有页排序0e功能，但不继承其GPU资格：212106/213616仍属于旧ZERO链。本文更新实现与实际诊断状态，不修改历史原件。

## 最新真实门：214400显式FULL/0ZERO/42层回读与原消费通过

固定2071入口已实际运行exit0，机器审计 `source/kv-transaction/214400-independent-review.json` SHA aa16dc31f430230db6c1c0ed69f55b88b3d036b3822bf59e2b9a8ddd9d97ea45。416源/固定b4e63947与1aff84be5d9a/原080656-e155-bc51-SERVER-seed、CPU6/32GiB均核。实际SAVE1→FULL2→DROP3，0ZERO；R16704/P1044/718405632B，SAVE24run/1008copy，目的66run/FULL2772copy、42层回读2772copy全byteequal。caps/zero_stageFalse/zero_calls0/fullcoverage/destbound真ACK齐，fast454/host释放/runner六checks/原output8token消费。没有套旧1043页/16token。

32-0/524288in32768out、226.79482778999954s/2456.2112171085555total/TTFT62775.54467374284ms、KV521936/preempt0→1；DB51919340三SHA897/29d/71ac前后同。21:49:38.171431Z416源post不变/68MiB0/双栈closed无GPU进程；测前ERROR空，raw完成后shutdown EngineDeadError/WARN保留。包owner SHA21ae6e302795fba5d6b09b6597d26cd0e58d95c3805cffe079ded2934ca981ea。**仅VERIFY1诊断，不比较性能或继承完整accuracy/异常多victim资格，不从省零写入量推算收益。** 以下“准备/待设备”段落为交付时设计与验收方法，不能覆盖本次真实通过。

## 切口与职责

FULL只消除本项目保守恢复协议新增的中间清零，不改变比赛模型/参数、请求FCFS、R选择、KV池大小、原allocator或采样/RNG。actual normal42为BF16 `[pool,2,16,2,128]`、stride `[8192,4096,256,128,1]`、offset0；每层每完整16token页16384B，42层每逻辑页688128B。H2D覆盖R/16个目的页的全部K/V/head/dim字节，未发布期间没有消费者需要看到先前的零。R外原scheduler新算的suffix不在覆盖证明中。

| 新文件 | 职责 | SHA256 |
|---|---|---|
| patches/framework/candidates/biv150_kv_full_restore_transaction.py | 从616新增真实FULL operation和完成转移 | 84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883 |
| patches/framework/candidates/biv150_kv_full_restore_protocol.py | 从67e4新增caps保存/资格选择/真ACK证明，不改原FCFS | 1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8 |
| patches/framework/candidates/biv150_kv_full_restore_worker.py | framework所有，验证完整42层覆盖并执行原H2D/事件/回读 | 5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477 |

旧canonical0e、capacity67e4、worker31cc、transaction616和page-copy c95f保持原字节。新三文件仅在新source分别映回 `biv150_kv_protocol.py`、`biv150_kv_transaction.py`、`biv150_kv_worker.py`，保证原相对import，不能直接从candidates子包启用或覆盖旧实验。

## 实际接口与调用顺序

RPC键仍为 `key/kind/operation_serial/pages/prefix_tokens/nbytes`；新增kind=`RESTORE_FULL`，不传新tensor或改变旧command格式。key包含session/request/epoch/attempt，slot串行号持续递增；同operation、页表、字节数与真实完成回执必须一致。一次新路径预期如下：

```text
原FIFO消费所有可能旧writer → SAVE1提交/producer围栏/D2H真完成
→ SAVE ACK携完整normal42快照能力 → 原free成功/tx确认source已释放
→ HOST_RESIDENT（原FCFS/低容量快拒/自然等待不变）
→ 原allocator得到全部private页 → guard并原地排序 → tx.bind/ALLOCATED
→ RESTORE_FULL2提交/worker绑定目的 → 原producer device围栏
→ 完整H2D + Event完成 + VERIFY1逐层回读
→ 真ACK/RESTORE_DONE → 原schedule实际有本rid工作才PUBLISH
→ DROP3释放host → 原runner cached resume六检查 → 原output处理
```

**不存在ZERO command、ZERO_PENDING或伪ZERO receipt。** transaction只在ALLOCATED且无inflight时提交FULL，成功同operation真Receipt归RESTORE_DONE；旧ZERO/RESTORE接口与分支保留。SAVE的device fence、RESTORE自己的device fence、copy完成Event与VERIFY1回读均未删除，不能把这些同步成本算作已省。

worker只在SAVE实际_finish之后回传 `full_restore_supported=True/saved_layers=42/saved_page_bytes=16384/saved_prefix_pages=R/16/saved_bytes=nbytes`。adapter保留这五项，同时核tx.ALLOCATED/noinflight/no cancel/source已free、R整页、请求computed0/PREEMPTED、同实际req_to_blocks list、numcached整数0、完整目的页数、ref1/unhashed/非null、页ID唯一及与tx.destination一致；caps/私有proof不足时**仅提交前**执行原ZERO→RESTORE。

worker接受FULL前独立核SAVED/owner/key/serial/settled、normal42储存签名、42个唯一完整pinned CPU uint8 host视图、42个GPU raw页视图、目的唯一、无已绑定目的以及c95f PagePlan全R页覆盖。不是仅相信adapter的capability。绑定后记录RESTORE_FULL_BOUND，完整copy完成及可选回读后成功ACK须带 `zero_stage_executed=False/zero_calls=0/full_coverage=True/destination_bound=True/full_coverage_bytes=nbytes`。adapter在制作Receipt前再次核这些字段。

## 失败、取消与所有权

缺完整覆盖资格只允许在FULL提交前退回旧ZERO路径。FULL已接受/可能部分写入后，禁止重走ZERO或把失败解释为未执行：未settled保持inflight/host/目的引用，不能publish/free；真实completed失败Receipt进FAILED，再沿原私有页free成功→rollback→DROP。成功ACK缺覆盖证明会在Receipt前raise，保inflight并failclosed，不伪装成功/降级。cancel发生在inflight时也须真ACK后转CANCELLED，随后实际free/host DROP；stale key/serial/字节映射回执不能推进状态。发布后的回滚限制不变。

原FullAttention `needs_kv_cache_zeroing=False`，历史new_block_ids不是待zero集合；本候选不消费/重排那份历史，不扩大零机制。完整覆盖只限本事务已拥有且未发布的R页。private页排序仍可能改变未来free/LRU序，不能声称整个allocator轨迹不变。

## 最短已做CPU合同与互审

唯一 `tests/test_biv150_kv_full_restore.py` SHA **0035b97f5331083001409871165a66e364c3c1a8f956182e2080d53520e65a54**，1项0.002s通过；没有重复COPY/DTO/原worker套件。它调用actual worker command parser/完整覆盖plan元数据，以及actual adapter/transaction与ACK stub，覆盖完整/缺caps、pending/stale、success缺proof、failed-settled/未settled和cancel回滚。TensorDescriptor/transport是CPU替身，**不执行worker GPU RPC、copy、Event或producer fence**，不能作为GPU完成/字节/模型accuracy证明。完整逆变换确认protocol回67e4、transaction回616；证据在 `source/kv-transaction/full-restore-cpu-check.json`。

framework/hardware/root三方最终审84be/1aff/5d9a及唯一合同均无最短隔离VERIFY1门阻断；两位审阅者没有重复跑套件/设备。

## 新包装与待设备门

- `scripts/remote/prepare_kv_full_restore_source.py` SHA **b4e04e504e0ffda195913a267ca39b87562c73f30bb71e8dbf304392de0ebbd3**。
- `scripts/remote/launch_kv_full_restore.sh` SHA **63947c7fc1c7bc423ceb41d99fb50bcd5b5560442609d76e597ccd5c5fd52bfe**。

沿a79b/0ae最小差分：三输入新asset映到canonical模块、固定新pin、独立kv-full-restore标签与FULL目的字段；080656/init791c/e155、原bc51/context-long/seed721201/VERIFY1命令不变。保68MiB0/无GPU进程/9031双栈闭前置、DB快照/source archive及新目录拒覆盖。仅Python/heredoc compile和静态pins/diff，无shell/prepare整复制/新suite/上传/设备。hardware已只读终审最终b4e/6394，无阻断；root决定后继串行设备顺序，213016容量性能基点已完成、当前213616 VERIFY0候选在途，FULL尚未启动。

后继最短VERIFY1必须看到同key的真实SAVE caps、私有页映射、**RESTORE_FULL成功ACK/no ZERO RPC/zero_calls0/full_coverage/destination_bound**、42层全byte回读、原runner六checks与原输出消费、32/0和完整source/DB/KV/CPU/后态。若只旧ZERO fallback则FULL未激活，不能算新模式通过。通过诊断仍不代表性能/完整accuracy；后继匹配VERIFY0须原参数、相同DB状态与KV容量边界如实记录。没有ZERO独立时长，省写字节/调用只能按实际R/页图描述，不推算TPS或预设最低收益。

## 已准备的本地原件验收入口

`scripts/review_kv_full_restore_run.py` SHA **2071bff34cdcd469294b406966ad86a0941d556b1d1e9ddd62dc87f927caf55b** 接收真实FULL run ID。复用固定81f227…的现有stdlib inspect_run（仅取定义前缀，不执行其历史CTA底部），适配context-long并将DB相等硬断言改为报告真实变化；继续全416源/原driver-benchmarkSHA/CPU6/32GiB/post/DB实体复算。另固定b4e/6394/三FULL资产及原080656/init/e155/封存bc51 AST SERVER。

它只在真实SAVE→RESTORE_FULL→DROP三个ACK/serial1,2,3、无ZERO/旧RESTORE、同key-pid-pages-bytes映射，完整SAVE能力/FULL覆盖/无ZERO/42回读、私有排序/原runner六checks/实际原输出消费、host释放和累计计数都齐时通过。R/页数/连续段/字节和调用数从实际命令推导，consumer只要求实际正整数，不写死1043/1044页、66段或16token；DB变化照录，绝不据此算收益。

```powershell
python -X utf8 scripts/review_kv_full_restore_run.py <实际FULL-run-ID> --output analysis/source/kv-transaction/<实际ID>-independent-review.json
```

只全部通过后独占创建新输出，拒覆盖。缺原件打印pending_missing_evidence并exit2，校验失败not_passed/exit1，均不写通过结果。入口准备时仅compile/AST stdlib/pin检查，没有合成run/ACK；随后214400原件到齐才执行inspect并得到本节开头所列通过结果，不重跑CPU联合合同/设备。静态准备证据 `source/kv-transaction/full-restore-review-entry-check.json`，送framework只读快审。FULL实际run完成并由root下载后再运行/登记，当前容量213616仍由root独占。
