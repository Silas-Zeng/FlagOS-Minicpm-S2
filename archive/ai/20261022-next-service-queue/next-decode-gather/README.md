# 纯 decode 省去无消费者的 CPU token gather

仅 CPU 准备；未部署、未上卡，没有性能或模型准确率结论。适用本项目 MiniCPM5-2B／天数 BI-V150，其他平台不外推。

根负责人新实际诊断回执：当前6f组合512步入口等待累计4.078ms／preprocess10.849s，约0.0376%；该局部快照不支持高成本 pinned 所有权改造，暂不实现那条方向。这里改查预处理本体：**原 GPU 输入准备能覆盖整批有效 token 时，不再收集随后无消费者的 CPU input IDs。** 收益上限尚无局部计时，逐步 guard 本身可能抵消节省，不能预报大收益。原 GPU 数学、请求顺序、采样/RNG、metadata 和输入准备 event 都保留。

- `biv150_decode_cpu_gather.py`：`1a9de781b2f9504c627991071c5ee4b52eda59ca8af283f28a15b9fab38ef7bd`。精确6f原字节的2011–2024行只包一层条件，逐字节可逆；没有替换 CPU gather 算子或 GPU token 准备。依赖原 metadata `0e961524…` 与 async `1bb85e31…` 的受审 scope，源首次核 SHA，资格每步重算。
- `validate_decode_gather.py`：`f9bc1491347811027c94dbbbc80edd24c0ed55e193b18fc15654ab4e4976e4f1`。最小 fork 原 `validate_cpu_combination.py`：双方以6f为基点、绑定同一原两 helper；原五 case，加 identity 和新请求两个必要 case；四步 graph 改纯 decode62。每次保原11项比较/RNG，poison CPU scratch 证死工作，GPU全部有效 IDs 另有 CPU token/previous-token oracle。CPU scratch 只在资格证明成立时允许保留旧值，GPU输入和固定地址必须与对照一致。无 timing，不重跑原12类 async 单项门。
- `check_cpu_contract.py`／`cpu-check.json`：唯一新增合同一次0.1833s通过。真实 scope AST 配 CPU 描述符检查16个资格/回退边界、跨步失效，源码逆回及原四个 GPU 输入/事件方法 AST相同；不是 GPU 模拟，不证明真实拷贝、stream、graph、RNG或收益。另仅做 compile／无 Torch、Triton、vLLM 导入／`--help`。

## 资格与完整覆盖证明

只接受 text、BF16、42层/2048hidden/16queryheads/2KVheads、并行1、async、无spec/draft/embeds/MM的既有受审范围；所有请求恰一个 token、全有 previous sampled row、请求及旧行唯一、旧行合法，Tensor dtype/device/stride/storage 及 CPU位置范围合法。映射异常、new request、无previous、mixed/prefill和未知条件均执行原CPU gather。合法反序映射保留原 GPU scatter；identity 保留原 GPU slice copy，不缓存旧资格或旧指针。

在该子集里，原 cumsum 的目标恰为`0..N-1`，`num_common_tokens == total_without_spec == N`，因此 `_prepare_input_ids:1852` 不执行 CPU H2D；原 identity copy 或原 scatter 覆盖全部有效 GPU IDs。精确6f类内 `self.input_ids.cpu/np` 显式站点仅2023行的写入；间接 reader 是1794、1852行的`input_ids.copy_to_gpu`，均由上述条件排除。其他模型输入、draft、pooling/embedding消费者用 GPU IDs；本候选不放宽这些未知特性。条件失效的下一步先执行原 CPU gather，随后原 H2D，不能把之前保留的 CPU scratch 当作新数据。

## 根负责人执行入口

本门沿原 controller 为唯一设备锁、child、monitor、300s timeout 和定向清理 owner，不加第二 controller。原件固定后由另一职责 owner 审阅，再由 root 唯一 SSH／GPU owner 选新 UTC 目录执行：

```text
python validate_decode_gather.py --run-dir RUN \
  --runner-path EXACT_6F_RUNNER \
  --runtime-path ORIGINAL_METADATA_0E \
  --async-runtime-path ORIGINAL_ASYNC_1BB \
  --gather-runtime-path biv150_decode_cpu_gather.py
```

还需原`validate_block_table_candidate.py`和`monitor_gpu.sh`，依赖 actual input_batch/utils/block_table 三 SHA 不变。没有真实 selected 或任何 token/graph/RNG 比较失败即停止；正确性通过之后才由 root 决定是否复用原4K/128out/64req最短服务验证，不能拿门的耗时作吞吐。默认不安装、不改6f原件、已合并代码或已安装框架。

社区启发仅取 [vLLM MRV2 官方设计](https://github.com/vllm-project/vllm/blob/main/docs/design/model_runner_v2.md) 的 GPU 持久状态/减少冗余 CPU 准备思想，未合并新框架。旧备忘提到当前`buffer_utils.py`有`async_copy_to_gpu()`的表述已过时，实际已见`UvaBufferPool.copy_to_gpu()`等；本候选不依赖 UVA、pool 或这些新接口。

跨职责定向只读互审通过（runtime `1a9de781…`、gate `f9bc1491…`）：显式 CPU 写入与1794/1852两处间接 H2D reader 的完整覆盖证明成立；新请求、mixed、spec、embeds/MM 的原路及跨步资格失效均保留。原 GPU IDs 更新、metadata、输入准备 event 未改；新增门只允许已证死 CPU scratch 留旧值，仍要求全有效 GPU IDs 的独立 oracle、固定地址、四步 graph 消费者及 RNG 通过。未重跑合同或设备；尚无真实服务命中、准确率或性能结论，逐步 guard 成本仍可能抵消收益。
