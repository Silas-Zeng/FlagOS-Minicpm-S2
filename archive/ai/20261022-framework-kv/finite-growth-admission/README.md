# 有限 KV 增长准入

在当前 Q+GQA414 基点上，只对全新、无 APC 的 WAITING 请求增加准入判断。依据正在 decode 请求的合法剩余输出上限，计算到下一条完成前的增长窗口；每次尝试都重算，不保存预留账本，不提前借用未来释放的页。完整输入、已发出计算和 placeholder 均纳入预算。原 KV 分配、FCFS 顺序、RUNNING 与抢占逻辑保留。

相对旧全输出预留，191047 的真实准入快照显示有限窗口能多放行第30条，同时暂缓第31条。192308 恢复窗存在约13.7K重复输入计算，但同窗也包含其他请求；延迟准入增加的尾部并发、prefill搬迁及CPU检查成本，均以服务对比判断，不能把整个恢复窗口当作收益。

helper8f564、footerbcf83、preparered587、launcher58d4经独立新增差分审阅。复用旧源码守卫、原predictor及安装机制；只做语法、精确source前缀和未改函数AST检查，没有重跑旧测试。候选414→415仅改init、新增helper，runnercc442及现有算子不变。

原bc51的16K/1024输出/32请求/c64/seed721201短服务，原SERVER不变、关闭profiler。root统一设备：193302为baseline，194020为candidate；准确身份及结果见各run/control。真实生效需同Engine的FIRST_CHECKED/FIRST_DEFERRED与Q/GQA实际调用，不能只看INSTALLED。最终去留见团队方法记录和配对分析；本目录为可复现资产，不声明准确率或稳定收益。
