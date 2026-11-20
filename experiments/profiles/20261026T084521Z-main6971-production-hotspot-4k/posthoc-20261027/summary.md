# 旧 main6971 正常 decode：没有大额跨步 host 提交空洞

只读复用 `20261026T084521Z` 的既有 ixsys，未启动 GPU。393916416B 原件 SHA256 为 `f96d26feceeaa2aaee32ff65c44b9d537065df2164b3f0f29385c406c561875a`。历史源码是 main6971/native14f；**不能作为当前 main241/main56 的性能预算或收益资格**。

选择 2604–2667 共64个连续正常 N64 puredecode 步，另取2668开始作末边界。prompt/computed/output CPU元数据证明每步都是decode，远离162/258/642/1053四个插桩步骤，段内没有 `biv150_diag`，时钟快照偏差跨度400ns。

| 实际阶段 | 64步设备活动区间并集 ms | 均摊 ms/步 | 完整连续段占比 |
|---|---:|---:|---:|
| Graph span | 2260.262760 | 35.316606 | 92.32% |
| postprocess：row gather＋lm_head | 73.148764 | 1.142949 | 2.99% |
| sampler | 97.189288 | 1.518583 | 3.97% |
| 下一步 preprocess | 7.076150 | 0.110565 | 0.289% |
| sampled output D2H | 0.137623 | 0.002150 | 0.0056% |
| trace没有设备活动覆盖的间隙 | 10.430136 | 0.162971 | 0.4260% |

完整段2448.244721ms。1857项GPU活动（1408个图外核＋65个与边界相交的Graph span＋384次copy）全部通过唯一API correlation与显式flow交叉确认；1856个微间隙的后继操作全部已在间隙开始前入队。最大间隙49.52µs。间隙与 `cudaEventSynchronize` 相交6.784799ms，但这不能当可删除CPU工作；后继入队已完成，更不能将等待API全长算成提交气泡。

63个完整 Graph→nextGraph 周期均值38.256621ms，其中Graph35.319230ms；Graph后2.937391ms中的2.774436ms有实际图外设备活动覆盖。主要次序是 row gather→lm_head→FP32 cast/temperature→top-p统计/过滤→softmax→exponential noise→divide/argmax→D2H→下一步元数据copy/slot mapping。

Graph外 lm_head 的单独 `linear_kernel` 均值1.136700ms/步。sampler主要核为 temperature `true_div_func_kernel_rank_2` 0.350552ms、两次 `_weighted_hist` 合计0.291341ms、随机采样 divide 0.191064ms、softmax 0.183308ms、row stats 0.102538ms、exponential 0.100661ms。它们是实际设备工作，不是CPU空洞；没有在本轮提出或重启采样融合。

**范围：** Graph整段是device Graph span，不等于图内每瞬间计算/访存饱和。profiler本身仍可能影响执行，本段只是排除大额跨步host提交空洞，不报告关闭profiler后的净收益。父子NVTX范围重叠，不相加作CPU耗时。当前不新开调度器，不扩窗口，不重启失败采样融合；下一阶段优先Graph内GQA/线性热点，先按新main已有实现去重。

复现：从项目根执行已有Python运行时：

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 'tmp/main6971-existing-timeline-20261027/attempt-20261027T035459Z/analyze_puredecode.py'
```

脚本要求同目录原 `receipt.json`/`baseline.ixsys`，并直接校验已有084521调度元数据SHA；不依赖准备时的 `selected-steps.json`。派生小件为 `puredecode-summary.json`、`puredecode-steps.csv` 与此说明/分析脚本；逐间隙JSON仅供本地深查。巨大trace/tar留本地及远端，不复制进文档仓。
