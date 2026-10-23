# 原 Attention 硬件指标诊断

仅原 6f/C2/C3，D1/P2047、KV16K、随机物理页及共享旧 prefix；一次 KV 写入，8 次 warmup，采集 128 次原 forward。重复相同 Q，属于 warm-cache 合成诊断，不能当吞吐或候选收益。无 GEMM，不声称 DB 一致。

上传同目录 `diagnose_q_shared.py`、`worker.py`、`fixture.py`、`asset-pins.json`；C2/C3 可传既有原件。沿原 `ROOT/scripts` 依赖和干净 6f `PYTHONPATH`：

```bash
python diagnose_q_shared.py --run-dir /workspace/experiments/minicpm-s2/framework/<唯一UTC>-q-shared-diagnostic --runtime-path <e5f原C2> --mixed-path <a129原C3> --model /workspace/MiniCPM5-2B
```

controller 沿原锁、双 idle、monitor、300 秒超时、进程组清理，固定 `/usr/local/corex-4.5.0/bin/ixsys` 和 set 3 / 500 Hz / device 0；不改环境。worker 在区外完成源码/模型 pin、原 compiled metadata/IR 哈希与 observer 恢复；采样区只有原 forward，末端 synchronize 后 stop。全 KV bits、RNG、输出有限性与 padding 在区外检查；失败记录并尝试 stop/settle。源码、结果、命令、环境及 `native-trace.json` 由原 owner 封存。尚未部署；CPU 检查见 `cpu-check.json`。

framework 已只读新增 profiling/恢复窗口与 outer 包裹，无阻断；未重跑合同或设备。一次必要 CPU 静态检查 12 项通过、耗时 0.1774 秒。exit 0 不等于指标有效，须以原 trace 确认 set 3 是否实际提供所需带宽/吞吐数据。
