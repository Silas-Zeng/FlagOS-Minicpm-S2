# 完整 M 映射与真实采样关联的最薄结构门

复用085500的已核q1实际输入/上下文、全M slots、42normal无alias/前缀安全及未变采样方法；不再抓table/seq/cache、不重做首层oracle，也不比较不同Attention结果逐位相同。本门不是模型精度资格替代。

原event域内，原序只prepare+preprocess并阻塞保存完整M个实际inputIDs/positions，不运行原序模型；然后P重新prepare。期望token inverse从原reqIDs和SchedulerOutput的q独立构造，不复用Plan.ends/inverse，实际P的两数组逆回全逐bit核。P模型只前向一次，既有logits算完只读取N个实际GPU logits_indices，比独立原请求序ends；不复制hidden、不再算logits。

sample_tokens在原_sample调用前后各加一CPU callback；_sample函数本体、sampler、bookkeeping/async快照保持原字节。后验关联同scheduler_output、同logits、原N行、原请求序及InputBatch/sampling_metadata/sampler身份，原_sample恰一次成功返回；不深拷贝generator或history，不把_sample内合法update_async_output_token_ids误判。没有第二次采样或额外draw。

构建：`python prepare_structure.py --base <原422目录> --output <全新目录> --emit-only`。当前最终用 `files-final/` + `files-final-prepare.json` 完整424map；`files/`为早期镜像，禁止部署。原422只五路径差（两helper、runner、两显式runner锁），P/helper/worker/protocol未知源仍拒。helper `12076fa9e2cbde1e0fd4fc93ba722bd8f6577bdc130435ec1007ea5e34c8547c`，runner `3e99f5751d425c488021eca07e47c55fae7b7e47adce25ed4280e3c8fc67cec7`，builder `c719b11511fc273e457a8da0deca26bf2188573ca2a2cf9742bff71d8b462d8b`。

env：`BIV150_COMPUTE_ORDER_STRUCTURE_DIR=<独立control>/structure-artifacts`。每PID输出original/permuted-prepared.npz、structure.json、sample-started.json、sample-link.json。必须fullM两项和独立N indices通过，且sample-link状态为 `structure_and_actual_sample_link_completed` / outside>0 / original_sample_calls=1；单FIRST_SELECTED或普通exit0不足。未知scope或不命中记未覆盖，任一实际映射/关联错误停止，不重试原路、不放宽容差。

仅CPU compile/完整map/精确逆回已过，无模型、GPU或新mock。另一owner已只读审阅12076fa9 / 3e99f575 / c719b115新增差分，无当前短诊断阻断；两整数快照同stream阻塞完成后才重写pinned，原event保留，inverse独立构造，原_sample一次且不重试。代码冻结，root唯一安排原bc51短负载。验收以sample-link completed为准，非仅structure.json；它只佐证原采样调用返回及身份/形状关联，不证明GPU完成、token等价或新路径准确率。精度仍保留独立reference与原官方准确率各自覆盖边界，不将0P准确率和结构正确拼成全模型新路径精度通过。
