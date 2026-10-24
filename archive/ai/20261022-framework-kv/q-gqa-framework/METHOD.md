# Q-hoist 与 GQA 框架兼容组合

原顺序C2→C3→GQA在模块加载时安装；Q于runner构造成功后接入。Q旧guard要求unified globals属于Attention，因GQA wrapper而拒绝；本候选仅增加exact已loaded GQA源码/函数/闭包身份校验，不改统一入口绑定、两operator算术、调度或服务参数。未知包装仍拒，prefill原fallback动态进入Q2D，decode继续GQA。

基线183552为队友PR12 cf1f448 exact GQA1a814、runnercc7f，413文件；候选184141为Qhelper51fc＋薄观察，runnercc442，414文件。原16K输入/1024输出/32请求/c64、seed721201、bc51driver和SERVER不变。

两臂32成功0失败，同KV521936及DB四端527表19702行三SHA；root复用逐460/478seal核验，参数化compare21项全真。182.460600→169.783491s，总吞吐3053.020761→3280.978592tok/s（+7.466632%），TTFT−9.416976%、TPOT−6.786409%。这是一个单pair正信号，不是稳定统计或完整官方成绩。

候选Engine339894 execute43 N2/M2048成功返回后，Q/GQA计数均增42并各写一条实际marker，随后撤观察。Python计数不覆盖graph replay，成功execute返回不是新增GPU完成ACK；基线原PR12无新观察器，FIRST_WIDTH只证明尝试。组合准确率184819现已独立PASS101/105，105 success、0传输失败／0cap／无空答案；不继承两单项结果。

原件：`experiments/framework/20261022T183552Z-q-gqa-service-baseline-context16k-long{,-control}`与`20261022T184141Z-q-gqa-service-candidate-context16k-long{,-control}`；配对结果为`analysis/q-gqa-service-pair.json`。这里仅冻结小素材与清单，不重复完整源树。

若离线复现比较，将本目录素材恢复至`tmp/q-gqa-framework/`原布局再调用compare_service_pair.py的两run参数。accuracylauncher使用已有35d原driver/原official脚本与已测414源，只给Q日志目录及安装marker；该组合准确率现已通过；它不扩大原单pair性能的统计范围。

准确率原件：`experiments/accuracy/20261022T184819Z-q-gqa-framework/`，root逐289seal验收复用；Engine341334 execute2 N8/M376双delta42，19:10:03 UTC退出0及414 live/archive与cleanup通过、KV521936。调优DB由527表19702行增长至529表19769行，after物理9ca232／schema9535／logical552d；不得称DB稳定，后续不能把旧527性能轮直接当529基线。
