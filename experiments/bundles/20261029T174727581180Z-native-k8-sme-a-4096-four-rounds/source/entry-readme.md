# NativeK8 SME 服务接入准备

材料基于声明的 main899 `899ce77470b0b539aebc108fd122f668c2d5894d`。组件 dispatcher A/B 已通过最小服务边界测试：A SHA `824f7dda043dd8e101b0f2296cba4aeda14d0718ae673805da1564a141c1f734`，B SHA `bdc16c49fef721b5dad7d7627f9c046f726f29a2f9c589297b9f4f036b08b6ef`；各自 namespace 为 `cjj_native_k8_klookahead_probe_a/b`。这只证明 codec、dispatcher 参数边界、A/B 数值、side-stream 和 changed-Q Graph，不是模型服务或准确率验证。

`materialize_adapter_overlay.py` 从干净 main899 源树生成一个 arm 的私有替换文件和哈希清单，不修改源树。示例：

```powershell
python tmp/native-k8-sme-component-20261029/service/materialize_adapter_overlay.py `
  --main-root tmp/framework-main899-shallow-20261029 `
  --out tmp/native-k8-sme-component-20261029/service/generated-A `
  --role A
```

B 臂把输出目录改为 `generated-B`、`--role B`。将清单中三个 `vllm_fl` 文件复制到隔离的 main899 服务源副本，保留其他源码与库不变。这个 overlay 只替换 NativeK8 adapter、compile fingerprint 与来源清单；身份分别绑定新 SO SHA 和新 dispatcher namespace，绝不修改旧 5898 资格记录。

可用已存在的 PR105 W8A8 `14f4457a…` 和 stock GQA `c8a725da…` 作为两臂共同的服务依赖，`VLLM_FL_BIV150_KONLY_MIXED_NATIVE=0`，encoded service 与 NativeK8 显式开启，A/B 分别加载新 SO。保持 MiniCPM5-2B、标准服务命令、官方 benchmark 参数和同一冻结 DB 起点；每臂使用独立 DB 副本并比较/恢复到同一 SHA。该载体仅用于声明的 main899 A/B 对照，不能称 PR118 成绩、PR118 复现或 main118 结果；也不代表准确率/正式资格通过。

`owner.py` 是本实验专用薄封装，原样调用冻结的 `run_official_gate.py`，只把其 `TEST_CASES` 设为一个官方负载，并在原 `wait_ready` 成功后追加 NativeK8 install 身份检查。每次调用只跑所选负载的完整四轮，保留原 benchmark、服务命令、弃首轮口径、端口/GPU preflight、设备锁、输出校验、DB 前后快照和进程清理。A/B 必须分别使用新 run 目录；owner 会从同一 tuning snapshot 为每臂复制独立数据库到独立 cache 的 `config_cache`，并把实际副本路径交给官方 driver，不改全局 DB。官方 driver 自己持有 `framework-device.lock`，不要在外层重复持锁。

远端准备完成后先执行 `--prepare-only`；这会核验 415 项 main899 源清单、overlay 三文件、库与 DB 哈希、官方 driver/common/benchmark 哈希，不导入 CUDA。下例适用于 A 臂 4K；B 臂将 `A` 改为 `B`，16K 将 prefill 与新 run 目录改成 `16384`。主线负责先跑 A 的四轮、回收完成后再运行 B：

```bash
python3 /workspace/experiments/minicpm-s2/service/owner.py --prepare-only \
  --arm A --prefill 4096 \
  --source /workspace/experiments/minicpm-s2/code/native-k8-sme-service-main899-e717ec99-20261029 \
  --source-archive /workspace/experiments/minicpm-s2/cpu-probes/20261029T172942504792Z-native-k8-sme-service-common/main899-source.tar.gz \
  --base-manifest /workspace/experiments/minicpm-s2/cpu-probes/20261029T172942504792Z-native-k8-sme-service-common/main899-source-manifest.json \
  --overlay-manifest /workspace/experiments/minicpm-s2/code/native-k8-sme-service-main899-e717ec99-20261029/native-k8-sme-overlay-A.json \
  --common-assets /workspace/experiments/minicpm-s2/cpu-probes/20261029T172942504792Z-native-k8-sme-service-common/common-assets.json \
  --tuning-snapshot /workspace/experiments/minicpm-s2/cpu-probes/20261029T172942504792Z-native-k8-sme-service-common/tuning-snapshot \
  --native-library /workspace/experiments/minicpm-s2/cpu-probes/20261029T172942504792Z-native-k8-sme-service-common/libraries/libnative_k8_sme_dispatch_A.so \
  --gate-library /workspace/experiments/minicpm-s2/cpu-probes/20261029T172942504792Z-native-k8-sme-service-common/libraries/biv150_native_w8a8.so \
  --native-gqa-library /workspace/experiments/minicpm-s2/cpu-probes/20261029T172942504792Z-native-k8-sme-service-common/libraries/corex_native_gqa_s2_probe.so \
  --driver /workspace/experiments/minicpm-s2/service/reference/run_official_gate.py \
  --common-dir /workspace/experiments/minicpm-s2/scripts \
  --benchmark /workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py \
  --database-name TunedConfig_iluvatar_triton_3_6.db \
  --run-dir /workspace/experiments/minicpm-s2/official/native-k8-sme-A-4k-NEWUTC

# 所有参数不变，先将 --prepare-only 换成 --run，再换 B/A 的臂身份和全新 run-dir。
```

`--run` 结束时 owner 写入 `native-k8-sme-owner-result.json`，其中区分 `host_or_capture_events`，不声称请求频率或 Graph replay 次数；官方四轮 CSV 与 `result.json` 仍由原 driver 生成。此隔离载体是 main899 上的新 A/B 实验，不是 PR118 复现或 main118 成绩，也不继承旧库的准确率/正式资格。性能结果需结合已验证的数值组件和后续准确率单独判断。
