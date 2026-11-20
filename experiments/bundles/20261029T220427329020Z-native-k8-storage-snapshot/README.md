# Native Adapter 单次调用 storage 快照候选

本候选只变更 main899 `vllm_fl/patches/biv150_konly_encoded_native.py` 中 `Adapter.validate` 的 host-side storage metadata 读取方式。通用 `storage(t)` 保持原实现逐字不变；只有 `validate` 显式传入局部缓存的 `bounds`/`overlaps` 路径会复用 backing-storage 范围。每次 `validate` 仍重新执行原来的 dtype、shape、stride、offset、bounds 和 backing-storage alias 校验；Tensor data pointer 与 storage offset 仍按原顺序各读取一次。不同 view 对象分别取 storage 快照，并分别用其自身 offset/shape/stride 验证。

这是函数级独立候选，未集成进当前pure-A/B overlay。main899该原adapter记录的namespace/SO身份为旧5898；当前受测载体pure-A实际是824f。不能借本候选改动放宽原source pins或声称已有当前完整载体；若CPU比较有信号，后续需由owner选择胜者源码物化、更新对应身份，再按该实际载体安排必要对照。

`prepare_candidate.py` 只接受仓库本地 frozen main899 原文件 SHA `957bc4bca3262e76c419ccd6fb77592da4967338223fc602797332077fe85579`（12913 bytes），然后在此目录生成 `baseline.py`、`candidate.py`、`candidate.patch` 和 `source-receipt.json`；不改冻结源码、overlay、服务包或生产入口。先运行：

```powershell
$py='C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -X utf8 tmp/native-k8-storage-snapshot-20261030/prepare_candidate.py
```

当前实现中，9 个 Native validate Tensor 先各过一次 bounds，随后24个 overlap pair 再读取两端 storage，合计约57次 storage 读取。按对象身份只读一次后，validate 路径最多9次。具体读取调用从57降到9次 `untyped_storage()`、114降到9次 storage `data_ptr()`、57降到9次 `nbytes()`；每个 Tensor 的 `Tensor.data_ptr()` 与 `storage_offset()` 仍各读一次。未传缓存的通用 `storage(t)`、`bounds(t)` 与 `overlaps(a,b)` 保持原调用路径，不增加读取或缓存开销。shape/stride/dtype与所有关系检查仍保留。该数量是源码调用计数，不代表端到端时间或性能收益。

快照只存在于一次 `validate` 的局部变量中；没有跨调用、跨请求、跨层或全局缓存。前提是这些 Tensor 的 storage/metadata 在一次同步验证过程中保持稳定。调用方若并发执行 `resize_`、`set_`、替换 storage 等修改，候选快照可能不再等价于逐次查询；此类并发修改必须继续视为不支持。candidate 不读取 Tensor 数据，不触发设备同步，不改 producer、路由、错误处理或 fallback。

## 后续 CPU 验证

`check_real_torch_cpu.py` 仅用真实 PyTorch CPU Tensor 比较冻结 helper 与候选 helper 的 bounds/alias 结果、错误类型和错误文本，并验证不同 view 仍分别缓存；另外以真实 `Tensor.set_` 替换 storage 后，确认新调用建立的新缓存看到新 storage。默认不计时。显式传 `--benchmark` 才会先通过正确性/别名门，再对9个真实 CPU Tensor执行同一组9个 bounds 与24个 overlap关系，以固定 ABBA/BAAB 顺序各计400次，输出每窗口原始ns与每调用中位数。K/scale/V共享底层storage，scratch彼此独立。此短测只表示helper路径局部CPU耗时，不代表完整Adapter、服务或设备收益。它不伪造 Torch；当前本机无 Torch时会明确返回 `not_run`/退出码2。待设备空档时，先在目标 Python/Torch环境离线执行，不启动服务、不加载SO、不初始化CUDA：

```bash
python3 check_real_torch_cpu.py
# 仅在需要局部CPU计时时显式选择：
python3 check_real_torch_cpu.py --benchmark
```

只有此真实CPU比较通过后，才值得讨论实际模块导入下 `Adapter.helper_binding` 的代码身份检查。当前没有 Torch CPU 运行结果、设备结果或性能结论；不得把静态AST/源码计数当成验证收益。
