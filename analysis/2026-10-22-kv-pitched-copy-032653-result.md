# 032653：2D SAVE独立API字节门通过，wall计时波动

`20261022T032653Z-kv-pitched-copy-gate` 已exit0完成。本agent仅对本地实际原件做stdlib验收，未重跑设备、候选或测试；报告 `analysis/source/kv-pitched-copy/032653-gate-review.json` SHA `eff32911b14287b0caa255b83f984f3f77b61c789366a9789172afd4363b7f6d`。root完整归档SHA为 `2ba3856fef63566c8a372818a2ae60e21c999d8022465d8d29ad13a7de99c55c`，本agent独立复算86项seal及完整文件集合、7项source前后身份、DB快照实体指纹。

冻结outer3ffe、gatec8c0、runtime818e、桥0a4d与c95f均一致。实际g++使用Corex头及rpath、源码在库之前，编译exit0且stderr空；`bridge.so` 为15936B，SHA `9e33ecbf9cf57f52469db6b1d509a600cd1a8eeafe78a54095e88dc474c71fc0`。ldd/readelf、ABI头指纹及worker实际映射的Corex `libcudart.so.10.2.89` SHA `d39d5796…` 均吻合。外层controller258685、唯一worker258707，设备单BI-V150/16SM/32GiB；非零Torch stream handle `94118921500112`，实际max pitch为2147483647B。候选提交紧随同流producer，在同流event完成后先验证新host，之后才执行旧路，未靠后续旧copy掩盖stream错误。

| 实际页序来源 | R / 页数 | 单层原KV字节 | 旧连续copy调用 | 新调用（linear / pitched） |
|---|---:|---:|---:|---:|
| 015315进展victim | 16928 / 1058 | 17334272 | 37 | 11（2 / 9） |
| 021658进展性能候选 | 16768 / 1048 | 17170432 | 26 | 6（2 / 4） |

两组均未触pitch fallback，全部原逻辑页序及KV字节保留；source和host视图均含真实16KiB storage offset。每case九项检查全部通过：候选与独立CPU页号/页内offset oracle、原c95f及完整输出一致，真实提交计数正确，host两端guard和整个source及source guard不变。两case共18项、计时后5项、CPU/GPU RNG均通过；本agent额外以纯CPU字节公式重算两份payload SHA，均与实际结果一致。原页几何来自真实服务，门内张量仍是**单层构造**，并未执行42层模型或服务恢复协议。

两组正确性完成后，仅首case做每窗口8call的ABBA：

| 窗口 | wall ms/call | 同流event ms/call |
|---|---:|---:|
| A：原c95f | 7.415286498 | 0.652491808 |
| B：C batch加2D | 0.672264665 | 0.628266811 |
| B：C batch加2D | 0.681895239 | 0.628109097 |
| A：原c95f | 1.454228535 | 0.652679801 |

保留这个组合单层信号。原基线两次wall差异大，不能报告稳定wall收益；也不能把C batch与2D的贡献拆开，或外推42层SAVE、稳定DMA带宽和E2E。plan、Tensor/descriptor准备、分配、producer、CPU比较不在窗口，准备成本原件另列。实际CPU quota6、Torch CPU线程56，外层保留v1 cpu.stat/host观察；尚不能据此断定某个窗口节流。worker `memory_before/after={}` 源于只读v2路径在本v1实例未观察，不能解释成零内存。20GiB host限制与外层用量均为观察值，非峰值。

DB前后均523表19474行，物理 `dc2c7646…`、schema `0dc7a465…`、logical `c05d7e31…` 三SHA相同。03:27:06.831936Z postflight为68MiB/0%、无GPU进程、9031双栈closed；源码前后不变、worker/编译/清理无错误。没有模型服务、官方性能或accuracy结果。

本地验收第一次复用SQLite helper时传相对Path，`as_uri`拒绝，未写成功JSON。该本地错误及生成cache的说明保存在 `032653-first-review-incomplete.json`；仅保留并移除本地新生成cache，86份封存原件字节不变，改绝对Path续审通过。这不是设备失败，也没有重跑设备或旧测试。

registry已113行、queue86实际完成。root明确本轮本地checkpoint，不再启动新GPU；下一仅root决定的独立64call A/B/C/C/B/A及逐窗口v1 cpu.stat方案，不能回填本门的未测分量。当前文件收口后暂停写供一致归档，goal仍持续。
