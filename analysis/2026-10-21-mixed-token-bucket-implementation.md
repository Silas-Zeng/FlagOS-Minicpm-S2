# Prefill/mixed token bucket：独立最小实现

2026-10-21；CPU-only，未 SSH、未启动 GPU、未改 080656 冻结 source 或任何运行 driver。实现仅为可供最短真卡门使用的独立候选，默认未启用；未继承 SQL+C3 的103/105准确率，也没有性能结论。

## 实现与接入

- 实现：`patches/framework/biv150_mixed_token_bucket.py`。
- 专用 footer：`patches/framework/mixed_token_bucket_footer.py`。
- 设计依据：`analysis/2026-10-21-mixed-token-bucket-plan.md`、`analysis/2026-10-21-mixed-token-bucket-source-review.md`；未重复先前 DB/硬件研究。
- actual runner 持久原件：`experiments/accuracy/20261021T090505Z-sql-mixed-level3/source/plugin/vllm_fl/worker/model_runner.py`；actual backend 已在该run的 installed source归档，阅读镜像 `tmp/remote-source/triton_attn.py`。
- 新取得的 actual KV writer 持久原件：`analysis/source/mixed-token-bucket/triton_reshape_and_cache_flash.py`。其 `reshape_and_cache_kernel_flash` 在任何 key/value load/store 之前，对 `slot_idx<0` 直接返回；Python launch 的 token grid 取 slot_mapping 长度。

GPU owner 必须在新的独立 source 副本复制实现到 `vllm_fl/patches/`，将 footer 的**原始字节**追加至完整080656 runner；不要文本重排、换行转换或把它接到其它候选。原 SQL→C2→mixed 安装顺序保留，bucket 最后安装。模块不会靠环境变量或 import 自动开启；没有创建 candidate delta 或覆盖默认 performance.patch。

## 精确 guard

| 对象 | SHA256 |
|---|---|
| 原080656 runner，完整前缀 | `e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1` |
| 唯一允许的新增 footer 后缀 | `21074c950f7ebfec73215f8db746f13b6980779277b084cec6c79e27b706e620` |
| actual Triton backend | `1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605` |
| actual Triton KV writer | `f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb` |

除文件身份，还检查 runner class binding、Iluvatar vendor、backend cache-writer 函数 alias，以及 separate KV update 属性。runner原字节也允许直接安装供隔离门调用；若有新增 footer，只接受唯一完整精确后缀，额外行或前缀变动即拒绝。

## 实际 scope 与语义

`execute_model` wrapper 只建立含 runner/scheduler 对象身份的 ContextVar，finally 清理；dummy/profile/capture直接调用 determine 不获授权。原 determine 总是先执行。只有 real execute、mode NONE、descriptor 非uniform-decode、max_query>1、M>=256、原descriptor未pad时，才令 `B=ceil(M/128)*128`；B=M或B超过原max/input/position容量则回原行为。pure decode、FULL、强制eager/uniform/LoRA捕获参数、cascade、encoder和spec tokens均回原路。

scope **包括纯prefill尾步与mixed尾步**，并不要求天然single-token prefix；原M259/M952的精确请求组成尚无直接证据，因此不加针对其猜测的prefix条件。模型限定目录名MiniCPM5-2B、BF16、未量化、LlamaForCausalLM/silu/2048hidden/6144intermediate/42层/16Q/2KV；排除MM、prompt embeds、mRoPE/XDRoPE、pooling、aux输出、KV sharing/cross-layer共享、KV/EC connector、SP/ubatch、多卡和spec/LoRA，FULL_DECODE_ONLY配置不变。

只 `dataclasses.replace(descriptor,num_tokens=B)`，保留真实request数量/uniform/mode/DP返回；若开启 cudagraph stats，用原类型构造真实M/B/padding统计。未修改 scheduler、attention metadata builder、slot mapping builder、postprocess、logits_indices、LM head或sampler。

原 NONE 路径仍向attention传真实M；C3仍按真实M切片。原 `_get_slot_mappings` 已给M:B填-1，actual writer先跳过这些行。原 preprocess 已给positions[M:B]清0；新wrapper在其返回后同current stream给input_ids[M:B]清0，使embedding尾索引合法。真实前M输入不变，采样仍为原N行，不增加随机调用或消费行。没有 `.item()`、设备→host读取、全卡同步或逐层清尾kernel。

padding attention output 尾仍可能是未初始化/NaN。在本限定普通Llama行独立GEMM、norm、activation下它不应回流真实行；这仍须真实污染尾门验证，不能凭CPU合同视为已证明。改变M可改变vendor MM调优配置和数值，不承诺bitwise；新bucket的首次调优与暖态额外row开销都要保留。官方skip1可能消除冷shape收益，不能把冷启动改善视为正式得分。

## 已完成的最小检查与局限

`python -m py_compile patches/framework/biv150_mixed_token_bucket.py patches/framework/mixed_token_bucket_footer.py`通过。

`python analysis/source/mixed-token-bucket/check_contract.py` 八项合同通过，原始stdout在同目录 `cpu-contract.log`：259→384、952→1024的descriptor/stat/合法尾/前M不变/context清理；uniform/FULL/容量/eager四fallback；非execute determine保持；真实冻结runner和footer允许，分别扰动即拒绝。硬件owner独立执行与审阅，无需另建测试框架。

该检查使用纯Python Buffer与`_eligible=True`，**不验证实际GPU Tensor、stream、KV、RNG、模型输出、作用域全字段或性能**。本地直接import torch因重复libiomp5md.dll报错；未设置KMP绕过或修改环境，未把这一环境错误记为候选失败。

最短下一步仍由唯一GPU owner在当前正式run结束并清理后执行：新source跑实际M259/M952对照，含未初始化/污染tail与紧接下一真实step；比较有效hidden/logits、KV及同N采样/RNG状态。若不bitwise，保留差异后交owner决定，不能自动扩大accuracy。门通过才测同参数SQL+C3与+bucket短pair，分别记录首见/暖态、DB/KV/显存与候选实际命中marker。

## 独立审阅

hardware_innovation已审 runner/attention/cache的真实M与slot负值路径、ContextVar/stream生命周期、exact footer、CPU合同；对最终scope措辞与suffix守卫两项建议已落实。详细结论在 `analysis/2026-10-21-innovation-hardware.md` 与 `docs/agent-work/hardware_innovation.md`。没有授权默认提交、准确率继承或并发设备实验。

## 已准备的无权重最短 GPU 脚本（未执行）

`scripts/remote/validate_mixed_token_bucket.py` SHA `12b4c421325e209aeab5eb14ba27b91250c0404d3289087252c5164b6f2cac4e`，py_compile与`--help`通过，当前没有设备运行结果。复用已有 `validate_mixed_decode.py`、`bench_attention_dispatch.py`、`validate_block_table_candidate.py` 与 monitor；CLI为 `--run-dir NEW --runtime-path C2_MODULE --mixed-path C3_MODULE --bucket-path BUCKET_MODULE`。

仅M259→384和952→1024两个case，均31个decode加1个prefill。actual配置/Builder/Impl/缓存writer/C2/C3实现未伪造；padding wrapper在明确标注的小Harness中操作真实CUDA buffers，不实例化完整ModelRunnerFL。IDs尾置130577、positions尾置巨大非法位置，调用候选同流zero后小型合成embedding须合法；padding操作前后CUDA RNG状态保持。Q/K/V/out尾NaN，slot-1，比较原M与B下有效Attention输出和整KV逐位相同，要求out尾仍NaN。再从KV长度1023接1024的32请求decode，复用同64block/req缓存与被污染backing，核有效输出/KV逐位、其余out存储保持，确认puredecode descriptor不pad。

脚本独占同一lock，预先查9031/显存，保存命令/源码hash及原件/配置/包版本/GPU采样/日志/失败与退出；不跑服务、权重、计时或profiling。它只证明此合成Attention/KV隔离和真实CUDA零尾的门槛，不承诺全模型MM、hidden/logits、采样或原runner完整H2D/event生命周期。设备门通过后仍需原参数短服务筛选与必要独立accuracy。root负责等待当前官方run完结并清理后独占执行。
