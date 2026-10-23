# QGQA与既有KV保存/恢复：CPU就绪组合

只准备，不部署/启动设备。root唯一GPU owner；第一轮若批准是原bc51长负载VERIFY1，不是性能pair。此前“停止重启swap”的早判断已撤回：没有找到组合逻辑冲突，旧总收益仅未严格测定；192308目标独占2D约1.5872秒值得实测权衡，但不与构造copy时间直接相减。

固定184141 QGQA414/base-map bf69、runner cc442全部保留。仅原a662 worker第21行与1aff protocol第509行runner整SHA显式改cc442，产物分别2de7802d/91185a23；未知源仍拒，逆换逐byte回旧版本。原异常消息文字e155未为措辞额外改动。其余84be事务、c95线性COPY、a4de scope、818e pitched-SAVE、cpp0a4d和SO9e33完全原字节；RESTORE仍c95，未叠新pitch、selector、finite或单H2D候选。

e043 init只追加旧protocol footer，精确得791c。完整输入414→输出422/map82514a24，仅init和8个新增普通KV文件；不把旧420整树或两个旧manifest覆盖到当前源。preparer全map核原树/资产/产物/原树后态，新路径拒覆盖；只copy/hash，不import候选/Torch/框架，不加载或编译SO。

把本目录的preparer、launcher、两个map及8个KV资产共12个执行输入文件放远端同一独立assets目录；root审阅并确认官方退出/清理、68MiB0%无进程、9031双栈空闲后才可执行：

```bash
bash /path/to/q-gqa-kv-swap/launch_q_gqa_kv_swap.sh
```

固定base `/workspace/experiments/minicpm-s2/code/q-gqa-service-candidate-20261022T184141Z`，不接受负载/算法参数覆盖。原bc51 `--context-long-screen --seed 721201`，16K输入/1024输出/32请求/c64与原SERVER保持；显式VERIFY1与finiteunset，每run独立绝对Qartifact目录。沿原driver单锁/PID/monitor/cleanup，不新建controller/第二GPU owner；full source、命令、DB-before归档兼容原 `scripts/seal_framework_screen.py <run-id>` 补DB-after/live/post。

安装marker只是预检。首轮必须实际同事务SAVE→FULL→DROP、两组42层源/目的完整字节通过、0ZERO、动态安全R/页/bytes/调用几何与stream、runner六checks/原消费者及host释放，并见当前Q/GQA真实成功execute路径、32/0与原tokens/完整source/DB/KV/清理。旧Q/GQA准确率与旧42byte不冒充新组合结果；Q/GQA graph replay Python计数不覆盖所有step。单并发host slot在DROP后可复用，不是Engine终生只SAVE一次。

VERIFY1含回读，不以时长计算收益。只有首组合字节/消费通过后root才决定VERIFY0单pair；那时完整source声明、原args/包/host条件、DB四端与实际KV匹配才可归因，不凑容量、不自动重复。本目录没有VERIFY0或accuracy自动入口。

冻结pins：preparer `6d09374054f2ae1df54f7dc9fceb5e221eae3f8b39bcbaf5a93c0500c5181cc4`；launcher `1bd16b321ae7d1d11e105f7c0e3ed19e3712afb059b1989a5974556872d8e03e`。完整资产身份与两处diff见identity-delta.json及static-check.json。CPU仅内存compile/byte逆回/完整map/两个heredoc compile/bash-n；没有preparer main/整树copy/旧suite/新mock/设备/SSH。hardware新增差分审阅无阻断；12个执行输入已上传独立远端目录并逐SHA核对。尚未启动，须等官方任务结束清理。

## 首轮收齐原件后的最短判读

```powershell
python -B -X utf8 tmp/q-gqa-kv-swap/review_verify1.py <实际UTC-q-gqa-kv-swap-verify1-context16k-long> --output analysis/q-gqa-kv-swap-verify1.json
```

入口复用固定2071原raw/事务段，不改FULL/ACK/顺序/六checks/consumer/host释放条件；raw仅runner和422身份适配，SAVE原线性计数改用冻结818e纯整数plan核实际linear/pitched/fallback总数。补固定422 map/接线pin、SAVE源42全字节与原FULL目的42、同Engine Q/GQA实际返回标记。实际R由命令prefix_tokens读取；其安全计算受84be/原队列/device fence约束，raw没有完整issued/queued/known，所以不伪称独立重算上界。缺原件/条件失败不写通过JSON。尚未运行任何run的该入口；不替代root原seal核验。reader SHA：6807e3ae75fd5e565f5a4f16502b81cfc57f3e0551c088fa35491a834a93ab56.

VERIFY1通过后若root决定单pair，直接复用已封存候选422源码与固定基线414，分别新建原control/source-map/plugin-source/DB-before段和独立Qartifact目录；不重新构造worker或控制器。末端仍为原bc51命令，仅每侧ENV明确VERIFY0，finiteunset，候选marker=KV_PROTOCOL_INSTALLED、基线marker=Q_FRAGMENT_SERVICE_INSTALLED：

```bash
env -u BIV150_FINITE_GROWTH_ADMISSION BIV150_KV_VERIFY_RESTORE=0 BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR="$control/q-hoist-artifacts" python3 /workspace/experiments/minicpm-s2/scripts/run_framework_screen.py "$run" --source-dir "$source_dir" --context-long-screen --seed 721201 --require-log-marker "$marker"
```

每侧各自结束再原sealer，root显式串行；当前固定VERIFY1 launcher不能用外部ENV覆盖成VERIFY0。未来pair须同原args/包/CPUhost条件、DB四端三SHA与实际KV匹配，并记录真实SAVE/FULL/consumer；新组合准确率仍单列，不能用诊断或旧源算gain。不自动追加pair，本段是接续命令方案。
