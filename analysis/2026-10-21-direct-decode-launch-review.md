# Direct 3D decode launch：CPU 正确性审阅

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

> 历史记录：本文保留当时的 CPU 审阅与后续门禁建议，不代表当前设备验证状态。

当时结论：适合进入隔离的 GPU 正确性/计时门禁，尚不是已验证的服务优化。本次审阅没有启动 GPU 工作，也未修改已安装的 Attention 源码。

## 已审计输入与候选

实际下载的文件已独立核对哈希：

- `tmp/remote-source/triton_unified_attention.py`：
  `54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f`
- `tmp/remote-source/triton_attention_helpers.py`：
  `59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1`

`patches/framework/biv150_direct_decode.py` 导出 `transform(source: bytes, helpers: bytes) -> bytes`。任一输入哈希变化都会被拒绝；它仅修改 kernel 的 resolver block 和 3D grid0，返回 bytes，不写文件、不导入 torch/vLLM。输出 SHA256 为 `e10a3efbb36efc0e007f875d1b981cd0cb447bc861d19ec5c3bda689a39677fa`。该输出只能交给隔离实验模块使用。

## 映射论证

已审计 helper 将序列边界映射到 `floor(query_start[seq] / BLOCK_Q) + seq`。query length 为一时，活跃 query block 的 local block index 为零。query length 为零时，在 segment 除法或输出写入之前返回。这与官方 helper 实现一致。
[vLLM Attention helper](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/ops/triton_attention_helpers.py)

因此，直接使用 `pid0 = seq_idx`、`local_block = 0`，并直接加载 start/stop/sequence length，会为每个活跃的 0/1-query 序列恢复相同 metadata。公共 early-return 保持不变，支持首部、内部、尾部 zero-query padding 造成的 query-start 重复值。

对于稠密 MiniCPM batch 64、BLOCK_Q=2，原始 grid0 为 96，包含 64 个活跃位置和 32 个空位。若只将原映射截断为 grid0=64，会丢掉序列 43 到 63。因此必须同时修改 resolver 和 grid。该候选在此用例减少三分之一 query CTA launch，不等于 Attention 耗时或整个服务延迟减少三分之一。

已检查审计 kernel 内 pid0 的全部消费者：它仅输入 resolver。之后的 Q 读取、block-table 读取、mask、ALiBi/bias、循环边界和 partial store，均使用解析后的 sequence、local block 和 query-start。没有 kernel 计算通过 `num_programs(0)` 使用 grid0 大小。KV-head 和 segment program ID 不变。

对每个活跃 token/head/segment，目标仍按实际 query-token offset 索引，不按 sequence program ID 索引。未增加重叠 store 或 cross-CTA reduction。独立 reducer 保持 raw-token grid 与 owner lookup；即使 prefix 值重复，zero-query 序列也正确地不拥有实际 token。

## 门禁与边界

- 现有 `use_3d` 选择逻辑不变：query length 大于一、没有 intermediate buffer、序列数超过 `seq_threshold_3D`，或启用 batch invariance，仍走原 2D 路径。
- 特化依赖已有且真实的 `max_seqlen_q <= 1` 合同。调用者声称最大 query 为一却传入更长 query，超出本证明范围；不会为重新查明这些长度新增 host/device 同步。
- Zero-query/zero-KV padding 序列保留 `tiles_per_segment` 之前的原 early-return。活跃 query 对应无效零 KV 长度的问题不由此补丁修复。
- CUDA graph 保持全部 pointer 和 stride。捕获的 sequence-count shape 固定，各次 replay 可在合法 0/1 长度内改变 query-start。Padding 下应比较实际有效输出；prefix 未表示的额外 padded output-token slot 在基线本身就有未定义/陈旧 partial 风险，不能混同于实际活跃 token 的正确性。
- TILE_SIZE、BLOCK_M/BLOCK_Q、warp/stage、segment count 和源码算术/softmax 顺序均不变。实现仍在已有通用算子内，不引入替代路由或 RNG。

逐位相等有可能，但尚未证明：将 local block index 固定为编译期零会改变常量传播、寄存器压力，可能影响指令调度；不同 CTA ID 也会改变调度。GPU 门禁必须在实际相同输入下比较输出和有定义的 partial；CPU 映射证明不能建立数值恒等。

## 最小 CPU 验证

`python -m unittest discover -s tests -p test_biv150_direct_decode.py -v`

结果：6 项测试在 0.070 s 内通过。穷举至八条序列的所有 0/1 模式，覆盖 BLOCK_Q 1/2/4/8；覆盖 55-of-64 graph padding、内部/首部零、全零 batch 和 512-sequence 稀疏用例；证明稠密空位及错误截断，并比较 MiniCPM token/head/segment 目标。也检查了输入源码哈希不匹配时的拒绝。

对两份实际审计文件还做了一次内存内转换，通过 AST/语法验证：reducer AST 相同、`use_3d` 门禁相同、2D grid 不变，从公共 zero-query early-return 开始的 kernel 算术尾部逐字节相同。未导入转换后的模块，也未写入源码文件。

当时建议的下一门禁是极小的真实设备同输入比较：稠密 batch 64 / 4K、batch 30 / 16K、zero-query padded row，以及 2D 回退；预热后可验证 graph replay。通过后才做短服务配对，衡量暴露出来的收益；任何稳定的小收益都可能有价值，不设固定百分比门槛。未修改对照组 greedy 自身不稳定的记录见 `2026-10-21-framework-smoke-differential.md`，不能以此免除本门禁。
