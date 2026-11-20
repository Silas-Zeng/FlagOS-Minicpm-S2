# main526：原 mixed 长题独立串行对照

main526 原 mixed 对照也出现与选行候选相同的 `<think>`、1024 tokens耗尽。因此先单独提交同一个“岸边有花、46＋39”长题，判断失败是否需要并发条件。请求原件逐字复制旧223346的 `mixed-requests/prefill-request.json`，消息、temperature、max_tokens、API和判分不变。只发这一个请求，不重跑计数或四道串行题。

没有加入 `return_token_ids` 或其它参数，避免未经实际API核验的元数据开关干扰定位。先保存原始HTTP响应与usage/finish_reason，再按原85答案与think闭合规则判分，失败原件保留。main526/native14f/官方CLI、实际backbone/34native/指纹/AOT、DB与finally清理复用上一对照。

```bash
python3 verify_service.py --source-dir /workspace/experiments/minicpm-s2/code/20261024T161030Z-main0bf9-main-official --performance-control /workspace/experiments/minicpm-s2/official/20261024T161030Z-main0bf9-main-official-four-rounds-control
```

仅主智能体实查设备和9031空闲后运行，无自动后继。若串行也失败，不能归因于mixed调度或选行；若串行通过，再定位并发路径。精确封包和原请求SHA见 `package.json`。
