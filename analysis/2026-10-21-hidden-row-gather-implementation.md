# 最终 hidden BF16 gather：独立低风险备选

2026-10-21。owner `/root/hardware_innovation`，root 在研究之后明确委派实现。仅本地CPU写文件和源码合同；没有SSH、GPU、服务/benchmark启动或修改冻结080656、默认补丁和现运行器。它是框架语义边界上的真实新copy实现，尚无设备正确性、端到端收益或accuracy结论。

## 文件与身份

| 对象 | 路径 | SHA256 |
|---|---|---|
| 原冻结runner | `experiments/accuracy/20261021T090505Z-sql-mixed-level3/source/plugin/vllm_fl/worker/model_runner.py` | `e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1` |
| 新runtime | `patches/framework/biv150_hidden_row_gather.py` | `109905b3d276d6e4ff6cc74a7b97dfe6e8ee31a517b0ac7c4fdb163cc37ad8fd` |
| 独立byte transformer | `patches/framework/biv150_hidden_row_gather_source.py` | `881f2cf209da11842577aab01cca3830e985ad7c9030554156757a5de7e791f2` |
| 转换后的完整runner | 尚未接入任何运行source；由transformer生成 | `e68d6886d788a2f56d470fccaee62558d4622545eede2a59fbeb083a5264016e` |
| 最小CPU合同 | `analysis/source/hidden-row-gather/check_contract.py` | `670636a9aea1642afb289ef868239040c7c6aa4320643b373488104b3cc10547` |
| 无权重GPU gate（未执行） | `scripts/remote/validate_hidden_row_gather.py` | `65cb8affd4ae08af877ccb4b4cfca6822eec5ba3f83770f39999ee677c546863` |

只在新的隔离080656完整副本中：复制runtime到`vllm_fl/patches/biv150_hidden_row_gather.py`，对该副本的runner原始bytes运行`transform_source`，将返回bytes写回该副本。不要接在bucket或别的runner改动后面，不覆盖现source。SQL/C2/mixed原footer顺序不变，没有生成默认candidate delta。

transformer锁完整e155，只替换两个原 `sample_hidden_states = hidden_states[logits_indices]` 表达式。每个原if/else分支中先调用helper，None时仍执行原表达式；其后compute_logits、广播、ExecuteModelState、采样与RNG完全保留。新增一个显式import，不靠环境开关或自动扫描源码安装。

## 范围与索引证明

runtime限定当前MiniCPM5-2B/BF16/Llama/2048hidden/6144MLP/42层/16Q/2KV、未量化、单TP/PP/DP/DCP、无SP/ubatch/MM/prompt-embeds/pooling/aux/broadcast/spec/LoRA等非审计路径。Tensor要求同CUDA device、BF16二维contiguous `[M,2048]`、int32或int64 contiguous一维indices、N等于真实request数、M在原最大buffer容量内、合法alignment且hidden/index不共享storage。不匹配时在分配/launch之前返回None。capture状态也回原路。

**这不是任意GPU索引值检查器。** 原e155 `_prepare_inputs` 的非spec分支固定构造 `logits_indices=query_start_loc[1:]-1`，CPU query_start_loc由正向scheduled lengths的累加产生并H2D。helper检查原CPU lengths为int32一维、每项正、N一致、CPU query_start_loc与累加一致、最后端点<=真实hidden row数。因此在精确源的受限调用路径中证明GPU indices来源和边界；不加`.item()`或D2H同步。模型graph padding可能使hidden M大于真实scheduled总数，这仍合法；不能强制两者相等。

私有kernel按实际row index做负索引修正和bounds mask，支持合法重复/乱序/负值copy；public helper仍只用于审计后的query ends。不能把运行时无法读取的任意GPU indices当成已验证输入。后续改变 `_prepare_inputs` 或源身份须拒绝或重新审阅。

## 实际实现和生命周期

`_copy_hidden_rows`为新的Triton BF16 load/store kernel；WIDTH2048 constexpr，实际输入M和输出N使用`do_not_specialize`，grid只由N决定，固定2warps/1stage。没有算数归约、autotune、Python源码按M生成、额外模型行、KV更新或随机操作。输出是新分配的N×2048连续tensor，行数/顺序与原采样表达式一致，输入和indices不修改。

调用仍在原postprocess current stream上，前面的模型和indices生产依赖不变；返回后LM-head照原stream消费。对hidden/indices/out调用record_stream保护allocator生命周期，它不代替跨stream readiness。跨stream调用必须先由调用者建立producer→consumer等待，不能新增全卡同步假装满足异步正确性。

## 已运行检查

- `python analysis/source/hidden-row-gather/check_contract.py` exit0，原始stdout保存在同目录`cpu-contract.log`：exact源/两个原分支/原fallback可逐byte逆回e155/语法/变动或重复转换拒绝；CPU query-end合法边界与破坏证明拒绝；runtime M/N的JIT annotation。
- 三个新.py `python -m py_compile`通过；gate `--help`通过。没有导入本地torch/Triton来运行候选。
- framework_innovation独立只读审阅runtime109905、transformer881f和gate主要控制/worker逻辑，独立执行CPU合同、py_compile/--help通过，未发现明显阻断。其建议“cache观测能力不足不能当copy数学错误”已采纳，见下。

这些只是CPU source/contract证据，不是实际tensor、完整runner生命周期或GPU结果。

后续root在worker启动前发现并要求修正归档基础错误：动态load transformer会创建source/__pycache__，source hash集合必须只遍历regular file。已仅加`if path.is_file()`并检查本gate其余路径、py_compile通过；新SHA65cb8a…覆盖93fd…，runtime和数学未变。尚未执行到设备，不归作候选功能负结果。py_compile/help与源码合同从来不证明整个controller归档路径已执行。

## 最短设备门（唯一owner串行，当前不得并行运行）

当前官方run结束且设备真实释放后，由root上传runtime、transformer、gate以及既有的`validate_block_table_candidate.py`/`validate_async_token_update.py`和`monitor_gpu.sh`依赖。controller参数：

```text
VLLM_PLUGINS=fl PYTHONPATH=<原080656 source> python3 validate_hidden_row_gather.py \
  --run-dir /workspace/experiments/minicpm-s2/framework/<唯一UTC>-hidden-row-gather \
  --runtime-path <上传的新runtime> --transform-path <上传的transformer> \
  --runner-path <原080656 source>/vllm_fl/worker/model_runner.py
```

controller锁同`framework-device.lock`，核实9031关闭/显存空闲/原ixsmi无进程，保存精确runner/runtime/transformer/生成源/gate/工具源、环境白名单与版本、原stdout、GPU样本。唯一child持CUDA context，最多300秒，退出或信号时清理自己process group；child结束后再做真实postflight，不让controller自己的CUDA上下文影响显存空闲判断。

worker不加载权重或启动服务，只做：

1. M259/N29、M952/N16、M2048/N64、padded64/真实62的原query-end copy；输入包含全部BF16 bit patterns，用int16 view比较全部输出，覆盖signed-zero/NaN payload而不以BF16 torch.equal(NaN)冒充bitwise。
2. 同一input/index storage地址改变真实M/N，读取已有JIT cache字典确认不新增specialization；不通过故意读新的device-cache key改变它。
3. int64 indices、CPU/错dtype/宽度/stride/alias/spec/破坏CPU证明的回退；私有copy的合法负值、重复、乱序；显式producer/consumer依赖和删除源引用后的跨streamcopy。
4. 保存CPU/GPU RNG状态不变、fresh output storage、真实N输出。没有计时结果或性能倍率。

输出`status=pass`/exit0才同时确认copy和可观测的稳定shape specialization；copy门通过但cache接口不可读为`inconclusive_specialization`/exit2，不能称数学失败；真实新增entry为`reject_specialization`/exit1。其他真实copy错误记录`reject`和原traceback。能力不足不应触发重复整套GPU实验，root可据明确局限决定下一步。

gate的fixture并未构造完整ModelRunnerFL，也不证明LM-head/sampler或真实endpoint输出；若值得保留，再做匹配短服务对照及必要最终准确率/可复现门。第一轮新shape改善可能被official skip1消除；CPU query-proof和新kernel launch也有热路径成本，不能预报大收益。
