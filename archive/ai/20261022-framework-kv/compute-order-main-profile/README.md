# 当前 main 的计算序候选

基点固定 `3283672b92fa30f93f652b242193999836a95f88`，原 tree `a6e53d5219addc76700718880f86c33ab014b311`。445 个 Git blob 仅替 runner、增加 compute helper，输出 446 个 blob，tree `5c77e68caff6aa0c8b6c230adb78a2d4c293cca1`。完整声明见 `candidate-manifest.json`、`candidate-git-blobs.json`；`production.patch` 为两文件生产补丁。

runner `183de0ab` 复用旧 P 的 14 处切口，保当前 main 全部 footer、原 `_sample` 与其余方法。helper `5bc850eb` 仅替来源 profile：严格识别 normalized → GQA → generic 链、已安装 L=0 clone 及 C3 的实际绑定；C500/未知平台在 torch/capture 前回原路。Plan 算法、输入/采样顺序及未知 scope 拒绝均沿用。没有 PR15、实验 Q/KV、诊断或算子修改。

上传本目录 `launch_compute_order_main.py`、`main-tree.json`、`candidate-manifest.json`、`files/` 两路径，复用基线的原 main tar：

```sh
python3 <assets>/launch_compute_order_main.py \
  --archive <baseline-assets>/current-main-3283672b.tar.gz
```

启动器 `88b35410` 只在新 source 解包原 tree，再核两文件与完整输出 map；其余沿 `571a9690` 的 bc51 context-screen/seed721201、SERVER、6CPU、锁和清理。安装门仍为 normalization install；同 Engine 的 `BIV150_COMPUTE_ORDER_FIRST_SELECTED` 与实际 normalization 选择须结果后验。任何 DB/KV 失配不宣称严格收益。

`static-check.json` 记录本次 CPU compile、14 切口逆回、Plan/采样 AST 不变及启动器精确逆回；原 tar 全树核验复用 `tmp/current-main-baseline/tar-check.json`，未重复测试/导入模型/运行设备。历史 +5.124857% 单 pair、结构门和三题 P 路径质量只是旧栈证据；当前 normalized main 的实际命中、性能、完整准确率尚待独立验证，不能继承为已通过。
