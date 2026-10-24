# 当前工作与 API 接续

更新：2026-10-22 21:53 UTC。主线为框架、KV 管理、调度及与现有算子的适配；新增算子由队友负责。原始证据不覆盖，收益按实际验证范围报告。

## 当前设备与下一步

- 当前唯一GPU作业为 `framework/20261022T215040Z-skip-computed-h2d-service-baseline-decode4k`，driver368463/server368476/Engine368644；原bc51 decode4k/4096+128/64请求/c64/seed721201，source完整414、runnercc442。214819单H2D方法门已PASS并封28原件；当前是该方法独立短服务pair第一侧，21:52 KV521840。结束后原sealer归档，再手动调用`tmp/deploy_short_gate.py skip-computed-h2d-service-candidate`；不要启动第二个GPU任务，root为唯一owner。
- **KV组合短pair已获可比正信号**：213757基线169.825947946s→214326候选168.399855358s，吞吐+0.846849%、时长−0.839738%、TTFT+0.043841%、TPOT−1.438678%。两侧32/0，30项门全过，同KV521936与DB540/20112四端三SHA。候选VERIFY0真实R16704/1044页/718405632B、原消费8、无诊断回读；549+563原件已核。保留单pair，不称稳定收益，accuracy未跑；详`analysis/q-gqa-kv-swap-verify0-pair.json`。
- **213134 VERIFY1已完成并通过**：root逐490原件核传输，reader6c5f73aa复用原事务验收，通过32成功0失败、R16688/1043页/每方向717717504B、SAVE210/FULL2772/zero0、源及目的42层完整字节、runner六checks、consumer16、host释放；KV521840、DB540/20112前后一致。诊断时长180.527678s不作性能比较；shutdown的EngineDeadError位于结果完成后的原owner清理阶段，原日志保留。新组合尚无独立accuracy。详`analysis/q-gqa-kv-swap-verify1.json`。
- **原官方已完成**：`20261022T202736Z-q-gqa-framework-official` exit0、8轮共1536成功0失败、原8raw/2summary及丢首轮2–4均值校验通过，严格清理。4K总5002.10/output1000.42 tok/s、262.25s；16K总3679.39/output216.43 tok/s、605.60s。DB532/19839→540/20112、三SHA变化，不能与旧DB算增益；引用原184819的101/105准确率。root核703原件并下载至`experiments/official/20261022T202736Z-q-gqa-framework-official/`；tgz 3340233B、SHA3f05f5527d774d3071d70a6a27cbcc7e7932f27e2add8cdee480e56298604cea。下方早期官方进度已被本完成状态覆盖；详`analysis/q-gqa-official-final.json`。
- **有限KV准入保留为默认关闭的研究候选，尚无确定收益。** 四轮原16K/1024输出/32请求/c64/seed721201全部32成功、0失败。候选真实将抢占1→0；同532调优DB的最终对照为195213基线169.815742s、194634 warm168.133490s，表观吞吐+1.000545%、TTFT+2.282034%、TPOT−3.552231%。24项检查仅KV失配：521840对521936，所以严格收益字段为null，不能称已确认提升。[最终分析](analysis/finite-growth-common-db-service-pair.json)
- **停止这一点的重复测试**：不为凑KV反复重启、不放宽可比门、不把已有Q/GQA准确率套给新调度、不追加完整官方性能或准确率。旧性能日志没有non-Torch/peak分项；新201344/201518启动诊断出现反向容量差，non-Torch在profile前已差4MiB，但不能回填旧轮或归因finite import/具体allocator。保留有限准入机制与小幅正信号，默认关闭；不再独立追这4MiB。
- **小收益备用短测已就绪，尚未上卡，排在KV组合之后**：CPU metadata成功时，`num_computed_tokens` GPU副本没有数值消费者，尝试省去原H2D；helper拒绝时先补原copy，再走原GPU逻辑。只改runner三小段（cc442→97f41），其余413源、固定buffer/event及原async-spec校正不变。真实方法门461676含毒值、有效行回退与原graph消费者；launcher e8f9bb已交叉审阅。素材完整保存于`archive/ai/20261022-framework-kv/skip-computed-h2d/`，部署器快照在父目录。等独占设备空闲后，root可调用`tmp/deploy_short_gate.py skip-computed-h2d`。未有净收益或新准确率；门过后才进行原bc51短服务对照。
- H2D方法门后的服务接线也已交叉审阅：`archive/ai/20261022-framework-kv/skip-computed-h2d-service/`。preparer e174044c／launcher c342134a，强制实际方法门PASS才构建两臂；原bc51 4K/128输出/64请求/c64/seed721201，完整414只runner差异，复用原metadata首次标记与Q/GQA成功execute，无新热日志。每次一侧，原sealer兼容。未部署、未测；当前目标只是删一次约124–256B的H2D提交，queue2可能掩盖，无端到端收益承诺。
- 后续优先KV调度及框架适配。不要回到新增算子、盲目组合或重跑已完成的诊断。额外pin抢占KV暂NO-GO：原逻辑已优先保护有效前缀，pin会挤占running增长；无可替代低价值页的证据。active-width普通切片copy、GQA signature缓存也无新机制，不重复。
- 原server日志无抢占行，不能等同零抢占。root在21:00:17Z只读一次既有`/metrics`，累计抢占4、length成功1152、running19/waiting45；请求往返42.845ms，不等于CPU成本或benchmark损耗。原文/回执在远端该轮control与本地progress/observations，51293B、SHA227176db；没有修改服务源码/参数、没有profiler。此实际动作覆盖旧“不插新采样”计划；不再重复读取，4次不能精确分摊case。官方结束再结合原件判断下一KV策略，不能把32请求的一次恢复线性外推128请求。
- **下一主线为Q/GQA＋已有KV保存恢复的最小组合**：撤回旧“Q/GQA已更快所以swap NO-GO”的过早判断，那不是负收益证据。192308原轨迹中7步目标为唯一q>1请求，294个2D kernel全部对应目标恢复prefill，合计1.587201499s；同批GQA 0.3221s不能删，整个2.8555s窗口不能全部计为可节省。旧swap内部FULL相对ZERO的小收益不是swap相对重算的收益；旧跨容量对照未证明净收益。
- CPU确认原e155与当前cc442的`_update_states`、记账、KV分配/reshape、执行和capture相关方法未变；新metadata/async/Q/GQA没有改变KV写入布局。`tmp/q-gqa-kv-swap/`已备最小422源组合：只显式重定worker/protocol两处runner身份锁，init追加旧footer，保留原6个KV/bridge文件字节；不混入H2D、finite或新RESTORE pitch。preparer6d093740、launcher1bd16b32，待hardware新增差分审阅后root可上原bc51长负载VERIFY1（诊断，不计性能）。先证实两组42层源/目的字节、真实消费者、Q/GQA及32/0，再决定VERIFY0单pair；新组合不继承旧准确率。
- 后继独立机会仅保存几何依据：旧真实FULL目的1043页可由66连续段合并为14个连续/等距段，42层提交数2772→588，字节量不变。原SO只支持D2H，不能交换指针直接用于H2D。`tmp/q-gqa-kv-restore-pitch/README.md`记录实际ACK/页分布；未实现、未上卡，不叠入首轮组合。

## 本轮已完成

- **当前启动分项诊断**：201344基线KV521936、201518 finite KV521840，预算分别22447777996/22443583692B。finite非Torch残差从before_profile已多4194304B，profiling自身非Torch增加两侧均60817408B；权重、Torch峰增、graph估计均同。两次原bc51 smoke、原SERVER/seed不变，32个输出token IDs及文本相同、DB532四端三SHA同，观察器各profile1/三hook恢复。只解释本次组成，不算性能/准确率，也没有mixed Q/GQA实际命中。资产与接线在`archive/ai/20261022-framework-kv/current-kv-memory/`；[分析](analysis/current-kv-memory-smokes.json)。
- **CPU筛选停止项**：text-only闲置inputs_embeds各8MiB虽可省实际占用，却在现有profile前后差中抵消，不能承诺增KV，也无热路径工作可删；full hidden缩寿命无兑现依据。PP动态chunk只适用多级流水，MTP异步计数只适用spec，当前均不适用。queue2已一批lookahead，queue3会触及buffer/placeholder/EOS/KV释放，缺可归因CPU空泡证据；不盲改、不为这些追加上卡。原agent交接保留依据。
- **有限准入源码**：`archive/ai/20261022-framework-kv/finite-growth-admission/`。helper8f564、footerbcf83、preparered587、launcher58d4经过独立新增差分审阅；原QGQA414→415只改init与新增helper，runnercc442/算术不变。只对全新、无APC的WAITING计算首合法max完成窗口；完整输入及issued/placeholder保留，复用原predictor/分配/FCFS回退，每次重算，不预借未来释放、不承诺通用零抢占。同Engine真实N30/H791/free1664<demand2559延期。
- **四轮服务**：193302旧基线169.797007s（DB529稳定）；194020冷候选175.720694s（DB529/19769→532/19839）；194634同源warm168.133490s（DB532稳定）；195213新DB基线169.815742s（DB532稳定）。逐包470/479/479/470原件全核、全部源与清理通过。冷轮旧DB行保留，仅新增3表70行；不拿首次调优的慢结果断言策略无效，不把warm表观正信号当确定收益。[方法记录](team/methods/finite-growth-admission.md)
- **191047准入观察**：477原件全核，7个事件覆盖准入、KV不足与恢复；离线有限预算可放行第30条、暂缓第31条。该轮保留328早期输出，恢复重算13672tokens；延迟准入的尾部并发与prefill搬迁必须一并计算。[观察分析](analysis/finite-admission-observation.json)
- **192308恢复诊断**：481原件全核，native valid、7步目标13760tokens、3696 kernels，首末跨度2.85552s。其中2D 1.58720s、GEMM0.77666s、同批GQA0.32210s，不能全归victim。hist端点只给CPU cadence参考，N1尾段含drain，不能作N1/N2因果增量。两诊断32/0、DB529稳定，不作性能基线；资产在 `archive/ai/20261022-framework-kv/q-gqa-resume-native/`。
- **组合准确率184819通过**：Math500 Level3为101/105（96.1905%），105成功、0传输错误、0输出到cap、无空答案；289原件全核、原35d脚本/参数和414源码不变、实际Q/GQA同execute均增加42次。该准确率属于已有框架兼容组合，不覆盖新有限准入。[准确率审阅](experiments/accuracy/20261022T184819Z-q-gqa-framework/accuracy-review.json)
- 已有183552→184141 Q+GQA服务pair同KV521936、DB527四端三SHA及21项可比门通过，单pair吞吐+7.466632%，独立组合准确率现已通过；不升级成稳定统计或完整官方性能。[分析](analysis/q-gqa-service-pair.json)
- 最新远端调优DB为532表19839行：物理9d9f2360、schema15e23e15、logicala3970aab（全SHA在各control）。之前527/529轮保持其历史结论；新对照不得混用旧DB基线。

## 本阶段结果

- **公共前缀扫描**：173203观察确认128次N1累计CPU10.453319ms；174402 skip/174712基线分别KV521840/521936，虽然表观吞吐+0.201392%，条件不完全匹配，未认性能收益。三轮460/460/459原件已核，保留机制候选，未有官方准确率。[分析](analysis/prefix-skip-service-pair.json)
- **CPU输出记账**：180643候选、181134基线均64请求成功/0失败，真实N63/M63 sample路径激活，源仅runner+helper。KV521936/521840失配，表观吞吐+0.058650%、TPOT略慢，不认稳定或因果收益；458/457原件已核。原事件、快照和history保留。[分析](analysis/async-bookkeeping-service-pair.json)
- **BQ16七段链**：181739原C2/C3上严格输出bits、完整KV、RNG、侧流及padding共25项通过，32ABBA每窗无throttle，wall60.169030→60.023055ms，局部省0.2426%。两种几何均7步/相同绝对输入，尚不是调度实现或模型准确率。窄恢复窗口条件折算整轮仅约0.003–0.004%，且普通调度余数可能形成新prefill；保留局部正信号，不接scheduler。
- **既有Q-hoist**：153947/154518可比短服务单轮吞吐+1.71126%、TTFT略退化；155446 Math500 Level3为101/105（96.1905%），通过95%门。准确率仅属于该源码，不能移给Q+GQA组合。

## 代码与复现边界

- clean6f完整412源远端：`/workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z`；runner `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141`。
- [队友GQA PR #12](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/12)只读固定head `cf1f44876e6cf9e16e8e53f160d630972e535109`，helper `1a81409ba23a149081f7fc257460ea1512cbfdceeb0af32a2698994958749b9a`，runner `cc7f834d25ccbe5d839a731b8e9aa8bf7533bea6f2f937c394423b3844842dfe`。队友性能报告未由root逐raw核验。C3动态统一入口已覆盖GQA，不存在需要另修的漏路由。
- 本阶段仅本地保存，未更新GitHub。`f0ad34a` 已保存上一阶段组合准确率、两轮诊断、四轮有限准入服务共3145份原件；`a7516731` 追加两次启动诊断927份原件及中文结论，`31f828f9` 保存运行中官方进度和单H2D方法资产；本次追加后继服务接线。实验总表170条、167个run。用户本轮所贴规则限定现有GitHub只读，本阶段按此执行。
- 原服务参数、benchmark和MiniCPM5-2B不变；不启用量化/推测解码，不升级框架。启动、清理和封包工具沿用已有脚本；不重新验证未变的旧部分。

## 接续入口

[实验总表](team/experiments.md)由`experiments/registry.csv`生成；更新命令`python scripts/build_team_view.py`。原件在`experiments/framework/`、`experiments/accuracy/`，每轮control内保存命令、源码、环境和封包清单。

子智能体只CPU并行准备，最新短交接分别在[framework](docs/agent-work/framework_innovation.md)、[hardware](docs/agent-work/hardware_innovation.md)、[systems](docs/agent-work/systems_innovation.md)。本轮冻结素材在`archive/ai/20261022-framework-kv/`；未冻结工作仍在上述tmp目录。

[截至181739的完整旧接续记录](archive/ai/CURRENT_WORK-through-20261022T181739Z.md)保留所有旧状态与路径；[更早归档入口](archive/README.md)。旧记录中的活动PID/计划以本页与实际进程为准。
