# [Draft] 融合异步采样token的整数gather/scatter更新

基于 `main` 的 `70d04f38382e900949ddeb34d2ac75aacdc93af4`（tree `82e37f8f263eeb09563a4790359ec95a0de1ca17`）。本PR只加入async token更新，不重复提交已有prefill、top-p、SQL和C3，也不叠加CPU metadata、KV恢复或其他候选。

异步输入准备在请求删除、压缩或重排后，需要把上一批采样token写入当前input IDs。原代码先索引出一个临时token张量，再scatter到目标行。此改动用新实现的int32 Triton kernel一次完成gather/scatter，沿用原CPU请求映射和两份索引H2D；不改采样算法、RNG、请求顺序或token内容。

runtime和runner逐字节复制自受测 `20261021T174741Z-async-token-decode4k` 原件。runner相对基点只有一个import和原scatter表达式的一处条件包装；无common/identity快路及原spec、embeds等路径保留，不支持的描述退回原表达式。kernel使用动态长度与stride，不按请求数生成新源码或autotune配置。

已有证据均来自天数BI-V150：

- `063353` 真实 `_prepare_input_ids` 方法门的12类case通过，包括删除/condense、重排、新prefill空洞、正stride、无common和dtype/embeds/spec回退、cross-stream等。比较完整input IDs、embeds、is_token_ids、padding与原H2D记录。该门使用真实方法和替身配置/缓冲区，无整模型准确率或性能承诺；`async-token-adaptation.json` 证明适配SQL+C3后的原/新方法体与该门一致。
- `174741` 短服务64请求全部完成、0失败，实际出现 `BIV150_ASYNC_TOKEN_UPDATE_FIRST_SELECTED`。对 `174402` 基线，同KV521840、同DB三SHA、原服务参数；耗时 `39.410040799 → 39.134667002 s`，total tok/s `6859.571686 → 6907.839537`（`+0.703657%`），平均TTFT `20301.984347 → 20126.242608 ms`（`−0.865638%`）。

这是单轮短筛小信号，未随机交替，不能当作稳定收益或官方成绩。没有本方法的新整模型准确率、完整官方吞吐或C500验证，旧SQL+C3的 `103/105` 不能继承，因此保留Draft。团队评审后决定必要补验与合并。

适用范围由受测runtime限定为iluvatar平台、MiniCPM5-2B BF16、指定模型结构、相关并行度为1、async scheduling、无spec/LoRA/embeds等组合；tensor要求同device、int32 token、int64索引、合法正stride、不同storage。CPU已有映射证明索引范围及目标唯一性；重复源读取允许，重复目标退原路。原current stream承接两份H2D，`record_stream`仅保护分配器生命周期，不能替代producer readiness；capture退原路。

本次仅做PR材料打包、身份与组合可应用核对，没有新设备或套件，没有修改共享checkout/分支或远端。此PR与CPU metadata草稿都触及 `model_runner.py`，应各自评审，按最终main精确组合；组合后的设备与准确率尚未验证。源码身份、基点blob、证据SHA和缺项见 `manifest.json`；拟加入的中文方法说明为 `docs/async-token-update.md`。
