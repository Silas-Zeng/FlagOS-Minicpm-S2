标题：增加显式调用的 KV 正等差二维 SAVE 规划与 SDK 批量桥

稀疏源页中的正等差段可在保留全部原 KV 字节及逻辑顺序的条件下合为二维 D2H 提交。本 PR 提取已测 818e planner/adapter 和 0a4d C++ 桥，补中文范围、源码编译和调用方完成契约；不包含 SO、完整 SAVE/RESTORE 协议或默认启用代码，不改 setup/README/serving 参数。

变更仅三项：

- `vllm_fl/patches/biv150_kv_pitched_copy.py`
- `vllm_fl/patches/biv150_kv_pitched_bridge.cpp`
- `docs/kv-pitched-copy.md`

已有两组真实页序单层字节门和三路短控制通过；同桥线性→2D的单层热 wall 小信号约3.62%，不外推 E2E。后续独立 BI-V150 42层诊断保存717717504B，原966→210次API提交，源free前独立对照及恢复后回读通过；该调用方不随本 PR 交付，诊断不作吞吐成绩。本次准备仅核源码字节、语法与依赖，未新增设备测试。

SO须从Git源码按实际Corex SDK手工编译并固定SHA；原生接口只提交，调用方必须保 producer依赖/当前stream/全部强引用/真实完成事件，提交异常先settle，不允许静默旧路重试。当前只支持cuda:0 normal16KiB页、单层或42层、总payload≤1GiB；C500等其他平台未验证。

基于同一个团队 `main`：已发布 `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c`，tree `82e37f8f263eeb09563a4790359ec95a0de1ca17`；本地同tree历史提交 `70d04f38382e900949ddeb34d2ac75aacdc93af4`。静态依赖只含标准库和实际 SDK，**不依赖连续页复制 PR**；两者可任意顺序合入。单独回退只删除本 PR 三个新增文件。
