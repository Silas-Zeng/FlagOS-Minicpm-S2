# 方法 PR 协作安排

GitHub框架main已恢复比赛原始源码13eb9be，恢复提交77bc2488。旧SQL+C3快照保留在codex/archive/sql-c3-imported-20261022；本地实验版本不受影响。所有下列PR均为Draft、未合并。

| PR | 方法 | 审阅基线 / 依赖 |
|---|---|---|
| [#5](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/5) | 默认关闭的实验诊断开关 | main；不作为性能收益，不借此改比赛参数 |
| [#6](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/6) | prefill Attention启动策略 | #5；会改已安装Attention，复现须隔离依赖 |
| [#7](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/7) | 确定性top-p | #6；共享安装入口的拆分 |
| [#8](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/8) | SQLite目标表反射 | #7；此顺序还原历史受测上下文，算法本身独立 |
| [#9](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/9) | 3D decode launch | #8；依赖prefill产生的受测Attention版本 |
| [#10](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/10) | mixed Attention天然前缀拆分 | #9；需要对应decode实现 |
| [#1](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/1) | CPU metadata复用 | #10；原受测head保留 |
| [#2](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/2) | async token更新 | #10；与#1并列，合并时保留两条helper import |
| [#3](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/3) | KV连续页复制工具 | main；独立新增文件 |
| [#4](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/4) | KV二维SAVE工具 | main；与#3无代码依赖，未默认接入服务 |

六项历史增量重建后的vllm_fl源码逐字节等于原受测SQL+C3快照；这只是拆包核对，不是新模型验证。CPU两PR各自仍仅3个变更文件，KV两PR分别2/3个，未把旧整包重新带入独立PR。

先评审前置项，前置合入后再更新后续PR基线；不要将整条链盲目批量合并。CPU两项已有组合真实方法门与64请求短测，但未做新整模型准确率。两KV工具的完成事件、引用生命周期及接入职责仍由调用方承担。

日常查看[方法实验记录](../team/README.md)，每个PR写明尝试、改动、测试、结果和是否保留。单项与组合证据分开，不把103/105或整体吞吐分配给单项。

其它本地探索、失败和未集成原型留在实验记录中；进入共享代码库时继续按真实方法PR呈现。FlagGems目前没有新增库内算子，不制造算子PR。精确head/tree和历史迁移回执放[归档](../archive/github/20261022-framework-rebuild.json)。
