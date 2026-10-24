# 临界准入的稀疏 CPU 观察

仅 BI-V150、本轮已冻结 Q+GQA 414 源；未部署、没有新性能或准确率结论。原 230548 只有首次分配失败，165525 只有恢复窗口，不能补出 N29→30→31 准入前的 APC 与页预算。旧全输出 reserve 已消除抢占但无吞吐正信号；当前先观察，不实现 reserve。

exact df780 `Scheduler.schedule` 仅插四个观察调用：WAITING 原 allocate 前、返回后、原 status/computed 更新后的实际准入、RUNNING 首次分配失败。原表达式、参数、返回、异常与队列更新不改；首次 EngineCore step 核自然加载的 Q+GQA/Async/UniProc 后仅绑定该 scheduler 实例。框架负责人已审设计及最终916e/5127/2a2b/3b03新增接线，无当前诊断阻断；其额外静态检查确认剔除四callback后完整schedule AST相同，没有模拟框架执行或设备验证。

N>=29，按 `(request_id,num_preemptions,status)` 保存首 attempt 与首次成功准入，最多 8 个 key、4096 次临时采集；成功前重试只复制 O(N) CPU 标量/列表长度，避免把成功后的状态伪作 before。无逐步日志、无页内容/页表遍历、无 Future 查询、无 CUDA 调用。记录真实 max_tokens、known/computed/placeholder、当前 scheduled 与已排队 SchedulerOutput、free/owned/cached 计数及原 APC 结果。after-admission 尚未执行 `_update_after_schedule`，两阶段明确分开。owned 是逻辑数量，不冒充唯一可释放页；EOS 与 GPU 完成前缀未知。

观察开销不能用于性能比较。最短设备任务仍由 root 执行原 `--context-long-screen`、16K/1024/32 请求及原 seed/SERVER，无 profiler；先验收真实准入事件与失败事件，再判断有限完成窗口是否比旧全 reserve 少延后。不因一次预算反事实承诺能消除重算，也不将恢复全窗口归于 victim。

五部署件为 helper、`observer_init_footer.py`、`prepare_admission_observer.py`、`base-source-sha256.json`、`launch_admission_observer.sh`。后者接收原414副本目录一个参数：

```bash
bash launch_admission_observer.sh /workspace/experiments/minicpm-s2/code/q-gqa-service-candidate-20261022T184141Z
```

准备器只创建新415副本，改init并新增helper；runner仍为 `cc442e54`，Q/GQA原件不变。`cpu-preparation.json` 保存全部精确SHA：helper `916e842e`、prepare `2a2b2a33`、launcher `3b03622e`；已核四锚逆回、源码编译、init与声明路径，Bash语法通过，没有整source复制、动态mock或GPU。`prefill_context_parallel_size` 资格复用112603实际五并行guard通过的原件。启动HOOKED/ARMED不是有效观测证明；后续须查同Engine PID的实际准入事件及原始请求完成/清理，缺失记录或观察disabled均保留为局限，不自动算通过。
