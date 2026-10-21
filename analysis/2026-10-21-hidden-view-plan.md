# Hidden-state prefix view：低优先、未验证草案

当前只保留方案。`biv150_decode_hidden_view.py` 与对应 CPU proof 已写出，但尚未运行测试、交叉审查或集成；不能据此声称正确性或收益。优先调查异步采样 ID 更新路径，等待 profile 证据。

## 变换及等价前提

审计输入为 [保留 runner](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/remote-source/model_runner.py>)，SHA256 `446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64`。无 spec 时第 2231 行给出 `logits_indices=query_start_loc[1:]-1`；execute 的 CPU 元数据满足 `max_num_scheduled_tokens=1` 且 `num_tokens_unpadded=num_reqs=N`，非负的 N 个 query 长度只能全为 1，因此 indices 为连续 `0..N-1`。graph padding 不改变有效前缀。

[transformer 草案](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/patches/framework/biv150_decode_hidden_view.py>)只改普通非 broadcast 分支第 4435 行，命中时使用 `hidden_states[:num_reqs]`，其余回到原 gather。两处赋值均做 anchor 检查，broadcast/PP 分支不改，源 hash 漂移或已变换源码直接拒绝。BF16 MiniCPM 结构、并行全为 1、无 spec/LoRA/pooling/KV sharing/ubatch/aux/connector，连续二维 hidden layout、原 logits processor/非量化 LM head 等均须满足。索引仍照原路径产生，采样调用、行顺序、输出 shape 与 RNG 消耗次数不改。

## View 的边界

前缀 view 与 gather 的数值和布局可相同，但前者共享原 storage，不是快照。上游 v0.24 的 [Llama compute_logits](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/model_executor/models/llama.py)调用 [LogitsProcessor](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/model_executor/layers/logits_processor.py)，非 logits-as-input 路径将 hidden 输入传入 LM head、处理新 logits；[UnquantizedEmbeddingMethod](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/model_executor/layers/vocab_parallel_embedding.py)继续分派 GEMM。这仅是上游源码审计，不能代替实际安装版本及 plugin/FlagGems 分派的只读性验证。

runner 的 ExecuteModelState 本来同时持有完整 hidden 和 sample hidden；无 spec/aux/prompt-logprobs 时，后者不再用于 draft 分支。仍须验证 compute_logits 不改输入、同 stream 消费在下次 graph overwrite 之前完成，以及没有新增跨 stream 消费；view 自身保活不能证明缓冲区不被覆盖。草案的 [CPU proof](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tests/test_biv150_decode_hidden_view.py>)包含身份索引数学证明、动态 N/布局/RNG 检查、view 非快照反例、保守回退及真实 runner AST 差分，但当前未执行，不作为通过声明。

## 优先级纠偏

FlagGems index key 含输入 shape；`hidden_states` 常由 graph pad 到 64，active 62/61/60 不必改变 gather 输入 shape。因此不能把新 active 数量、native gap 或 codegen 直接归因给这一行，warm gather 的收益也可能小于新增 Python guard 成本。

更可疑的 [runner 1879 行](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/remote-source/model_runner.py:1879>)读取上一轮实际 active 行数的 `prev_sampled_token_ids`。原 `_prepare_input_ids` 已有 unchanged identity slice 与 no-common 回退；剩余分支先创建两个映射 tensor，再 gather 临时采样 ID、scatter 到持久 input_ids。硬件 owner 负责一次整数 gather→scatter kernel 候选；我负责独立审查及真实方法 GPU gate 脚本的 CPU 准备，保留原 CPU/H2D/fast-slice 行为，不重复实现该候选。诊断归因后再决定是否运行 gate。
