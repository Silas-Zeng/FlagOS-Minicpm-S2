# GQA标量页基址：原while/原span单组件

未GPU。仅恢复原page16 while，把page load派生的scalar pointer与不含load的lane offset拆开；原NHD数据、2D同storage合法span、FP顺序、原reducer和N64/S2实际ABI均保留。不叠已负for，不改tile、guard、compiler或显式SME bit，无额外KV副本/布局变化。

固定021f AccelerateMatmul.cpp的isSafeSmePtrOffset要求含load的offset整体uniform；旧page+lane混合offset不满足。本候选scalar page-base单独为uniform offset，后继lane offset不含load。CombineAddPtrPattern只匹配相邻AddPtr，Splat隔开scalar/tensor层；ReorderBroadcast向内标量化、不展开scalar base。源码只是可证伪机制，不能替代本站C++binary与真实TTIR/ASM。

复用已核for-span worker的原8门、原FP64合同/Graph换值/side/RNG/DB/完整producer+reducer ABBA，仅新kernel引用、说明、跨臂逐位诊断。逐位诊断不篡改原硬FP64门。原base source/native14f/清理不变，CPU逆AST精确回旧while-span；旧for+span慢75.05%且实际SME0为反证，不能继续只凭mask62宣称成功。

root统一等当前官方结束并实查GPU/9031后，解包到独立scripts/gqa-scalar-page-base-component-20261026：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/gqa-scalar-page-base-component-20261026/entry.py --source-dir /workspace/experiments/minicpm-s2/code/20261026T013104Z-main34942f7-prefill-stride-official --native-library <已核14f原生库.so> --shape hotspot
```

只做该实际N64/S2一组。先核TTIR page-base是否仍scalar/Splat分层、hot-loop dot K/V真实SME copy/wait/ASM与shared/SGPR/VGPR/spill；若没SME，保留负机制事实不追加模型/参数扫描。数值或运行门错误立即停止；性能负按用户规则收尾。不代表模型准确率或官方收益。
