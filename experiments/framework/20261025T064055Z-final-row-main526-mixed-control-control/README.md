# main526 原 mixed 双请求对照

旧FFN527与新unbacked S1候选均在 mixed 长题出现只返回 `<think>`、1024 tokens 耗尽。先用原 main526/tree8671e2ec 与 native14f 执行完全相同的两个真实请求，区分候选退化与原框架/夹具自身问题。

直接使用161030四轮已验证的冻结源码和官方服务参数，原 `mixed_requests.py` 的计数流式请求、长prefill、判分和1024 tokens限制逐字不变；不重复原四串行语义、不加选行补丁或其它诊断数学。先记录本服务实际backbone/34native/指纹/AOT，再执行两请求。所有响应、错误和DB/GPU/源码/native后态保留，原finally负责清理与DB恢复。

```bash
python3 verify_service.py --source-dir /workspace/experiments/minicpm-s2/code/20261024T161030Z-main0bf9-main-official --performance-control /workspace/experiments/minicpm-s2/official/20261024T161030Z-main0bf9-main-official-four-rounds-control
```

仅主智能体实查单卡和9031空闲后运行。对照若同样失败，旧负结果不能归因于选行；若原框架通过，再比较候选。此轮没有性能或完整105准确率结论，不自动追加GPU任务。精确封包身份见 `package.json`。
