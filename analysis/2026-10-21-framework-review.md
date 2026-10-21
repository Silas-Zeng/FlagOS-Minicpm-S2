# 框架 CPU 审阅与最小 block-table 候选

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

> 历史记录：以下实现状态、审阅和后续建议按当时证据保留；不代表当前集成结论。

审阅日期为 2026-10-21（Asia/Shanghai）。本文仅包含 CPU 源码分析和 CPU 状态机验证，不能证明 GPU 或端到端加速。

## 源码身份与证据边界

- 本地 `tmp/src/vllm-plugin-FL` 的 HEAD 为 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`。Working tree 中 `vllm_fl/__init__.py`、Iluvatar 适配器及 `platform.py` 有未提交改动；审阅的 `model_runner.py` 相对该 HEAD 未修改。
- `patches/plugin` 中已有选定的 prefill 策略、确定性直方图 top-p 实现和诊断配置开关。不假定这些文件与远端源码相同。
- 框架负责人下载了实际安装源码 `tmp/remote-source/block_table.py`。包含原版权头的逐字节副本已作为测试 fixture 提交到 `tests/fixtures/block_table_vllm_0_24.py`。Fixture 目录中的 `.gitattributes` 对该文件禁用换行转换。两个文件的 SHA256 均为 `b3a6649b968fba0b48c333d7ac96e65cc713a86133cc7eef0a8399f5339ec600`。候选 installer 校验这些精确字节，不匹配则报错。
- 环境记录：远端 vLLM 为 `0.24.0+empty`、PyTorch 为 `2.10.0+corex.4.5.0`；本地 CPU 验证使用 Python 3.13.9、NumPy 2.3.5、PyTorch `2.8.0+cpu`。

## 冗余传输与必须保留的传输

实际 BlockTable 使用固定宽度的 host/device buffer，每次 commit 都上传完整的活跃行前缀。行修改包括 add、append、clear、move、swap。MultiGroupBlockTable 构造各组时，通过模块 global 解析 BlockTable。官方版本也具有这些性质。[vLLM BlockTable 源码](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/worker/block_table.py)

Plugin runner 在 `_prepare_inputs` 开始处（本地行 1971）发起上传，早于 CPU 索引和 metadata 准备。传输可以与 CPU 工作重叠，因此上传耗时不自动等于暴露延迟。`synchronize_input_prep`（本地行 3824）在 `_update_states` 前等待，在输入准备后记录 event，保护复用的 pinned host buffer。候选保留该协议及原 copy 操作。

存在一项关键的外部写入：`_get_block_table`（本地行 2319）将 graph padding 使用的 device 行清零，不修改对应 host 行。Dummy run 也会 commit block table（本地行 5960）。因此，通用的“CPU 未变就不上传”规则需要更广的证明。候选明确只允许在真实 `_prepare_inputs` 内跳过；dummy、capture 和其他直接 commit 始终执行上游 copy。

## 已实现候选

文件：

- `patches/framework/biv150_block_table.py`
- `tests/test_biv150_block_table.py`
- `tests/fixtures/block_table_vllm_0_24.py`（完整的已审计上游源码）

候选继承已审计 BlockTable，在任何 runner/InputBatch 创建之前替换模块 global。ContextVar scope 只包裹 `ModelRunnerFL._prepare_inputs`。选定的 plugin patch 未启用它，仅导入候选文件也不会启用。在隔离实验 runner 模块中，类定义之后的集成 footer 如下：

```python
from vllm_fl.patches.biv150_block_table import install
install(ModelRunnerFL)
```

所有行初始均为 dirty。成功的 add/append/clear-row 操作标记对应行；move 标记目标行；swap 标记两行。在 scope 内，若活跃前缀没有 dirty 行则跳过 commit。否则调用原有单次、全宽前缀 copy，成功后只清除该前缀的 dirty 标记。非活跃 dirty 行保留到之后 commit；copy 失败则保留标记。`clear` 使用原 CPU/device 清零逻辑，并保留原 block count，不会悄悄重置 `num_blocks_per_row`。

候选不缩减、替换、压缩或重新分配 block table，也不增加上传 stream 或 kernel。捕获的 device pointer 与 stride 仍为上游值。即使输入准备抛异常，显式 scope 也会重置。源码不匹配会在修改类之前失败，重复安装是幂等的。

每个 table 保存累计内存计数器，分别统计真实 scope 内准备和其他调用者的 commit 尝试、skip、成功提交 copy、提交字节数。`snapshot_stats(table)` 返回分离的 `scoped`、`non_scope`、`total` 字典，不做 I/O 或同步。短实验后可为每组打印一次快照：

```python
from vllm_fl.patches.biv150_block_table import snapshot_stats
print([snapshot_stats(t) for t in runner.input_batch.block_table.block_tables])
```

失败 copy 计入 commit 尝试，不计入 copied bytes。Clear 不重置 lifetime counter。Copied bytes 表示提交量，不表示 DMA 已完成或暴露延迟。计数器增量带来少量 CPU 工作，因此性能测量对应带该插桩的实现。

集成边界很窄：活跃 CPU table 写入必须经过已审计的修改方法；直接 host 写入需要 scope 外 commit。Graph padding 后实际重新激活必须经过 add/move/append 或其他受跟踪修改；dummy 读取始终上传。框架负责人负责审查实际已安装消费者代码中的直接写入。负责人随后报告，对已安装 `vllm/v1` 和保留的 plugin worktree 做只读审计发现，`get_numpy_array`、`get_cpu_tensor`、`block_table.np`、`block_table.cpu` 的访问仅在 BlockTable 内，没有消费者直接写 host table。Device padding 写入仍由上述 scope 边界覆盖。

## CPU 验证

命令：

```text
python -m unittest discover -s tests -p test_biv150_block_table.py -v
```

补充 fixture 和计数器后的结果：10 项测试通过；测试主体耗时 0.336 s，进程 wall time 约 2.6 s。测试加载已提交 fixture，而非被忽略的临时文件，解析前核对精确哈希。两个源码类原样执行，仅将传输 buffer 替换为两个独立 CPU tensor。在 standard 和 hybrid block mapping 下，各进行 2,500 次随机操作，与未修改类比较 host 状态和已 commit 的 device 前缀。定向用例覆盖：

- 未修改 step 跳过，修改后精确执行一次完整前缀 copy；
- device pointer/stride 稳定、非活跃 dirty 保留、copy 失败；
- clear 保留上游 block count，包括之后 append；
- 直接 device padding、强制 dummy 恢复、add/move 重新激活；
- MultiGroup 构造替换后的类；
- scope 异常清理、安装幂等、哈希不匹配拒绝；
- scope 内外计数器、copy 失败计数和分离快照。

这仅验证 CPU 状态转换，不验证真实异步 DMA 完成、加速器 graph replay、输出等价、精度或吞吐。

## 预期收益与限制

负责人观察到的 trace 中，每个 decode step 的 int32 table 约为 `[54..56,8192]`：1.69-1.75 MiB（1.77-1.84 MB）。本审阅未重新计算该 trace 统计。候选仅在无活跃行修改的 step 避免该传输。任何 allocation、请求 churn、clear、重排或 prefix reuse，只要标记一个活跃行，仍执行原完整 copy。

仅作说明：若每请求独立地每 16 个 token 分配一次，则 batch 55 无分配的概率为 `(15/16)^55 = 2.87%`。这只是模型，不是实测分布。Allocation 边界可能相关，请求 churn 还可能进一步降低 skip 比例。若 100-200 us 传输隐藏在 CPU 准备之下，暴露收益会小于原始耗时。设备负责人测得 skip rate 和短配对端到端负载之前，不应宣称数值加速。

因此，最小候选适合低成本筛查，可能只有小收益。只有短冒烟正确、配对结果改善到足以支持下一步，才应进行精度大测。

## 为什么不直接缩窄列数

原始行 stride 为 8192 时，若 `K < 8192` 且存在多行，切片 `[:num_reqs, :K]` 不连续。官方 PyTorch 2.10 CUDA copy 路径对非连续 CPU/device copy 使用临时连续 buffer，再复制到目标。CoreX 可能不同，需要检查实际 dispatch。不能假定隐式 narrow-view copy 仍是一笔 pinned 连续 DMA。[PyTorch CUDA copy 实现](https://github.com/pytorch/pytorch/blob/v2.10.0/aten/src/ATen/native/cuda/Copy.cu)

若最小候选有可用信号，后续可显式打包 pinned 连续 staging buffer，再 scatter 到固定 table，或合并全宽 dirty 行区间。两者都需要测得相对 packing 成本、launch latency、碎片化和额外 kernel 的盈亏点。最大列数必须覆盖全部已分配 block，不能只看当前 token 长度；move/swap/reuse/clear 转换也必须全部覆盖。

## 按证据排序的其他框架方向

1. 继续 scheduler 扫描之前，先 profile 优化候选的暴露 CPU/device 时间线。记录 `prepare_inputs_event` 等待、到 graph launch 的时间、sampling 尾部和 memcpy 身份。Prefill/top-p 补丁已改变平衡，旧基线 profile 不能确定新瓶颈。已有未优化 decode profile 的 memcpy 占比小，因此预期应保守。
2. 归因 launch 后再合并持久 metadata 准备。`_prepare_inputs` 分别上传 indices、query position、scheduled count、computed count，再启动小型 position/length 操作。单个预分配 host/device metadata slab 可减少提交工作且不改变调度，但必须审计 offset 或 lifetime 变化。
3. `_get_block_table` 中 graph padding 是可见的全宽 device fill。若优化后的时间线证明其显著，可用显式 validity 跟踪初始化新增 padded 区间。盲目删除 fill 会暴露陈旧 ID，本审阅未批准这种做法。
4. Graph 启动/capture-size 裁剪主要针对内存和启动成本，需证明在完全相同 serving arguments 下有运行时 KV 容量收益；无证据不能称为逐 token 优化。
5. 已有 block 64、更大 token batch、关闭 prefix、sampler compilation 短筛均为负结果。保留记录；没有新机制或明确混杂因素，不重复等价扫描。

活跃 Attention 路径为 `TRITON_ATTN`，已围绕共享 tensor 构造轻量 metadata。其他项目中 MetaX 专用 pageable D2H cache 修复不能直接迁移。官方 Triton metadata 源码也将已有 block table 和 sequence tensor 传给后端。
[vLLM Triton 后端](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/attention/backends/triton_attn.py)

本审阅智能体未执行远程命令、GPU 实验、官方 benchmark、参考仓库修改或发布。
