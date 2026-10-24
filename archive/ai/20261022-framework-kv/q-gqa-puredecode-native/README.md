# 当前422纯decode窄窗口诊断

已部署并排队，尚未运行。root唯一设备owner；队列`/workspace/experiments/minicpm-s2/queues/20261022T235007Z-after-official`（PID387488、queue4f020e5b）23:56为waiting_official。先等待231746官方exit0与owner退出，再原d9a363ee封存通过后唯一派发；失败停止、不自动重试。不得手工重复启动，先读state.json与diagnostic-launch.stdout；派发后记录失败不代表未启动。沿192308原native owner、longscreen（16K输入/1024输出/32请求/c64）、seed721201和SERVER，不改benchmark、负载或策略。仅固定422 init追加独立helper，runner cc442与原KV协议逐字节保持；VERIFY0、finite unset、独立Q artifact目录。部署六件见`preparation-check.json`，入口`bash launch_puredecode_native.sh`。

先观察两次同请求ID/顺序、N≥16、M=N且全q1、无new/resume/preempt/finished/spec/structured变化；第三次开启唯一8步窗口。各步记录原execute与原sample_tokens的CPU前后端点，第9次execute入口先按旧门边界sync/ProfilerStop再原调用。中途失稳只记`incomplete/mixed_abort`，不寻找另一个窗口。waiting不读取、不声称为0。首两步受开始边界排空queue2影响，尾部受停止边界影响；无逐步新增GPU同步，不把CPU返回当GPU完成或诊断吞吐当性能。

实例观察器可能持有已disabled的原Q execute闭包，保持其既有返回/异常行为，不强拆已验Q绑定。CPU端点含薄实例/disabled-Q观察层成本；即使出现间隔，也不能将其精确全归原生产host开销。

042609现成原件已有5条独立GPU `cuda_graph`，与5条`cudaGraphLaunch`按pid/correlationId对应；它与192308都有MONOTONIC `clock_snapshot`（旧样本offset分别280–573ns、135–641ns）。新原件须重新核时钟、相关图区间及边界，不预设8个CPU步就有8个完整GPU区间。只分析内侧graph之间的可见API、kernel、memcpy等；graph间隔包含sampler/metadata，不直接称GPU idle。既有读取器由hardware独立准备，不展开graph内核。

附带CPU mixed覆盖复用旧29137的query offsets与原C3 plan读法，冷核单attention-group/Triton后只取首metadata；真实execute首build计数。active8步及普通q1直接跳过offset扫描；其余每64次execute保存partial，shutdown若发生另存末次。直方图为N/M/q1总数/q1连续前缀/前缀外/plan.prefix_tokens，q1不保证已生成decode，plan不证明forward，unsupported/多build/观察错误均计数。shutdown缺失只承认partial。本long1024单波没有遗漏不能否定旧128out或官方多波负载的机会。

只做新增源码/字段/kwargs/层叠/恢复的静态核查与compile，不跑旧suite、框架mock、设备或完整源码复制。原件封存继续使用native-events.jsonl、native-validation.json、control/source-sha256.json和DB前后接口；结束后的退出/清理与完整证据由root验收。

framework对最终637550a0/f88182a2/4fc1ae7e/a634ea7d新增块只读互审通过；team对queue4f020e5b窄审通过。离线graph/clock reader93e310bb已冻结并互审，CLI `python read_puredecode_native.py --run-dir <run ID或绝对路径> --output <新JSON>`，尚未执行。仅syntax/help，不重跑旧分析。诊断实际有效性仍待原件。执行文件以tmp路径为准；归档副本供接续与查阅，涉及parents[2]的工具不能直接移位执行。

`cudagraph_dispatcher-reference.py`仅为当前installed `/usr/local/lib/python3.12/site-packages/vllm/v1/cudagraph_dispatcher.py`的只读SCP副本（SHA51f63275），供下一候选核启用条件；不属于诊断部署资产，不导入或更改原框架。

另用`summarize_mixed_coverage.py --run-dir <本地run目录> --output <新JSON>`提取最后累计coverage，SHA cf551ca3，已静态互审、尚未读数据。输出N/M/q1/前缀/遗漏/plan频次及partial/unsupported边界，无样本比例为null；不是forward或收益。与graph reader分开输出，不重复计算旧实验。
