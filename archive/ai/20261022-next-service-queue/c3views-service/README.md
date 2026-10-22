# C3views 真实服务最短门

**状态：CPU 准备与新增接线合同已通过，硬件职责 owner 只读互审无阻断，ready；尚未部署或运行服务。** 只适用于本轮 BI-V150，C500 未验证。基线为当前 `6f918ae6…` 组合；不叠 hot-key、输入等待诊断或新 CPU gather。

- **尝试：** 将已通过短输入门的 C3 重复 view 清理接入真实服务。105635Z 的 D29/P128/KV1024 微测 wall 为 0.460218→0.432737 ms（省 5.9714%），event 省 0.6663%；这不保证端到端收益。大混合 shape 的负结果仍保留。
- **改动：** `prepare_c3views_service.py` 仅在原 C3 安装末尾追加两行，并新增 `vllm_fl/patches/biv150_c3_view_reuse.py`。已测 policy core `ba085577…` 逐字节保留；其数学、scope、stream 依赖、scale 和原 fallback 不变。服务附加段在 `service_append.py`，不新增 GPU 操作。`ModelRunnerFL.execute_model` 首次成功返回且该次 selected 增量为正后，打印一次带 Engine PID 的证据，随后恢复原 execute 方法；启动/dummy 历史计数不能充当命中。
- **怎么测：** 原 `bc51ac2d…` driver，`--decode-screen --seed 721201`；输入4096、输出128、64请求、并发64，服务与 benchmark 参数不变。baseline/candidate 由同一干净完整6f源码分别复制，差异仅 runner 尾安装和新增 policy。单卡由 root 串行执行，保留原 driver 锁、GPU/9031 实时前置检查、源文件清单、DB前态和清理；不改变调度去强迫 D29/P128 出现。
- **结果：** `cpu-check.json` 只覆盖新安装、异常/回退接线、真实 execute 首次证据、撤销观察包装及完整副本差异；412→413文件，只两路径不同。未重复原 C3 合同，未运行 GPU。
- **是否保留：** 保留待真实服务判别；必须同时有实际命中、请求成功及可比基线，再讨论端到端效果。没有 marker 或负收益按实记录；不能用启动安装记录、微测或一次服务差异声称稳定收益。

远端将以下5个文件放入同一新目录：`launch_c3views_service.sh`、`prepare_c3views_service.py`、`biv150_c3_view_reuse.py`、`service_append.py`、`check_actual_selection.py`。root 选取已核对的完整6f source，逐个运行，前一个完成且设备空闲后才运行下一个：

```bash
bash <assets>/launch_c3views_service.sh baseline <完整6f组合source>
bash <assets>/launch_c3views_service.sh candidate <同一完整6f组合source>
python3 <candidate-control>/check_actual_selection.py <candidate-run>
python3 /workspace/experiments/minicpm-s2/scripts/seal_framework_screen.py <run-id>
```

原 driver 的 `--require-log-marker` 仅检查启动安装；**候选完成后必须另外运行 `check_actual_selection.py`**。它要求原短筛 exit0、恰一条真实 Engine PID 命中记录，输出 `c3views-actual-selection.json`。命中只说明至少一次真实步骤，不能视为全程覆盖率。首次 marker 和观察包装有少量 CPU 成本，之后 execute 恢复原函数；不对这点开销做校正。

现场对比还需核64成功/0失败、DB/KV、显存与主机负载；本包不自动将这些条件视为匹配。必要封存仍复用现有 `seal_framework_screen.py`，可读本 launcher 的 `purpose.json`、`source-sha256.json` 与 `plugin-source/`。

精确身份：

| 文件 | SHA256 |
|---|---|
| 原 runner | `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141` |
| 候选 runner | `806100175e62093870adc7457920491b6836ebf7630155cb6c39696b76b6b255` |
| 已测 policy core | `ba085577f24684cb980cdd09c2978192ff9b8b3a70fa62aadc1cfd3efced61d4` |
| 含服务接线的 policy | `c70542e65eee4a184ea79a83d16a5bd0607ae6dac4712b618840a7a3e9ef20da` |

本地唯一 CPU 检查命令为 bundled Python 运行 `check_service_install_cpu.py`；检查已通过，完整调用与副本身份存于 `cpu-check.json`。该检查生成新目录，不能原地重跑覆盖。新增实现若进入协作代码库须按方法提交中文 PR；当前仅 tmp 隔离准备。

跨职责只读互审已通过：确认原 policy 字节不变、C3 后安装、原 execute 调用恰一次且异常透传、dummy 不构成增量、成功真实 execute 增量才记录且撤观察包装、安装失败可恢复；未重跑合同或设备。`complete_step_return` 指原方法返回，并非新增设备完成 ACK；DB/容量/环境仍由原封存流程核对，单条 marker 不代表全程覆盖。
