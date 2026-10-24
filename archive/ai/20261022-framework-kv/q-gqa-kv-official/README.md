# 原 KV422 官方性能接续

root 已启动 `20261022T231746Z-q-gqa-kv-swap-official`，唯一设备 owner；本目录只准备接线与封存，不启动其他任务。固定源为 `/workspace/experiments/minicpm-s2/code/q-gqa-kv-swap-20261022T213134Z`，完整 422 map 为 `82514a24…`，不是 allocator423、restore425 或单 H2D 候选。该 422 的独立准确率为 215836 的 103/105。

- 启动稿 `launch_q_gqa_kv_official.sh`：`c720998168374ea4b8a96f89b6aad010b3b26a56dc291e8f56324a71c9465f02`。已由 root 与 team 只读审阅；复用原 `run_official_gate.py` 79119f15 / common35d30dfa / benchmark0813eba5，不新增 owner。
- 原两负载为 `(4096,1024,64,256)`、`(16384,1024,64,128)`，各 4 轮，原 CSV 丢首轮、取 2–4 轮均值；SERVER、模型、参数不变。VERIFY0、finite unset、独立绝对 Q artifact ENV。
- 前次 414 官方运行实耗约 1 小时 3 分 29 秒，仅作排期参考；当前多波抢占和 slot 复用成本未知，仍保原 21600 秒上限。此次只报告 422 绝对结果，不与旧 DB 的 414 官方结果计算因果收益。

任务结束且原 owner 清理完成后，root 才手动执行：

```bash
python3 <assets>/seal_q_gqa_kv_official.py 20261022T231746Z-q-gqa-kv-swap-official
```

封存脚本 SHA：`d9a363ee14e4f5172b7df23c7e055f277ad76a1e272ee624def8e98e6dc773d8`。它只适配旧 sealer 的实际 run/source/map/launcher/VERIFY0 argv 与归档文件名；原八行 CSV、两摘要、2–4 轮均值验证及 CSV 字节、实际同 Engine Q/GQA marker、完整 DB 快照、源/installed 身份、所有 owned PID、双栈端口和 68MiB/0 清理门保留。它复用原 owner 的 CSV 验证，不重跑性能或判卷；既有输出存在即拒绝覆盖。

CPU 仅语法编译、精确逆回和不变函数 AST 核对，见 `sealer-static-check.json`；未执行封存 main、CSV 验证、SSH 或 GPU。Q/GQA Python marker 不覆盖 graph replay，协议安装 marker 也不证明全部事务覆盖；原协议日志须随原件保留，不能由本脚本替代完整事务判读。目前官方结果尚未完成。

team 已只读核对封存脚本相对旧 bf2ec87c 的 14 项身份替换，无新增阻断；未运行 main、CSV 或设备。
