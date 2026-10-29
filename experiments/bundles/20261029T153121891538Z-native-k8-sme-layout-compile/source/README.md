# NativeK8 K-page SME 布局等价探针

仅比较既有 NativeK8 `issue_k_i8` 的完整16-slot页 shared stage，与两条 `__ivcorex_sme_load_16x1b64_colxfb8` 传输后的 stage 是否逐字节相同。A/B 都将2048B stage dump到带guard的输出；CPU reference、输入不变和输出guard也会检查。覆盖0、-127、127、固定seed随机值，两head及首/末合法page；不测partial page、不运行Attention、不计时或报告吞吐。

这只是布局/搬运一致性探针，不改生产代码。B路径由shared-stage写入导出结果之前等待 `__ivcorex_sl_waitcnt(8ULL)` 并做CTA同步。任何case不一致即停止并保存 `build/probe-result.json`；不要通过猜测布局反复修改实现。GPU运行需由root显式调用 `run.sh`，本次准备不编译、不加载库、不启动设备。

目标固定为BI-V150 `ivcore11`。`build.sh` 只编译隔离 `.so`，不执行GPU代码；它记录准确命令、日志和源码/产物SHA。独立的 `run.sh` 才会延迟导入Torch并launch A/B。

编译命令主体：

```bash
/usr/local/corex/bin/clang++ -D__ILUVATAR__ -D__MR__ -D__ILUVATAR_WORKAROUND__ \
  -O2 -std=c++17 -fPIC -x ivcore --cuda-gpu-arch=ivcore11 \
  --cuda-path=/usr/local/corex -shared native_k8_sme_probe.cu \
  -L/usr/local/corex/lib64 -lcudart -o build/libnative_k8_sme_probe.so
```
