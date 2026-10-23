# 天数 BI-V150 算子线：专用 GQA decode attention kernel

代码在框架库分支 `codex/gqa-decode-kernel`（kernel `3be29805d9277b5b22b921dc6b7b48f7bd55cd54`、默认开启 `53635f29b38c172f8a74f327ba67955c47963ab5`、方法说明 `3232d803614603fb94702154091fc37905944efb`），基点是团队 main `87ed53719126208eaa9ba1cab698b14a5693eb5d`，即 #1–#11 全部合并之后。原始登记见 [实验总表](../experiments/registry.csv) 中 `gqa_decode_kernel` 的六行，原件在 [`experiments/operator/`](../experiments/operator)。

## 改了什么

新增 `vllm_fl/patches/biv150_gqa_decode.py`，并在 `vllm_fl/worker/model_runner.py` 末尾追加一段安装。不改 `kernel_unified_attention` 本体、不改 grid、不改 builder 常量、不改 reducer，也不改 #9/#10 的行为；守卫不通过就按原路径启动。

kernel 面向本模型的真实形状：bf16、单 token decode、16 查询头 / 2 KV 头（GQA 8:1）、head_dim 128。

- `ROWS = queries_per_kv = 8`，去掉通用 `BLOCK_M = 16` 在单 token 情况下空转的一半行。
- program id 直接是 (序列, KV 头, 段)，省掉 `resolve_seq_and_query_len` 对 `query_start_len` 的搜索。
- 一步一页、页号按标量加载并随循环位置推进；主循环无掩码，只有尾页 clamp。
- softmax 用 `exp2`，把 `scale * log2(e)` 折进分数。
- 段间 partial 沿用 vLLM 自己的 scratch 布局，另写带显式 stride 的归约，因此**实际段数可以小于分配段数 16**；段数按 `TARGET_PROGRAMS`（默认 256）自适应。不改 builder 常量正是为了让 #10 的分流守卫继续看到 16 并保持生效。

两个必须记住的坑：写回 scratch 的最大值要乘 `ln2` 转回自然对数域（`reduce_segments` 用 `tl.exp` 合并，单段序列看起来是对的，多段才错）；页号基准必须随 position 前进，提在段起点会重复读同一页，之前因此得出 1.86x 的假加速。

## 怎么测与结果

| 层次 | 结果 | 证据 |
|---|---|---|
| kernel A/B（同 seed、同操作数） | b64/kv4096 0.948→0.648 ms（1.46x）、b16/kv16384 0.981→0.536 ms（1.83x）；KV 有效带宽 283→414、274→501 GB/s，同 suite 权重带宽锚点 `lm_head` 约 553 GB/s | 框架库实验目录 `sweeps/20261022T152000Z-gqa-kernel-rows.csv` |
| 同机同 prompt 暖探针（公共基 87ed537，只差本补丁） | 4K 3787.49→5058.23 tok/s（**+33.6%**，TPOT 68.69→48.16）；16K 2589.32→3234.26 tok/s（**+24.9%**，TPOT 76.41→56.38）；重复方差 <0.1% | 登记 #124、#125 |
| 官方四轮（较早快照 `b71e585`，同一 kernel 逻辑） | 4K 4809.36 tok/s（mean TTFT 4723.09 ms、mean TPOT 61.64 ms）、16K 3364.03 tok/s（TTFT 155385.04 ms、TPOT 133.37 ms）；相对官方基线 1878.47 / 队友官方 3683.65 / 2729.07 分别为 +156.0%、+30.6%、+23.3% | 登记 #121、#122 |
| 官方精度 | math_500 Level 3 = **0.9714（102/105）**，门槛 0.95；队友同协议 0.9810 | 登记 #123 |
| 默认开启合规确认 | 只用官方命令（仅 `VLLM_PLUGINS=fl`，无任何 `VLLM_FL_*`）启动，日志 `installed True`、rows 8、page_size 16、backend_rebound True、KV 521936 tokens；同一官方仪表两轮 3341.90 / 3371.88，对控制臂 2712.00 / 2734.40 的稳态为 **+23.3%** | 登记 #126、#134 |

对照条件差异如实标注：控制组与候选组的 GPU KV 相差 96 tokens（521840 对 521936，0.018%），其余启动参数、prompt、种子与主机负载相同。kernel 与通用路径**不是逐位一致**（4K 形状最大绝对差 4.9e-4、16K 1.2e-4，bf16 约 1 ULP），因此精度门是必要条件而不是加分项。

## 收益边界与回退

只在 bf16、单 token、16Q/2KV、head_dim 128、`seq_len <= seq_threshold_3D`（本模型 64）且无 KV 量化、softcap、sink、alibi、mm_prefix、chunk、tensor-descriptor 的 decode 步生效；prefill、多 token chunk、更大 batch 的 2D 路径、其它头配置全部走原 kernel。`VLLM_FL_BIV150_GQA_DECODE=0` 是唯一关闭开关，用于 A/B，官方命令不需要它。

## 审阅后的修复与未闭环

独立审阅提出四项，已修复（分支提交 `b50aa86`、`23e6968`）：门控 fail-closed 必须区分“安装期对签名断言全部键”和“运行期只要求调用点实际传递的键”——被审计的 triton_attn 后端传 31 个关键字而不传 `qq_bias`，第一版把它当必需键，导致 4K 暖探针回到控制水平（#135 记录了这次失败）；新增两个注意力源码的 SHA256 审计；`VLLM_BATCH_INVARIANT` 打开时不安装（该模式强制非 3D 路径，而本 kernel 会改变归约顺序）；CUDA graph 填充行 `seq_len == 0` 不再除零、不再把 -inf 折进 exp 产生 NaN；scratch 视图缓存键加入 `stride(0)`。

按用户新习惯，合并基上的对照改为官方仪表两轮（#126 控制、#134 候选）；官方四轮仍只保留较早快照的 4K 4809.36 / 16K 3364.03。若主办方复核要求四轮，最终交付前需补跑。沐曦 C500 未验证。
