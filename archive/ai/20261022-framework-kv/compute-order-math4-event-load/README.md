# 原四题的事件到达客户端

本包仅编排一次质量诊断，不是优化、性能对照或105题准确率门。原32背景一次生成、一次原CLI执行，前2与尾30保留各自原payload、seed721201、采样参数和请求身份，不拆两次CLI。

- `run_math4_event_load.py`：先启动原四题客户端，等4次原generate入口预热就绪，再启动背景；同一210秒期限包含预热、事件等待和生成。
- `warm_capture_evalscope.py`：薄包装实际generate/generate_async，在原函数前等`math4-go.json`；原capture9e1、completion_params、response、题目、judge均不改。实际adapter的generate_async不调用generate，源码检查已记录；4并发能否实际就绪尚未执行，失败仅inconclusive。
- `gate_benchmark_requests.py`：包装实际benchmark与原request函数；原endpoint ready check不门控，32个实际背景中只尾30等待observer的`release-background-tail.json`。无新增HTTP客户端、模型调用或重试。

调用沿原load接口：

```sh
python3 run_math4_event_load.py --run-dir RUN/context-16k \
  --capture /absolute/capture_evalscope.py --capture-output CONTROL/math4-client --seed 721201
```

服务启动前必须由root新建空`CONTROL/events`，并设置`BIV150_COMPUTE_ORDER_MATH4_EVENT_DIR=CONTROL/events`、原`BIV150_COMPUTE_ORDER_MATH4_DIR=CONTROL/math4-artifacts`。本包不创建新owner；root沿原bc51/4552的SERVER、锁、240秒外期限与清理接线。两自有进程组finally TERM/KILL；最坏约210+20秒，原期限不加长。

身份信号`background-request-ids.json`严格只有`engine_input_request_ids`一字段。完整32请求的原SampleRequest及SHA、header ID、顶层`cmpl-header`、子请求`cmpl-header-0`与该信号SHA保存在`benchmark-original-requests.json`；observer再以子请求加8hex严格关联真实EngineRID。来源为实际serve b09e85、endpoint5fd4b6及completion serving582b86两份已归档ID链证据。两observer信号必须同PID/config SHA；`observer-error.json`、`uncovered.json`、超时或进程失败均停止，不改变到达时序重试。

`cpu-preparation.json`只记录新文件语法、原argv/参数名和原adapter AST检查；未导入框架、运行客户端/设备或验证四题覆盖。进程exit0仍仅`processes_completed_requires_report_review`，原题身份、judge、实际outside发生在答案前及token关联仍须本轮原件后验。
