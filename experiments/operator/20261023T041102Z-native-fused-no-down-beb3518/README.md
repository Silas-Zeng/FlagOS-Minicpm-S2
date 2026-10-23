# 20261023T041102Z-native-fused-no-down-beb3518

来源：本机插件仓库分支 `codex/20261023-operator-fastpaths` 的 `experiments/biv150/20261023-fastpaths/`（其他 agent 产出，集成基线 = 团队 main `9a43eb1`）。

- 精度原件：`native-fused-no-down-accuracy.json`（0.9524，100/105）。
- 同族负结果：`native-all-rejection.json`（全层量化不可达 0.95）、`native-edge4-accuracy.json`（0.9429）。
- 融合对照：`native-fused-service-ref.log`（相对 FlagGems API 链 2.0×/2.36×，非服务 Inductor 链）。
- 吞吐 4K 5318.13 / 16K −8% 为用户转述，本仓库未独立复测，标注为未验证。
