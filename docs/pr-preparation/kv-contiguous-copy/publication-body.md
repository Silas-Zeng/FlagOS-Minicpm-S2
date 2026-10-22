逐页复制 KV 会产生较多 API 提交。本改动提供显式调用的连续页合并复制工具，在保留逻辑顺序和原始字节的条件下，将连续页合并为复制段。提交只含工具模块与中文说明，由后续调用方决定接入位置。

已有 BI-V150 字节门覆盖 normal/packed 布局、连续与分片页序。工具只提交复制；producer 依赖、完成事件、对象生命周期、页所有权和失败后的等待由调用方负责。当前没有默认服务接入或端到端吞吐声明，保留 Draft，C500 未验证。

共同基点为 `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c`。与二维 SAVE 工具无代码依赖，新增路径独立，可任意顺序评审合入；不改初始化入口、serving 参数或完整 KV 协议。

详见本分支的 [中文方法说明](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/codex/20261022-kv-contiguous-copy/docs/kv-contiguous-copy.md)及实验库的[源码与证据清单](https://github.com/Silas-Zeng/FlagOS-S2-Minicpm-throughput/blob/main/docs/pr-preparation/kv-contiguous-copy/manifest.json)。
