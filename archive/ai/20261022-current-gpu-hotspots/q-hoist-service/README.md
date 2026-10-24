# Q fragment 服务接线：先判真实白名单覆盖

本目录仅接入原6f组合，不叠C3views、hot-key、gather或其他新策略。helper由硬件职责owner维护；其私有JIT保原完整native binder/options/hooks/current stream，只在原正常编译TTGIR恰为已验ff6456时应用同一Q local_load外提。未知2D返回原正常compiled，最多保留8份原IR/编译元信息；不能据此扩大IR白名单。

原runner构造成功后，严格MiniCPM5-2B BF16、TP/PP/DCP/DP1、无spec/LoRA/ubatching、FULL_DECODE_ONLY范围才安装。`service_append.py`是**4空格缩进的runner末尾片段**，只编译完整拼接runner，不单独导入。真实`execute_model`返回后，候选launch累计增量>0且N>=2才输出一次`BIV150_Q_FRAGMENT_SERVICE_FIRST_ACTUAL_EXECUTE_SELECTED`并撤掉该观察器；单请求smoke和dummy不能冒充服务命中。原方法返回不代表额外GPU完成ACK，单条marker不代表全程覆盖。

完整基点map来自原174402的410文件，精确叠加已验6f runner及两个helper为412，与100830原归档map逐字典相同。输出仅替换runner并加入一个Q-hoist helper，完整413文件前后核验及原基点不变；不接受任意同runner但其他文件漂移的树。`prepare_q_hoist_service.py`最终已锁helper／append／map三SHA，未匹配则拒绝部署。

新增接线CPU合同`check_service_cpu.py`只运行一次13项通过：原ctor/execute恰一次、返回和异常context透传、日志/观察失败退出、smoke不作screen证据、原6f字节逆回。它使用CPU替身，不证明实际compiler/ABI/设备/数值。没有执行整source复制、旧套件、SSH或GPU。Bash语法通过。team已只读三个模板及helper封口无当前短门阻断；root按最短验证原则决定不等复杂mock，`check_compile_cpu.py`仅为**未完成、未执行的草稿**，没有对应通过receipt，不能把它当证据。原135941已验变换核心，新服务接口由实际短门验证。

部署需同目录五件：`launch_q_hoist_service.sh`、`prepare_q_hoist_service.py`、`service_append.py`、`base-source-sha256.json`、`biv150_q_fragment_service.py`。root唯一设备owner串行执行：

```bash
bash <assets>/launch_q_hoist_service.sh /workspace/experiments/minicpm-s2/code/cpu-combination-combined-20261022T100830Z
python3 /workspace/experiments/minicpm-s2/scripts/seal_framework_screen.py <run-id>
```

沿原bc51 `--decode-screen --seed 721201`（64请求、4K输入、128输出、原SERVER），不加profiler、不自动baseline或重复。原driver只要求安装marker；后验另查Engine PID实际selected marker、cold recipe及`q-hoist-artifacts/<pid>/`原件，atexit summary尽力写入而非完整必达。0命中须保留为覆盖否定，不据本轮总耗时宣称性能。后续若需收益对照，再由root确认同参数、DB四端三SHA、实际KV容量和主机环境；不拿135941局部门20%外推服务。

最终冻结：helper `77b489a8ed0d306558405152f94ae4c19cbc2d7132b11a56d0b9610f6e729a6d`；preparer `8c6b687b651bea5b768120af31dbf7789e9b5058d8180e099898d5bbceb73a49`；launcher `d3159dab797d45a35e056c638d51be9f06dab6e91e382cf77edfa76b31249839`。append `409e4896…`，candidate runner `06c69f83…`，完整412基点map `44355588…`，接线CPU receipt `b9c0321a…`。五素材全SHA见`wrapper-check.json`。最后helper必要小修仅把已launch后的计数／资源观察包为best-effort，None或观察异常保原return、不重试；framework已定向读过该差分，不再重复旧合同。

114435旧native轨迹未关联真实stride/ABI/IR；缓存存在本身不能证明服务命中。后续153947真实服务已出现单步42层命中，与154518基线同KV/DB，短吞吐+1.71126%、TTFT+1.3185%、TPOT−5.3841%，仅一次配对信号。155446完整官方Math500 Level 3为101/105（96.1905%），1题到输出上限，通过95%门；关闭阶段EngineDeadError/ResourceWarning原样保留。原件、精确代码与结果入口见[方法记录](../../../../team/methods/q-fragment-hoist.md)。当前冻结此候选供算子队友接续，不再扩IR白名单；root转框架/KV调度。
