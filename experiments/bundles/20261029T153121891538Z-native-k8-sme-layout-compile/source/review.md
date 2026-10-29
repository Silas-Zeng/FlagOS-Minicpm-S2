# NativeK8 SME probe 独立 CPU 审阅

范围：只审这份隔离探针的实现/ABI/CPU 静态边界，不编译、不加载 SO、不访问设备；不构成布局或生产资格。

- 已修正 host/device 条件：目标错误仅在 `__IX_ARCH__` device pass 且目标不是 `ivcore11` 时触发，和当前 main 的保护形式一致。host pass 不再因缺少 device 宏而直接 `#error`。构建命令移除无来源的 `__ILUVATAR_WORKAROUND__`，保留 `__ILUVATAR__`、`__MR__`。
- 两种 kernel 都以 `page*16384 + head*128` 定位K页内head，descriptor stride 为256B，16行各读取128B，末行仍落在该4KiB head plane内；测试页0/3、head0/1均在4页输入缓冲区界内。CPU枚举 `slot∈[0,15], dim∈[0,127]` 得到2048个不重复stage byte offset，完整覆盖 `[0,2047]`。A按与NativeK8相同swizzle搬运；B两次`16x1b64_colxfb8`覆盖每行连续的两个64B区间，写到stage两个相邻1024B区。首/末page及两head均进入case矩阵。
- B在SME waitcnt后执行CTA barrier，再由全CTA dump shared；A使用CTA barrier。没有在异步传输完成前读stage的路径。独立probe内没有其他shared读写竞争，A每个stage word由唯一word循环迭代写入；B依赖两个intrinsic tile在stage中无重叠地完成写入，这由后续逐字节A/B与CPU比较门验证。
- C ABI的5个参数与wrapper一致：input pointer、page/head两个`unsigned`、output pointer、`cudaStream_t`；Python声明为3个pointer-compatible值和两个uint（`[c_void_p,c_uint,c_uint,c_void_p,c_void_p]`），返回void。调用传入当前Torch stream并在每次A/B后同步，因此未把默认stream假设混进比对。输入/输出guard、输入不变、CPU reference及A/B逐字节一致均逐case检查；任一失败即写FAIL_STOP并返回非零。
- 本地检查：`probe.py`通过`py_compile`；CPU swizzle/页范围断言通过（2048项唯一且范围完整）。未运行build命令，因此尚无host/device双pass编译或生成机器码证据；root后续构建需检查实际SME指令、waitcnt和两个tile地址确实落入目标shared范围，再决定是否启动探针。

结论：修正后可交给root做隔离CPU编译和封装审查；尚未通过编译或设备布局资格。输入文件SHA256：

| 文件 | SHA256 |
|---|---|
| `native_k8_sme_probe.cu` | `5fd67f998946c127ed814798cd9ebc8b055ea35e5e932d3047347c79f285d95a` |
| `probe.py` | `83a03ad165a5cfa76aa50105257635a7f7310f905b0d75722436c35479cc71bd` |
| `build.sh` | `51a6d5f50784644540bf859174cb9fd61a23ad2ab2384c9634c3ff08808231d0` |
| `run.sh` | `8bfde02ba5120f4ae43d2fc6141319b118f93899ab32bcfa1564bc43110f011c` |

传输前仅统一文本为LF，以上SHA已按相同源代码的LF原件更新；不改变代码语义。
