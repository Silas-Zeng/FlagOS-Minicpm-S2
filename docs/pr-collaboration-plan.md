# 方法 PR 协作安排

GitHub 框架以比赛原始源码 13eb9be 为起点，以下十项 PR 已按依赖顺序合并：#5→#6→#7→#8→#9→#10→#1→#2→#3→#4。随后通过 #11 更新中文 README。当前 main 为 `87ed53719126208eaa9ba1cab698b14a5693eb5d`；旧 SQL+C3 快照及历史继续保留。

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

合并时逐项更新后续 PR 基线并固定 head。#1/#2 的 runner 冲突已采用原受测组合 `6f918ae6…` 解决，两个 helper 及各自回退均保留；全部 425 个文件与预期组件组合完全一致。按用户要求复用已有验证，没有重复测试。CPU 组合仍未做新整模型准确率，两 KV 工具的完成事件、引用生命周期及接入职责仍由调用方承担。

日常查看[方法实验记录](../team/README.md)，每个PR写明尝试、改动、测试、结果和是否保留。单项与组合证据分开，不把103/105或整体吞吐分配给单项。

其它本地探索、失败和未集成原型留在实验记录中；进入共享代码库时继续按真实方法 PR 呈现，后续维护也通过 PR。FlagGems 目前没有新增库内算子，不制造算子 PR。精确合并顺序、冲突处理与最终身份见[合并回执](../archive/github/20261022-framework-merge.json)，此前重建过程见[历史回执](../archive/github/20261022-framework-rebuild.json)。
