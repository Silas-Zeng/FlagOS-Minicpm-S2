# GitHub 团队协作与交付

三个仓库均为本实验专用私有库。实验记录与分析按硬件平台区分；另外两个代码库由团队共用，不要求按平台划分目录或分支。官方上游只作参考，修改发布到自己的协作副本。

| 仓库 | 用途与范围 |
|---|---|
| [FlagOS-S2-Minicpm-throughput](https://github.com/Silas-Zeng/FlagOS-S2-Minicpm-throughput) | 实验、分析、原始记录、补丁、中文报告、子智能体交接。分别设置 BI-V150 和沐曦－曦云 C500 入口。 |
| [FlagOS-S2-vllm-plugin-FL](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL) | 共用框架源码与中文构建/复现说明。现有候选已在 BI-V150 验证，C500 仍需队友验证。 |
| [FlagGems](https://github.com/Silas-Zeng/FlagGems) | 共用算子源码，固定 v5.3.5。现阶段上游源码未直接改动，候选通过插件中的实现启用。 |

原公开 [vllm-plugin-FL fork](https://github.com/Silas-Zeng/vllm-plugin-FL) 按用户选择保留，不作为本次私有协作发布目标。两位协作者的用户名尚未提供，邀请仍待补充；没有向不确定的账号发出邀请。

## 已发布的代码身份

| 私有代码库 | 远端 main commit | 完整 Git tree | 核验文件项 |
|---|---|---|---:|
| FlagOS-S2-vllm-plugin-FL | `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c` | `82e37f8f263eeb09563a4790359ec95a0de1ca17` | 410 |
| FlagGems | `d7e5cef98344cd068df2e425748f849c94681048` | `e8ba50863b7bfabc725cc6aaff97d3548d7daf0f` | 4769 |

本地代码副本在 `collaboration/`，已配置私有 origin。为保留 upstream 内容，新增的协作首页使用中文，原首页另存 `README.upstream.md`，许可证、原源码、原文档和文件模式保留。插件的实现与冻结候选 tree `5c14cfb8d3a452e97a67758873bf18039e1bf989` 一致，仅两个首页文件不同；FlagGems 除这两个文档外与原 4df 一致。

由于本机 Git HTTPS 传输失败，使用已有 gh 登录的 Git Data API 上传快照。每个 blob 的字节和完整 tree 均验收，通过后才非强制更新 main；没有创建 deploy key。远端 snapshot commit 与本地保留上游历史的 commit 不同，tree 相同。不要直接强推本地历史覆盖远端 main；接入时从私有库克隆并在新分支协作。本地源码历史的浅边界与离线恢复见 [恢复说明](offline-recovery.md)。

本实验记录库以其 main 最新提交作为本轮交接版本。Git 只保存适合协作的文件；SQLite、trace、完整 ZIP 和本地源码镜像等按 `.gitignore` 保留在完整离线工作包中。原始证据路径已禁止 Git 换行转换，避免破坏 SHA 验收。GitHub 文本库不能替代离线原件。

## 交接范围

原版与候选官方测试均已完成，报告仅覆盖 BI-V150。中文正式报告见 [technical-report](technical-report.md) 和 `output/pdf/report.pdf`。原始基线的归档及逐项核验、DB/KV 差异、负结果和未集成原型都保留；C500 资料由队友补入 `platforms/metax-c500/`。

完整离线包位于 `output/handoff/`，同时保存 ZIP SHA256、成员清单及摘要；恢复时连同 `recovery/git` 的 bundle 和浅历史边界使用。子智能体结论与过程入口为 [交接索引](agent-work-index.md)。本轮结果作为稳定基点交团队审阅与独立复现；用户已恢复后续优化，小收益候选也安排最短上卡实测并保留，后续原件单独登记。
