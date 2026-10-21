# 原版official结束时的必要取证清单

2026-10-21，仅现有任务收尾。只读核对`compare_official_runs.py`最终e9dc与原791 driver/35d3 common、0f2a DB helper，未改脚本或运行模型/远端命令。最新root14:47Z回执6raw/1summary，16K第二轮128请求成功/2585.11s并开始3/4，bab2正确；下列是待结束时的合同，**不是已完成结果**。

run为`/workspace/experiments/minicpm-s2/official/20261021T122607Z-original-baseline`，control为同路径加`-control`。用户已冻结全部未开始探索；收尾不触发新设备验证或retained/C3 import。

## 原791会自动产生的文件与关键字段

| 文件/目录（相对run） | 结束后核对内容 |
|---|---|
| `exit-code`、`result.json`、`finished-at.txt` | 三者真正产生；exit-code及result.exit_code=0，status=`official_benchmark_completed`，benchmark_completed=true，benchmark_exit_code=0，cleanup_errors=[]。finished-at等于result.finished_utc。缺结束文件仍pending；失败不能改标完成。 |
| `result.json` | 保留benchmark_started_utc/finished_utc、finished_utc、benchmark/server/monitor_final_returncode、validation、postflight、benchmark_source_after、cpu_after。monitor正常SIGTERM可为−15，不错误要求所有退出码都0；benchmark必须0，owned进程必须最终消失。 |
| `benchmark_results/raw_runs_*.csv`、`summary_*.csv` | 各恰一份且timestamp后缀一致；原8行依次4K四轮/16K四轮，summary恰两行；原请求数/tokens/数值/原2–4均值由现791 validate_outputs校验。保留原首轮位置，不能先过滤失败再挪warmup。额外逐行核原8行SUCCESS/成功数/tokens，若首轮异常也原样记。 |
| `manifest.json`、`benchmark-command.json` | 最终manifest非启动快照；server_command/benchmark_command原CLI，profiler=false、smoke_requests=0、RUNS4/SKIP_FIRST1，benchmark-command逐项一致；完整sha256、packages/Python/Triton/FlagGems身份、source_dir、数据库真实路径、CPU before保留。baseline require_log_marker应为空/无候选marker。 |
| `source/`完整树 | 每个manifest.sha256相对路径都存在且字节SHA一致；原benchmark0813、driver791、common35d3、DB helper0f2a不变。original base13eb、worker446f；installed Attention bab2；无retained module/hook/marker。最终实际数量从final manifest得出，不把startup225项当终审。 |
| `database-before/`和`database-after/` | 每个含原manifest.json及snapshot.sqlite；status=complete，snapshot_sha256/snapshot_bytes、schema_sha256、logical_content_sha256、table_count、row_count及真实SQLite实体齐全。保留各自command JSON/log。取回后只读重算，不清库/不改行/不删Tritoncache；source_data_version不是跨run身份。 |
| `server.log`、`benchmark.log`、`monitor.log`、`gpu.csv` | 原始完整日志/采样不裁剪；实际KV由`GPU KV cache size: … tokens`核唯一值。gpu.csv保留header及全部原行，index0/BI-V150/memory.total=32768MiB，不拿free_mib当总显存。检查是否有异常、重启或候选BIV marker。 |
| `started-at.txt`、server/benchmark.pid、models.json及source脚本 | 实际启动/原endpoint、PID与脚本留档。started-at与manifest.started_utc来自不同utc调用，不强制微秒相等；结束UTC与阶段标签不能混用。 |

原791在finally先停自身benchmark/server/monitor，再snapshot DB-after、调用common.preflight与check_benchmark_source，写final manifest/result/exit/finished，最后释放锁。应等这个流程真实结束再封存，不在5/6/7行时提前复制当final。

固定CPU配额需从两manifest保留并核对`cpu.cfs_quota_us=600000`、`cpu.cfs_period_us=100000`，即**6核quota**，不能拿宿主可见CPU数替代。原版与候选的初始DB实际不同，最终必须分别读两run before/after SQLite与指纹，**不得称cache-matched，也不清库制造匹配**。真实KV必须分别从两份完整server.log读取；不能用相近短测、默认值或总显存推算，候选092944的已审值521936也需引用该run原日志。最终只给两case原2–4轮描述性均值/比率与TTFT差，不合成比赛总分。

## 必须由root额外保存：driver并不自动生成

**1. `run/postflight-full.json`。** e9dc比较入口明确需要此路径，只有control里的文件还不够。原791的`result.postflight`只含端口与free_mib>=30000；它不等于完整idle证据。最低字段为：

```text
utc: 实际最终采样UTC
port_9031_closed: true
memory_used_mib: 实际数值，<=68
gpu_utilization_percent: 0
ixsmi: 完整原始表，含 No running processes found
```

利用率字段也兼容`utilization_gpu_percent`，二者择一真实写入；原query输出可放`query`/`query_raw`，总显存/型号可额外记录。端口核IPv4及可用IPv6；除完整设备进程表外，记root拥有的runner/server/EngineCore/benchmark/monitor实际PID已退出。不能只因9031关或free>=30000就声明卡全空闲。这里只列字段，**本agent不执行远端查询**。

**2. 最终source-review JSON与原字节。** 建议`run-control/final-source-review.json`，另把最后实际Attention字节复制为`run/postflight-sources/triton_unified_attention.py`。不要写进原`source/`或改manifest来掩盖变化。最低字段：

```text
utc / stage=after_driver_cleanup
manifest_sha256 / source_dir
archive_source_count / archive_source_failures=[]
live_source_failures=[]（逐项实际比对已完成时才写空）
installed_attention_path / installed_attention_sha256
archived_attention_sha256 / postflight_attention_copy_sha256
plugin_worker_path / plugin_worker_sha256
benchmark_sha256 / driver_sha256
no_retained_module=true / no_retained_hook=true / no_retained_marker=true
```

Attention三个SHA均须bab2；worker读取manifest.source_dir中的实际worker文件，须446f，不误把其他pip目录当source。benchmark0813/driver791；保留其余live installed依赖与archive的对照失败清单。原版source/日志不应有候选安装/执行marker。检查只用固定已知路径读字节，**不要import vllm/retained/C3，也不要用find_spec导入父包**。

live映射要区别：`plugin/…`对应manifest.source_dir下文件；`installed/…`对应固定site-packages；model config对应MiniCPM目录；benchmark对应原官方benchmark路径；helper/monitor对应ROOT/scripts；dataset对应原本地dataset目录。对不清楚映射的项记录未核，不凭archive哈希合格就称live全通过。

重要边界：e9dc会核归档source，不会替root读取远端live结束后的Attention。791的`benchmark_source_after`只核原benchmark字节/重复常量，也不是Attention after校验。必须保留结束后的bab2证据；先完成这次取证，不能在期间启动/导入候选使其写回54c。

## root的结束后校验与取回顺序

1. 等runner及final exit/result真实结束；先核result成功与原8raw/2summary完整，不对在途片段计算最终gain。
2. 沿既有owner路径完成fullpostflight和final source-review；保留实际命令及UTC、live Attention字节、无残留进程。原版依赖仍bab2；不执行新candidate来“验证恢复”。
3. 保留整run/整control、DB前后实体、完整source和原CSV；恢复record `dependency-restores/20261021T122607Z-original-baseline`已有的备份/独立review也保留。control启动225SHA与progress仅为历史补充，不替代final。
4. 打包后留远端归档SHA256/成员清单，下载完成核本地同SHA与所需成员；不要仅下载summary/result或丢SQLite/source。封存后不要改原件。
5. root确认完整原件本地齐，再交本agent做原有必要终审和e9dc两份真实比较。缺项仍pending、已有失败/身份不符为invalid，不能为了让脚本通过而改原CSV或补假字段。现不重复pending smoke。
6. 验收后更新现有registry行、report两档绝对值与percase meanTPSratio/TTFT差；真实DB/KV/暖机漂移一起报告，不发明总体公式。不恢复探索，GitHub仍只准备材料，推送/对外消息须另有授权。

本清单只保证取证不遗漏，不扩大现有验证范围；代码/官方脚本/默认均未改，也没有提前填写任何baseline成绩。
