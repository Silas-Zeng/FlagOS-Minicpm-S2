# 优化工作源码索引

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

> 历史源码审计记录：以下状态按撰写时证据保留；最新状态以项目工作记录为准。

以下路径均对应 `docs/environment-2026-10-21.md` 记录的固定源码版本。

## 模型

- `/workspace/MiniCPM5-2B/config.json`
- 架构：Llama 风格的稠密解码器。
- 隐藏维度 2048，42 层，16 个查询头、2 个 KV 头，头维度 128，中间层维度 6144，BF16。
- 查询头与 KV 头的比例：8:1。

## vLLM 插件

- `vllm_fl/platform.py`
  - 将该平台路径的分页缓存块大小默认为 16。
  - 注册 `vllm_fl.worker.worker.WorkerFL`。
- `vllm_fl/worker/worker.py`
  - 延迟创建 torch/CUDA 性能分析器。
  - `profile()` 控制 HTTP 性能分析端点。
  - 显式解除 Iluvatar 采样器的编译包装。
- `vllm_fl/dispatch/config/iluvatar.yaml`
  - 声明的优先级：FlagGems、Iluvatar 厂商实现、参考实现。
- `vllm_fl/dispatch/backends/flaggems/flaggems.py`
  - `VLLM_FL_USE_FLAGGEMS_ATTN` 默认为 false。
  - 为 false 时，注意力分派到 vLLM `TRITON_ATTN`。
- `vllm_fl/dispatch/backends/flaggems/impl/attention.py`
  - 可选的 `AttentionFLBackend`。
  - 调用 FlagGems `reshape_and_cache_flash` 和 `flash_attn_varlen_func`。
- `vllm_fl/dispatch/backends/vendor/iluvatar/iluvatar.py`
  - 厂商路径同样返回 vLLM `TRITON_ATTN`。
  - 包含 Triton 兼容补丁和采样器编译禁用逻辑。

## FlagGems

- `src/flag_gems/ops/attention.py`
  - 通用全注意力内核和 `flash_attn_varlen_func`。
- `src/flag_gems/ops/flash_api.py`
  - 纯 Triton 分页/变长注意力分派器。
  - 单 token GQA 将八个查询组交换到序列维度。
  - 选择固定的 `mha_block_*` 启发式配置。
- `src/flag_gems/ops/flash_kernel.py`
  - `flash_varlen_fwd_kernel`；该内核没有自动调优装饰器。
- `src/flag_gems/fused/reshape_and_cache_flash.py`
  - 分页 KV 写入内核。
- `src/flag_gems/runtime/backend/_iluvatar/heuristics_config_utils.py`
  - 当时的分页注意力配置使用 `BLOCK_N=32`、四个 warp、三个 stage，`BLOCK_M` 从 16 到 128。
- `src/flag_gems/runtime/backend/_iluvatar/tune_configs.yaml`
  - 通用注意力自动调优候选；不能据此证明分页变长内核也在自动调优。

## 主要源码假设

由于插件默认不启用可选路径，基线没有使用已安装的 FlagGems Attention 路径。这是已核实的源码事实。其性能影响在同服务 A/B 和 trace 分析完成之前仍未验证。
