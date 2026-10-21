# Prefill 非 attention 图回放：现有边界与反证

2026-10-21，CPU/source-only。未 SSH、未启动 GPU、未修改候选。结论：**可定位到现成编译段，但还没有证据说明图回放值得优先实现**；不能将开启已有 piecewise 模式算作新增优化。

## 当前真实状态

`experiments/framework/20261021T072153Z-sql-reflection-screen/server.log:43` 的最终配置明确为 `CompilationMode.VLLM_COMPILE=3`、`backend=inductor`、`use_inductor_graph_partition=False`、`compile_ranges_endpoints=[2048]`、`compile_sizes=[]`。`splitting_ops` 同时包含 `unified_attention_with_output` 与 `unified_kv_cache_update`。这意味着 prefill/mixed 仍运行已编译的 FX 分段，并非逐 Python layer 的 eager 模型。

同一日志 `:74–78`：从 `f7af72be36/rank_0_0/backbone` 读取 `(1,2048)` 编译缓存及 AOT model；`:84` 起捕获 35 个 decode FULL 图。官方 `FULL_DECODE_ONLY` 将 mixed/prefill 的 CUDA graph runtime 分派为 NONE，**不关闭 torch.compile**。因此“再开 torch.compile”或“再做 attention 处分段”都重复了现有机制。

实际 runner 镜像 `tmp/remote-source/model_runner.py` SHA256 `446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64`：

| 准确行 | 已有行为 |
|---|---|
| 3870–3889、3913–3948 | 判断 uniform decode，交给 dispatcher 选择 runtime mode；不是仅凭 batch size 判断。 |
| 4384–4407 | 将该 mode、batch descriptor、attention metadata/slot mapping 放进 forward context，调用 `_model_forward`。 |
| 3838–3868 | `_model_forward` 只代理整模型，不是可独立跳过 attention 的边界。 |
| 5381–5402 | breakable 开关启用时走已有 Breakable wrapper，否则 FULL 模式走 FL GraphWrapper。 |
| 6101–6109 | 编译路径直接调用编译函数，普通 layer hooks 不会在此路径执行。 |

来源限制：本地 reference 为 **13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0**，不是 `-main`；其 graph/break_graph 文件未有本地修改。`tmp/src/vllm-plugin-FL/vllm_fl/compilation/graph.py` SHA `91ba5a848e55630639ee241d8f8e8de1348d616a0b9dd1f0dc9e89ec7ebfec01`，`:112` 已用 global pool，`:150–158` 在 mode NONE 直接透传，`:178` 已禁止非授权时机的捕获，`:180–183/234–242` 已有地址检查。`break_graph.py` SHA `fc24923bc0332ff2588d775dc5108bf78e70f53aef0ba931bc580e8f0a2e1bb8` 只重导出上游。实际 installed 这两个文件及 compilation backend 尚无本轮 exact hash，实施前须补；不能用 reference hash 冒充 installed 身份。

## 不必重新切模型

已下载的实际缓存图 `tmp/remote-source/computation_graph.py` SHA256 `ab75722cd9edd5cbd33a2bb72d3f17f090eb2796ec86386d777a852f8e9cd69c`，只做 AST 检查，无模型或模块导入：

- 85 个子模块：`submod_0,2,...,84` 为 43 个非 attention 段，`submod_1,3,...,83` 为 42 个 KV-update/attention 段。
- `:264–278` 展示实际调用顺序。`:703/706` 的相邻 KV update 和 attention 被归入同一个 `submod_1`，后者写调用方提供的 output；不是两个独立可随意重排的边界。
- **最小有代表性的门为 `submod_2`（:709–868）**：layer0 attention 的 output/residual → O projection、norm、MLP、layer1 norm/QKV/RoPE → layer1 Q/K/V、待写 attention output 和 residual。后接原始 `submod_3`，原顺序继续；不拆成两个全模型 forward。
- `submod_0`（:561–698）包含 embedding/首层 QKV/RoPE；`:698` 返回五个 tensor。`submod_2:868` 同样返回五个 tensor，其中 attention output 是分配好的写入目标。只保留一个普通 hidden tensor 会漏掉 alias/输出契约。

## 官方固定版本已有的路径

[vLLM v0.24 backends.py:579–626](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/compilation/backends.py#L579-L626) 已提供 `wrap_with_cudagraph_if_needed`：当前没有 piecewise graph mode，因此直接返回现有 PiecewiseBackend。fresh FX 编译和 [AOT 重建 caching.py:410–506](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/compilation/caching.py#L410-L506) 都经过该接口。只改 fresh 编译路径可能完全测不到，因为本项目实际从 AOT 加载。

[v0.24 dispatcher:150–213](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/cudagraph_dispatcher.py#L150-L213) 已分开注册 decode 与 mixed keys；[模式定义](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/config/compilation.py#L48-L80) 已有 FULL_AND_PIECEWISE。另有 [breakable capture](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/compilation/breakable_cudagraph.py#L47-L106)，通过 attention/KV 边界暂停捕获；这也不是待发明的功能。这里引用固定 v0.24 一手源码解释机制，不升级框架，不声称逐字等同未取回的 installed backend。

## 若仍值得上卡，最小真实实现边界

提交内容必须是有价值的新 buffer/capture 实现，而不只是改官方参数、偷改 context mode 或路由到现有 wrapper。一个可审查的最小候选是：

1. 在 fresh/AOT 共同创建的 **PiecewiseBackend callable** 旁附加一个有限静态执行 adapter。第一门只对 backbone 的 `piecewise_compile_index=1`（上述 `submod_2`）生效；runtime FULL、实际 CUDA capture、未知输入/alias 契约直接回原 callable。保持全局 mixed context NONE，不改变调度、token 顺序、KV 更新、采样和算术顺序。
2. 使用实际 token 数的精确 shape、dtype、stride、device、逻辑段身份与固定权重地址作身份。只复制动态 activation/residual/positions 到长期持有的 staging；不复制权重。不同 layer 即使复用同一个编译二进制，也不能共用绑定了不同权重地址的一张图。首门不做 token rounding/padding、不猜 benchmark 形状。
3. 保持完整五输出及 alias/mutation 契约；相同形状、输入值变化时必须得到新结果。使用当前 compute stream 的正确依赖，强持有 staging 和 capture outputs。只用私有 pool 做第一门以隔离现有 decode 图；不能未经生命周期证明就共享 pool。图工作空间必须计入 KV 预算，不能先分满 KV 再隐藏额外图占用。

这些不是现成可安全填入的五行代码。[PyTorch 2.10 CUDA graphs](https://docs.pytorch.org/docs/2.10/notes/cuda.html#cuda-graphs) 明确 replay 使用固定地址、需先 warmup 并长期持有输入输出；共享 pool 还有顺序与输出覆盖约束。因此不建议现在铺 43 段、多个 bucket 的复杂缓存。若 staging 只是在有限形状上复刻已有 piecewise，且没有测到新增价值，也不应仅换名字当参赛实现。

## 最短设备决策与明确反证

当前准确率作业结束后，仍由唯一 owner 串行决定；本研究没有申请设备。无需新增多套 CPU 镜像测试。

优先用 SQL 新基线 **2 个真实 prefill/mixed 步的 native trace** 直接观察提交与 GPU 空洞，避免 decode graph 壳的归因盲区。已有稀疏高利用率样本来自旧运行，反对先验认定 prefill 是 host launch bound，但不能证明新基线无空洞。

若有可见的大量逐 kernel 空洞，再对上述一个现成编译段做真实输入直接上卡门：同输入输出/被修改输入契约一致，换值三次 replay 正确，计时包含 staging；不碰模型权重/官方 eval 配置。它只决定能否扩展，不作为 E2E 加速结论。

若 GPU 连续繁忙、staging 后单段没有收益，或额外显存明显压缩 KV，这条即停止。35 秒 prefill 阶段不等于 35 秒可消除的 launch overhead；当前没有可支撑“大收益”的数值。SQL+C2/mixed 已有更短、证据更强的设备实验时，本方向保留研究记录即可，不抢主线。
