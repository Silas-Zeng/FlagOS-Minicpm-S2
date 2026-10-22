标题：增加显式调用的 KV 连续页合并复制工具

已有 KV 页映射中，源和目的同时连续的页可以合成一次异步 `copy_` 提交。本 PR 增加保序的 raw-byte 规划/复制工具及中文使用说明，源码保持已测 c95f 版本逐字不变；不接入默认服务或改变 scheduler/模型参数。

变更仅两项：

- `vllm_fl/patches/biv150_kv_page_copy.py`
- `docs/kv-contiguous-copy.md`

已有 BI-V150 四 case 设备门覆盖 normal42/packed42 与连续/8-run 映射，每方向 672 MiB，全字节、guard 和 RNG 检查通过。原 wall/event 波动保留，未声明服务吞吐收益；本次 PR 准备只核源码字节与语法，未新增设备测试。

返回值是提交信息，完成 event、资源生命周期、页所有权与失败 settle 必须由调用方负责。没有增加默认 hook、SO、依赖包、README 改动或完整 SAVE/RESTORE 协议。

基于团队 `main`：已发布提交 `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c`，tree `82e37f8f263eeb09563a4790359ec95a0de1ca17`；本地同 tree 历史提交 `70d04f38382e900949ddeb34d2ac75aacdc93af4`。无前置 PR，与二维 SAVE 工具可任意先后合入；单独回退只删除本 PR 两个新增文件。
