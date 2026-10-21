# CTA 服务与设备门的原 kernel 编译身份取证

本文仅覆盖天数 BI-V150 的固定 MiniCPM5-2B gate-up 配置；沐曦－曦云 C500 由队友验证。hardware_innovation 只在本地 CPU 读取已归档文件，未重新编译、导入远端模块或运行设备。

## 结论与适用边界

CTA 服务 `182916` 的原 kernel hash 为 `23d5fd23898e6eecfef38a539119ea5fd5e8f41ebc68639dc48b0685e0b69a51`，设备门的原 kernel hash 为 `3639b8c97b8a4342970c3964dbabb29a1242f519fa9ad59761253a59d4346b5a`。实际缓存证据表明：两者编译参数完全相同，可执行和所有加载段内容相同，二进制文件差异只在 `.debug_info` 和 `.debug_line`。这两个已归档条目的 hash 差异不代表执行数学或机器码不同。

该结论只针对本次取回的条目与固定配置，不能推广成所有 hash 差异都无关紧要，也不替代新形状、完整模型准确率或设备验证。group8 服务与设备门实际编译 hash 均为 `08afb5451fca98d698022dd9770db694d9e3786dbf3e4215e1a660a8b8e8305f`。

## 证据与可复核方法

原件目录为 `experiments/source-audits/20261021T183920Z-compiler-cache/`，由 root 等设备空闲后一次只读取证。包 SHA256 为 `eb19121a54593fa3e52b37ec41900487c656f7398a65e09ddb061f23ac9587c6`；原 collector 精确 SHA 为 `685e6d107f8d96fe5bd5e4f67bb15b5313ec4ee946a2e6a63ea89b17992b892b`，保留在该目录的 `collector.py`。后来的本地 `02187d04…` 版本只增加环境白名单，未执行，不能替换本次 collector 身份或旧证据。

复核脚本为 `analysis/source/mm-cta-group/review_compile_cache.py`，SHA256 `8d9a7b9d17da7996e084fa6f53a224998b3db717455d6f2f4a50585dc5a220d5`；结果为同目录 `compile-cache-review.json`，SHA256 `0324315287afd29e112690aec6f8ae5a0e048bda7504b6c3a7a55b41046fe960`。脚本仅使用 stdlib，已实际运行一次，核过 manifest 中 32 个源码和缓存文件。

| 逐层核对 | 实际结果 |
|---|---|
| 编译 metadata | 仅 `hash` 字段不同；target、warp、stage、所有其它选项相同，`use_sme=7` |
| 原函数体 | 从 `def` 到函数结束 bytes 相同，SHA256 `ac913442cb9a88e781f94645b7b11be73a0c776adf1cd1567aabcb6b2a90acc0` |
| `.source`、`.ttir`、`.ttgir` | 只去掉 `#loc… = loc(…)` 调试定义后逐 byte 相同，没有删除操作行 |
| `.llir` | 只去掉 `DIFile`、`DISubprogram`、`DILocation` 源码调试定义后相同 |
| ELF64 section | 所有 `SHF_ALLOC` 段的 payload、type、flags、size 相同 |
| 可执行 `.text` | 8,016 bytes 完全相同，SHA256 `e29f72a3564ca0df74e94467a37cddae274641914f3655a1bda65385a4425210` |
| 整个 cubin | 服务 12,360 bytes、门 12,368 bytes，只有两个非加载调试段不同 |

原函数在真实 mm 文件的首 decorator 为第 50 行、`def` 为第 78 行；门提取后首 decorator 为第 20 行、`def` 为第 21 行。安装版本的 `installed-triton/spec/iluvatar/triton/runtime/jit.py:503` 通过 `inspect.getsourcelines` 记录起始行，`:549` 将 `starting_line_number` 显式纳入 JIT cache key。此处的不同源码身份、调试位置与最终二进制调试信息差异一致，而可执行内容已单独比较相同。实际 spec JIT SHA 为 `66a168ae959e719186771e66815e807f1e449e66c5283ef596ec3eb0e35cb775`，不是用网上版本代替实机版本。

[Triton v3.6.0 JIT 源码](https://github.com/triton-lang/triton/blob/v3.6.0/python/triton/runtime/jit.py)、[编译器源码](https://github.com/triton-lang/triton/blob/v3.6.0/python/triton/compiler/compiler.py)和[缓存实现](https://github.com/triton-lang/triton/blob/v3.6.0/python/triton/runtime/cache.py)只作机制参考；本机结论由上述 actual spec 源码和缓存决定。

## 服务状态

`experiments/framework/20261021T182916Z-mm-cta-group-context16k{,-control}` 已归档，包 SHA256 `96074323f386817d460bdefd0982c44ba5f58c3f760c07c0e81604364215ccac`。root 回执 32/0、118.41752643 秒、KV 容量 521840，DB 三项 SHA 未变。本 owner 实核 control 的 413 项源码 SHA、每 PID 产物和实际模型日志：`REAL_SELECTED delta=42 total_scheduled=2048 num_requests=1`，证明目标模型真实执行命中，不只是 dummy 编译。

`status.json` 为首个真实命中时的快照，不是服务 TERM 后的最终总量。此单次完成时长还没有在本文建立因果性能结论；匹配 baseline、冷热状态和完整原件比较由 root 负责。保留 gate-up 正信号及 down 负结果，不据本次 hash 审计扩大启用范围。
