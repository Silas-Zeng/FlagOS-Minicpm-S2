<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# native SiLU相邻两列访存

相邻两列用int2/float2读取并打包写回BF16，尝试降低尾处理地址/访存及CTA开销，原量化/GEMM/舍入顺序保持。BI-V150随机M2048/N12288/K2048，15个数值/Graph case及独立CPU参考通过；隔离尾处理Event慢6.9849%、完整gate慢2.4404%，均无净收益。只加载私有测试库，未接模型或替换生产native；停止此候选。实验PR52已创建为Draft并于15:01:05 UTC关闭，未合并；仅保存原组件实现与教训，不改生产路径。

相关代码：[native_w8a8.cu.diff](../../experiments/framework/20261025T143942955934Z-native-silu-vec2-component/source/native_w8a8.cu.diff)；[native_w8a8.cpp.diff](../../experiments/framework/20261025T143942955934Z-native-silu-vec2-component/source/native_w8a8.cpp.diff)；[worker.py](../../experiments/framework/20261025T143942955934Z-native-silu-vec2-component/source/worker.py)；[asset-pins.json](../../experiments/framework/20261025T143942955934Z-native-silu-vec2-component/source/asset-pins.json)。

相关方法PR：[SiLU vec2负结果 #52（已关闭，未合并）](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/52)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261025T143942955934Z-native-silu-vec2-component](../runs/bi-v150/20261025T143942955934Z-native-silu-vec2-component.md)（登记#275）：15case逐位/finite/guard与Graph通过；隔离Event0.216360→0.231472ms慢6.9849%，完整gate0.712861→0.730258ms慢2.4404%。 **是否保留：** 停止模型推进；实验PR52已关闭、未合并，不改生产csrc，不授模型/官方资格。
