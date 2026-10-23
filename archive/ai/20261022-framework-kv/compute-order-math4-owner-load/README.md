# 原题四条混合诊断负载

仅候选423诊断，替换原 bc51 的一次 load：同一服务执行原 `run_diagnostic_load.sh` 的 32×16384 输入、128 输出、并发 64、seed721201 背景，及原 6e045 EvalScope Math500 Level 3 命令加 `--limit 4`。背景先启动，只在本轮 `server.log` 新增 `FIRST_SELECTED` 后启动 EvalScope；不靠两个客户端的 import 延迟碰运气。原 batch8、temperature1、top_p0.95、max_tokens32768、judge 与 HTTP timeout3600 保留；不改原官方脚本或105题验收器，不把本轮用时当性能结果。

`run_math4_load.py` 从已锁原脚本文本提取 argv；不实现 HTTP client、加载模型或控制服务。capture 使用 framework 作者提供的 `capture_evalscope.py --output DIR -- eval <原参数+limit4>`，仅旁存原请求/响应。两条命令各启动一次，无编排重试；210秒总期限包含等待和客户端初始化，未完成记 `timeout_inconclusive`，背景先退出则 `uncovered_inconclusive`。finally 终止并等待仅本次创建的两个进程组。命令、PID、返回码及失败写入 `RUN/context-16k/math4-load-summary.json`；exit0只表示进程完成，四题身份须按原预测 metadata.question_id 对照原105题 index0..3，判分和实际答案前计算序覆盖另审原件。capture晚到而未覆盖也不调时序重试。

部署接口（仅root安排运行）：

```sh
export BIV150_COMPUTE_ORDER_MATH4_DIR="$control/math4-artifacts"
python3 "$assets/run_math4_gate.py" "$run" --source-dir "$source" \
  --context-screen --seed 721201 --require-log-marker BIV150_KV_PROTOCOL_INSTALLED \
  --math4-capture "$capture_assets/capture_evalscope.py" \
  --math4-capture-output "$control/math4-client"
```

`prepare_owner.py` 只在原 parser 和唯一 load 命令两处转换，逐字节逆回检查与 `owner.diff/owner-check.json` 留在本目录。原 SERVER、单锁、smoke、监控、240秒 load 外层超时及服务清理均不改。load `03a0c902…`、owner `4552fb7f…`、capture `9e1f6bcf…` 已锁；当前只完成源码 syntax/argv、两切口逆回检查和新增逻辑跨职责只读审阅，未执行负载、HTTP、模型或设备。背景原结果位于 `context-16k/background/`，EvalScope work-dir 为 `context-16k/math500-level3/`；本目录不新增性能或105题验收器。
