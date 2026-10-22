稀疏 KV 源页中的正等差段可合并为二维 D2H 提交。本改动提供页序规划、Python adapter 和 Corex SDK C++ 批量桥，保留全部原 KV 字节及逻辑顺序，并补充中文编译和调用说明。

已有 BI-V150 两组真实页序字节门及三路短对照通过，同桥线性→二维的单层热 wall 小信号约 **3.62%**。独立实验 worker 的 42 层诊断保存 717717504 B，API 提交从 966 次降至 210 次，源释放前独立对照及恢复后回读均通过。该完整 worker 不在本 PR 内；这些结果不代表端到端吞吐提升，保留 Draft。

SO 需从 Git 源码按实际 Corex SDK 编译。调用方负责 producer 依赖、stream、全部强引用、真实完成事件及失败后的等待。当前验证范围为 cuda:0、normal 16 KiB 页、单层或 42 层、payload 不超过 1 GiB；C500 未验证。

共同基点为 `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c`。不依赖连续页复制 PR，可任意顺序合入；不改默认初始化入口、setup 或服务参数，不包含 SO 与完整 KV 事务。

详见本分支的 [中文方法说明](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/codex/20261022-kv-pitched-copy/docs/kv-pitched-copy.md)及[源码与证据清单](https://github.com/Silas-Zeng/FlagOS-S2-Minicpm-throughput/blob/main/docs/pr-preparation/kv-pitched-copy/manifest.json)。
