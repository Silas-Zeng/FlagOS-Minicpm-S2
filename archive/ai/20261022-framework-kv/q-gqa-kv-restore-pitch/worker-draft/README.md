# FULL-only H2D worker增量草稿

未部署、不可运行。基点为当前422的worker2de7802d，草稿9f178a70；RESTORE_BRIDGE=None，必须在新桥实际单层字节门通过、得到实际SO hash并另行审阅锁定后才可能接入。旧422/8资产均未改，不继承其accuracy或净益。

精确差异见worker.diff：只在原rpc的kind==RESTORE_FULL处把H2D提交换_restore_pitched；旧RESTORE仍原c95f，SAVE原字节不动。原_full_restore_plan、目的页绑定、producer fence、同流真_finish、c95f逐层VERIFY回读、状态机和原except/finally保持。新helper不决定fresh/ref1/覆盖或发布资格。

新运行时a7439c2c显式复用slot已持有的818e；新桥单独命名biv150_kv_pitched_restore_bridge.so，不能替换原SAVE的9e33。runtime/bridge先于maxpitch持于slot，plan/prepared/currentstream在首native submit前均入slot；PreparedRestore再持完整host/raw/descriptor。submit返回不是ACK，任何异常含submitted_calls=0也由原rpc真实全卡settle，未settle保refs且不发布，不catch后重试旧COPY。两侧SO的loaded libcudart仍只允许原d39，新增载入/文件hash/plan/maxpitch成本留在真实FULL路径，不挪到启动profile。

当前风险是尚无真实新SO/单层H2D/42层提交证据；大batch descriptor和两库载入/首次校验的实际开销未知。FULL原覆盖校验会先执行，新prepare更严的storage-range无alias条件可能拒绝而不能降级；发生错误沿原事务settled回滚。旧异常submitted布尔仍表示原rpc进入可能提交区，不冒充新native实际提交数量（新异常文本自带计数）。未先宣称calls减少即收益。

最短后继思路（仅计划）：硬件独立单层门通过及root锁实际SO后，固定已验422仅替本worker并附a743/helper、4829/cpp和新SO，完整map另存；原bc51长负载/seed/SERVER/Qartifact环境/finiteunset及VERIFY1保持，不加新fixture或controller。必须再次实际FULL新实现/当前stream/动态几何/真event、0ZERO、SAVE源42和原c95f FULL目的42字节、runner六checks/consumer/host释放/QGQA/32-0后才有组合正确性；诊断时长不算gain，后续净益与accuracy另由root决定。

team_view_final_check已只读新增接线，无当前草稿机制阻断，明确None pin不可部署；没有跑旧合同/设备。static-check仅compile/旧函数byte同/逆回/except-finally AST核，没有Tensor/native mock或新suite。


425源/VERIFY1薄接线CPU准备已冻结：prepare_restore_worker_source.py f29f23e7，launch_restore_worker_verify1.sh 352bc6b2，base-source-sha256.json为原82514／422完整map。模板worker仍9f178a70且RESTORE_BRIDGE=None；绝不直接部署模板。preparer只接受显式原H2D门目录，核原完整seal的全部文件集合/SHA/bytes、已审ed733 controller和10e5 gate、实际源前后map/结果与SO一致、10项字节/guard/流检查、RNG和结束idle。实际PASS后仅将None精确替为该SO hash，再从冻结422构建425：只替worker，新增restore helper/cpp/独立SO，init/protocol/SAVE/runner等其余字节不动。输出完整map及差分/原门身份保外置receipt，不向source加manifest扩大计数。

最短后继命令（仅供root，尚未执行）：
```bash
bash launch_restore_worker_verify1.sh /workspace/experiments/minicpm-s2/framework/<实际PASS的UTC>-kv-pitched-restore-gate
```
所需上传仅本目录preparer、launcher、9f worker模板及82514 map；新helper/cpp/SO全部从已封存单层门取。原bc51长负载/seed/SERVER/VERIFY1/Qartifact绝对ENV/finiteunset和原DBbefore/PID尾段保留，原driver是唯一设备owner、原sealer字段兼容；不自动pair。若原gate目录事后新增未索引文件，完整集合检查会拒绝，不能删除/改原seal绕过。此时由root决定使用原未改目录或另审导入证据。

仅compile、两段heredoc、bash-n与map/变换结构静态核过，wrapper-check.json有边界；未执行builder/整源copy/门原件核验/库编译加载/设备。尚无本新SO、单层PASS或425事务证据；原review_verify1.py6c5f的422源及FULL线性calls门不能原样冒充新425验收，后续须只适配新425身份与新helper动态FULL几何，保其余ACK/两组42byte/runner消费条件。新425的净益和accuracy均待root决定，不能继承422资格。


root已告知独立H2D222047 PASS，实际新SO为f9bf8757…，并以本builder锁出425 worker924f538c…启动222222 VERIFY1；这是后继真实状态，前述“无SO”是草稿冻结时点。当前425 VERIFY1仍在途，不能把422 accuracy215836的103/105继承给425；该accuracy还令DB540→544，后续仅比较共同新DB。

VERIFY0薄启动稿：launch_restore_worker_verify0.sh 5c1542d3，425完整freeze map restore-source-sha256.json fb8b8672；基线固定213134原422，候选固定222222新425。不新增owner/编译/源变换/observer，原f5ea的QENV/VERIFY0/finiteunset/bc51 long32/seed721201/PID尾段逐字节保留。CLI如下，两侧各由root单次调用，不自动pair：
```bash
bash launch_restore_worker_verify0.sh baseline /absolute/path/to/passed-425-review.json
bash launch_restore_worker_verify0.sh candidate /absolute/path/to/passed-425-review.json /workspace/experiments/minicpm-s2/framework/<本轮已完成baseline>-control
```
报告为独立review_restore_verify1.py真实通过输出，root需在远端提供该文件；启动稿核PASS状态、222222 run、425 source_manifest SHA与实际f9bf SO，不能用只有exit0/INSTALLED的JSON替代。两侧都拒绝尚未完成的222222。候选另外核本轮baseline完成/源422/后态，且其DBbefore=after=候选before三SHA相同才启动；不恢复DB、不凑KV。候选after与实际KV/环境/32-0/无回读/协议和消费等仍由原配对reader后验，不能把预检称配对已过。源完整live/archive/map及四份原source附证沿原sealer保存。只做3段heredoc compile、bash-n、4路径map及原尾段同字节静态检查，无启动/快照/整copy/旧suite。新稿交hardware增量互审。


root已实际d45验收222222 PASS（R16704/1044页、FULL672为本轮动态16段、SAVE210、consumer8、32/0、DB544稳）；这只是VERIFY1正确性，不是净益。VERIFY0 baseline223056正由root串行执行。最小配对reader位于上级compare_restore_verify0_pair.py b3298755：沿旧5c0公共20可比门，baseline422／candidate425完整map，仅worker+3restore路径；两侧都须实际SAVE/FULL/DROP、真ACK/runner六checks/consumer/host释放且无回读。基线FULL保持原linear计数，候选复用d45实际目的页/maxpitch整数planner，仅回读断言切为0，无固定672/页/R；SAVE仍各自按818e完整实际几何。Windows深路径保extended ROOT，SQLite指纹入口沿d45去prefix但要求绝对且<260，继续原0f2只读指纹算法。原参数/包/CPUquota/GPU/DB四端/KV任何不齐都gain=null；单pair只能正负信号，不能称稳定或425 accuracy。
```powershell
python -B tmp/q-gqa-kv-restore-pitch/compare_restore_verify0_pair.py --baseline-run 20261022T223056Z-q-gqa-kv-restore-pitched-verify0-baseline-context16k-long --candidate-run <实际候选run> --output analysis/q-gqa-kv-restore-pitched-verify0-pair.json
```
新reader只语法与既有函数definitions适配构建，未load_arm/read raw/查DB/运行旧suite；静态receipt和相对5c0 diff在上级。root实际原件到齐后唯一运行，hardware仅新增差分互审。
