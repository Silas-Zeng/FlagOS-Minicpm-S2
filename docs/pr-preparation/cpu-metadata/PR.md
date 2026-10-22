# [Draft] 复用CPU metadata视图，减少输入准备中的小型GPU操作

基于 `main` 的 `70d04f38382e900949ddeb34d2ac75aacdc93af4`（tree `82e37f8f263eeb09563a4790359ec95a0de1ca17`）。本PR只加入CPU metadata复用，不重复提交基点已有的prefill、top-p、SQL和C3，也不叠加异步token更新、KV恢复或其他候选。

原 `_prepare_inputs` 已在CPU计算 `positions_np` 和 `optimistic_seq_lens_cpu`，随后又把请求索引、query位置、scheduled数量传到GPU，并通过小型索引与加法重新构造相同元数据。此改动复用CPU结果与持久pinned staging，把结果异步复制到原GPU缓冲区。原GPU地址、原input-prep事件保护、请求顺序、slot、采样与KV路径保留；描述不支持时执行原表达式。

改动包含受测原件的两个文件，以及中文方法说明。runtime与runner均逐字节复制自 `20261021T175049Z-cpu-metadata-decode4k` 封存源码；runner相对基点只有一个import和一处原表达式的条件包装。未修改算法、官方参数、量化、模型或benchmark。

已有验证均来自天数BI-V150：

- `174115` 最短真实方法门通过：五种decode/mixed/prefill形状，每种11项元数据、slot、CPU镜像和固定地址检查；连续改host值、原event生命周期与图consumer检查通过。方法级wall为 `0.712748 → 0.656465 ms/call`，不外推为端到端收益。
- `175049` 短服务64请求全部完成、0失败，实际出现 `BIV150_CPU_METADATA_FIRST_SELECTED`。对 `175441` 基线，同KV容量521936、同DB三种哈希、原服务参数；耗时 `39.185280642 → 39.073248478 s`，total tok/s `6898.917031 → 6918.697844`（`+0.286723%`），平均TTFT `20076.045601 → 20123.110001 ms`（`+0.234431%`，变慢）。

这是一轮小幅正吞吐信号，运行顺序未随机交替，不能宣称稳定收益或官方成绩。旧SQL+C3的 `103/105` 准确率不能继承为本改动的准确率结果。没有新准确率、完整官方吞吐或C500验证，因此保留Draft；团队评审后再决定是否需要必要补验和合并。

适用条件包括MiniCPM5-2B BF16、TP/PP/DP等并行度为1、原async输入准备事件、无speculation/LoRA/多模态等严格配置。runtime还固定校验两个已审vLLM依赖文件的SHA；依赖变更时，首次选择会明确报错。它没有硬件型号识别开关，不能把文件名理解为对其他平台自动禁用或已验证。

本次仅完成本地PR材料与字节/语法/组合可应用核对，没有新设备实验，也未修改共享checkout、分支或远端。建议合并次序：先评审本单方法；其他同改 `model_runner.py` 的PR基于最终main另行精确组合，不自动叠加本方法。

源码身份、基点blob、证据SHA与缺项见本材料的 `manifest.json`；方法及回退边界见拟加入的 `docs/cpu-metadata-reuse.md`。
