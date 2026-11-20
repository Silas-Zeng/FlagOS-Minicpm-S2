# RoPE＋KV 同服务模型验证

只运行一个原参数服务，沿用四个语义请求（85、323、12、95；最后一个要求至少 4096 prompt tokens），随后读取本服务实际 FX/AOT。要求 42 个融合 op、零个旧 KV update、每层 Q/K/dep 连到同层原 Attention，并保留 34 个 native 层 4–37。首次接受当前源码指纹对应的真实新建或加载 AOT，不借用旧 526 图；后续显式 `--prior-control` 才要求加载已验相同图/AOT。

来源为 main0bf9 的独立 528 文件版本，tree `57bb317de9d9040e3e52b27dc3b91ecc52eaae5e`；生产源码包在 `../rope-kv-model-candidate/source.tar`，SHA `2db1a73e45d76ba35fb1c308703c87456d2f26190a5ce79640e1c7b924fc261f`。原 native SO `14f4457a…` 与真实 7596/b375 构建凭据从成功 161030 main526 control 复用，构建源逐文件与候选核同，不重新运行未变的 49 项组件。

```bash
python3 verify_service.py \
  --source-dir /workspace/experiments/minicpm-s2/code/替换为已解压528源码目录 \
  --performance-control /workspace/experiments/minicpm-s2/official/20261024T161030Z-main0bf9-main-official-four-rounds-control
```

主智能体显式安排上卡。入口持有原设备锁，全程仅一个服务；实时检查卡和 9031，保留源码、环境、命令、PID、GPU 采样和请求原件。正常/异常均停止自己的进程组，最多 6 秒宽限后再次确认设备空闲，再保存 DB-after 并恢复 DB-original。任何清理或身份错误返回失败，不覆盖旧证据。

新增标准库 CPU 夹具 8 项见 `cpu-check.json`：实际 typed FX 风格、返回与层号映射及错误拒绝。它们不是实际设备图证据。本入口未上卡；不运行 32 请求 KV swap、不运行官方性能、不替代最终 105 题准确率。复用已核的原 `35d` SERVER/ready、`8de` 语义解析/组清理、`88f` main526 资格。

独立增量审阅已通过：community 核真实图与复用门，teammate 核单服务来源、锁、DB 和异常收尾；未重复旧组件或设备测试。实际 528 Torch 输出图与模型正确性仍待本次执行。
