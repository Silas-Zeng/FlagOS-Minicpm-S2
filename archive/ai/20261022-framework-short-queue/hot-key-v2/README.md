# hot-key v2：保留原 hook/launch 尾部

085923 与 100149 均未命中 fast path；100149 仅首次 CPU 日志证实两 launch hook 非 None。root 实读安装 `knobs.py`（`233f2698…`）后确认默认为 `HookChain` 对象，即使 calls 为空也非 None/truthy；原 guard 因而恒拒，不能解释为性能负收益。KVQuantMode 是 IntEnum，NONE=0，原 `!=0` guard 正确，没有放宽。

新版只用 recipe 替换精确原 run 的 `compute_cache_key` 和 `kernel_cache.get` 两行；probe 返回 key/compiled，不提交。原 cache miss、globals 校验、grid、metadata、当前 hooks、run、返回值和异常尾部均保留原 AST；两 IS_3D kernel 槽/reducer 单槽与其他 guard 不变，仍默认关闭。没有取消或缓存 hook。

policy `a67d3add779387331edcccffd863f1e1b70b76d0ffaf98cebdb8ac69f9458ac7`；gate `1f402c6d0d2de2de7c69e688028648fdc1f4f0e875264c570c3480555864acd4`。`check_hook_tail_cpu.py` 与 `cpu-hook-check.json` 为唯一新增 CPU 合同/实际通过回执：对比真原 run AST 的非 None hook、metadata、顺序、原二维 grid、新参数/stream、globals 和异常无重试。使用 CPU stub，不证明实际 hot 资格或 GPU 数值。门只是原两 case/32ABBA 换 policy pin，尚未执行新版设备门。

原 `tmp/next-hot-launch`、`tmp/hot-key-diagnostic` 以及正式受测文件均保留。下一步 root 串行运行新版短门；必须真实 bootstrap/hot 命中、两形状数值/KV/RNG及新指针/流通过后才解读计时。C3 view 独立线已交 hardware owner 继续，不与此方法叠加。
