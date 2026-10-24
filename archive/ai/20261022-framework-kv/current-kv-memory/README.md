# 当前版本的 KV 启动诊断

只运行两次原 bc51 `--smoke-only`，不做容量控制或性能对照。原件：`experiments/framework/20261022T201344Z-current-kv-memory-baseline-smoke` 和 `20261022T201518Z-current-kv-memory-finite-smoke`（各自 control 同路径加 `-control`）。root 已核整包 SHA、463/464 份原件及严格空闲后态。

共同 observer 仅在旧6a772a白名单增加 finite init c9a2；新9d43，原观察逻辑不变。preparer e3b93、launcher afc2经 root 增量审阅，完整414/415基点只 append init 和新 helper，形成415/416；每次只启动一侧，原 driver 持锁并清理，wrapper 后验原 profile 单次、原返回和三项恢复。精确源、环境、命令及身份在各 control。

本次 finite 在 profile 前的非Torch残差多4MiB，导致KV521936→521840，与旧性能pair方向相反；不能回填历史或归因具体allocator。两次32输出token IDs相同，DB532四端三SHA同；未覆盖mixed Q/GQA，不等于准确率或性能门。停止追这4MiB，旧有限准入仍默认关闭、收益待确认。

`compare_smokes.py` 是分析源码快照，原工作位置为 `tmp/current-kv-memory/`；复用时放回该位置运行，输出 `analysis/current-kv-memory-smokes.json`。首次本地分析因Windows默认GBK读中文失败，已显式UTF-8修复；未重跑设备。`memory-candidates.md` 保存本轮CPU筛选闭环，其他社区与队列依据在三份既有agent交接。
