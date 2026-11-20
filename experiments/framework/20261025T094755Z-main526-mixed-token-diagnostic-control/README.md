# main526 freshserver 原 mixed token 诊断

仅确认当前已合入 main526 的基线问题，便于判断是否需要撤回已有改动；不恢复 FFN 选行或 selected-Q 等失败候选。

每次新建服务，只提交原 mixed 双请求，不先运行相同长题，避免前序请求产生prefix cache命中。原请求JSON保留，运行时只增加 `return_token_ids: true`；主智能体已核远端实际vLLM `entrypoints/openai/chat_completion/protocol.py:375` 支持。消息、temperature=0、max_tokens=1024、stream及首内容同步均保持，不加logprobs、不启dev mode、不调用无法确认成功的reset API。

先保存原HTTP/SSE、token IDs及CPU频数，再判原85/1..128。长题语义失败仍等待并保存计数请求完成，最后汇总失败退出；运输错误也保存原响应，stream有界排空。旧串行结果复用，本包不再跑serial。首内容同步成功只证明HTTP重叠，不能单凭它声称某个2047/558计算chunk确已发生。

main526/native14f、官方服务CLI、backbone/34native/FP/AOT、设备锁与DB/finally复用已审064055对照。无新生产源码或环境策略；诊断不是官方准确率或性能。mixed首内容120秒/HTTP600秒/stream排空600秒；中断立即走原owner清理。主智能体统一启动，无自动后继。

```bash
python3 verify_service.py --source-dir /workspace/experiments/minicpm-s2/code/20261024T161030Z-main0bf9-main-official --performance-control /workspace/experiments/minicpm-s2/official/20261024T161030Z-main0bf9-main-official-four-rounds-control
```

输出 `mixed-requests/` 原请求、实际请求、原响应、token频数及结果，总表 `diagnostic-summary.json`。tokenizer离线解码待回收后CPU另做，不在设备请求内加载模型。封包SHA见package.json，最终交接后冻结；旧6c19三阶段草稿包保留但不运行。
