# BI-V150：分离混合批次的计算顺序与请求采样顺序

混合批次中，单 token decode 请求可能散落在 prefill 请求之后，现有 Attention 切分只能识别连续的 decode 前缀。这些行会随其余批次进入通用路径。本改动对当前步骤构造局部计算排列，将单 token 行聚拢，再把 logits 行恢复到原请求顺序。

只修改 `vllm_fl/worker/model_runner.py`，新增 `vllm_fl/patches/biv150_compute_order.py`。实际输入、positions、页表与 CPU metadata 使用同一计算排列；持久 InputBatch、请求顺序及原 sampler 的调用和随机数归属保持。未知形态在首次写入之前回原路径，写入之后发现不一致则停止该步，避免重复提交模型或采样。

基于 `3283672b`，包含队友已合入的 prefill normalization；保留其 Attention 实现和全部 runner footer。候选代码提交 `4fca58ba`，完整源码 tree 为 `5c77e68c`，与下列当前版本实测相同。适用范围受 BI-V150、固定 BF16 MiniCPM 配置、单 KV group、无 speculation 及已核来源绑定限制；C500 尚未实测，非 iluvatar 在新增 CUDA 检查前返回原路径。

| 验证 | 当前结果 | 限制 |
|---|---|---|
| 16K/128、32 请求短对照 | 两侧32成功0失败；4435.97→4728.30 total tok/s；P实际命中 | 表观+6.59%，KV521840→521936，`gain=null`，不能归因收益 |
| 原 Math500 Level3 全部105题 | 103/105，98.0952%，达到原95%门；无请求错误或空最终答案 | 1题到原输出上限；P零命中，不能证明P分支准确率 |
| 原官方4K/16K吞吐 | 8轮全部SUCCESS，共1536请求；原第2–4轮均值：4K **5116.68**、16K **3436.04** total tok/s | 单臂绝对结果，`gain=null`；不与旧组合或队友单轮成绩归因比较 |

官方同一 Engine 实际命中 P：N62、M2048、原连续decode前缀2、全部decode61、原前缀外59；原model forward返回，logits逆回原请求行、原sampler处理62行。TTFT为4580.19/152082.85ms，TPOT为57.74/130.38ms。吞吐命中不能弥补完整准确率评测中的P零覆盖，因此保持Draft，不自动合并。原725份原件逐项核验后导入726项，DB567表/20986行变为569表/21053行，如实保留；源码、官方脚本及参数未改。

已复用未变的计算排列、逆映射和原采样结构证据，本次新增 normalized 绑定与平台隔离已互审。未为构造代码分支重跑测试。没有改变模型、官方 benchmark、SERVER 或采样超参数，也没有新增算子实现。

证据随[实验 PR #2](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/pull/2)批量同步：[官方摘要及原CSV链接](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/framework-experiments-20261022/analysis/compute-order-current-main-official.json)、[完整准确率及覆盖限制](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/framework-experiments-20261022/analysis/compute-order-current-main-accuracy.json)、[短对照及KV失配](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/framework-experiments-20261022/analysis/compute-order-current-main-pair.json)。源码没变的映射、采样和结构验证直接复用，没有为上传重测。

本方法不依赖 Draft PR #15。后续合入其他 runner 或 Attention 修改时，需要显式更新精确来源 profile 并核对实际启用；来源不匹配会回原路径，不能仅看服务启动成功就认为优化生效。队友新PR #20的残余混合Attention分发与本方法处理路径有交集，未做组合或宣称收益相加；其验收和组合兼容性留待后续。当前保留Draft候选，准确率P覆盖与严格可比收益仍待确认；C500无本方法实测。
