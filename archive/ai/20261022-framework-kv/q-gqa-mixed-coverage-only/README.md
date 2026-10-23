本包仅CPU准备，尚未启动。目的为比较原16K/128输出、32请求、c64与002156的1024输出单波在mixed metadata排列上的差别；root须先拿到002156完整覆盖证据，再决定是否上卡。

hardware已完成新增mode与launcher接线只读互审，无阻断；未重复测试或访问设备。当前SSH公钥授权异常，原002156已exit0但完整原件待取；本包未上传，不能据此跳过前置证据或自行启动。

固定422只改init并新增helper，runner cc442和KV协议911逐字节不变。基于原637550a0显式新增`mixed_coverage_only`模式，首次安装任何绑定前核模式白名单；跳过全部profiler资格与起止分支，不安装sample wrapper。没有ixsys或native trace，也没有新增CUDA同步。原mixed计数及每64次execute的partial保存不变。默认native模式保原行为，旧包不改。

五件冻结SHA见cpu-preparation.json。仅精确变换逆回、compile及Bash-n，未运行框架、源copy、模拟套件或设备。launcher直接调用原bc51 `--context-screen --seed 721201`，保原SERVER/单owner/清理、VERIFY0和finiteunset，events与Qartifact使用新目录。当前连接变化不由本任务处理，也不自动排卡。

结果仍使用已有`summarize_mixed_coverage.py`仅读native-events.jsonl；armed应明确`observation_mode=mixed_coverage_only`、`profiler_enabled=false`，不得有start/stop或native trace。末次64步partial不保证整轮覆盖，q1不是确认decode、plan不是forward；无K加权和性能结论。
