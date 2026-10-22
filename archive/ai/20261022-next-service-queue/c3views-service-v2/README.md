# C3views 服务接线 v2：观察失败隔离

仅 CPU 准备，尚未上卡；旧 `../c3views-service/` 完整保留。以本包替代旧包部署，不能混用新 policy 与旧 `service_append.py`。

唯一行为修正：前置计数和后置计数／JSON／print 均属于可失败的观察；原 `execute_model` 恰调用一次且位于观察 try 外。观察失败只禁用观察并撤包装，保留原成功返回、不重试执行或日志；被框架缓存的旧 bound method 也不重试。原模型异常直接传播。成功时仍只记录一个真实 execute 的 selected 增量，随后撤包装。

`check_observer_failure_cpu.py` 仅新增四种失败注入（执行前/后计数、序列化、打印）与原异常透传；一次通过，原包字节未变，回执见 `observer-failure-check.json`。未重跑原 policy 或旧安装合同。原来的完整副本/安装检查复用 `../c3views-service/cpu-check.json`；当前 runner 安装尾、prepare、launcher、checker 均未改。硬件职责 owner 已只读确认新异常边界、身份条件撤包装和缓存 wrapper 不重试，未重跑合同或设备；无当前短服务阻断，ready。

部署文件仍为同目录五个：`launch_c3views_service.sh`、`prepare_c3views_service.py`、`biv150_c3_view_reuse.py`、`service_append.py`、`check_actual_selection.py`。基线为同一干净完整6f源码，root 在单卡空闲时串行调用：

```bash
bash <v2-assets>/launch_c3views_service.sh baseline <完整6f组合source>
bash <v2-assets>/launch_c3views_service.sh candidate <同一完整6f组合source>
python3 <candidate-control>/check_actual_selection.py <candidate-run>
python3 /workspace/experiments/minicpm-s2/scripts/seal_framework_screen.py <run-id>
```

原 driver `bc51ac2d…`、decode4k/128out/64req/64并发、seed721201及服务参数不变。原 driver 只检查安装 marker；候选完成后必须单独检查实际 Engine PID 的 execute 命中。若观察失败导致没有 marker，服务结果保留但不能认定候选真实命中；不通过新增日志去重跑模型。`complete_step_return` 只是原方法返回，不是额外设备完成 ACK。仍需核64/0、DB/KV/显存/主机负载，单条marker不代表全程覆盖或收益。

| 产物 | SHA256 |
|---|---|
| 已测 policy core，未变 | `ba085577f24684cb980cdd09c2978192ff9b8b3a70fa62aadc1cfd3efced61d4` |
| 新 service policy | `ebe870172f38a306201ec7ede620a85bf431c0994131c692be2ec17d67ea42a9` |
| 新 append | `c2cd377ca51c511efc20b46e99b27a5475fee4a6f826ced9dcf25fe7b8dbea5a` |
| candidate runner，未变 | `806100175e62093870adc7457920491b6836ebf7630155cb6c39696b76b6b255` |
| prepare，未变 | `98cc00a354afe965a5d3c9716be749bff891d64e90a9a9ec666914061bf5d567` |
| launcher，未变 | `f0be6bb2e8b3c04c2df4117660382e0ac59c2c6565b29b3a751525f5577464bb` |

原短shape 105635Z仅为微测信号，服务收益未确认；不叠hot-key/gather或输入等待诊断。BI-V150结果不外推C500，纳入代码协作仍须按方法以中文PR呈现。
