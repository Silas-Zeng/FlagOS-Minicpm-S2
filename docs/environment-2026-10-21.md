# 环境记录：2026-10-21

本页仅记录天数BI-V150实例，不是团队双平台环境总表。沐曦－曦云C500由队友负责；实验分析库按平台归档，两个私有代码库共用。下文初始“双卡预期”属于该实例的历史观察。

以下保留初次环境快照与当时观察。路径、版本、哈希保持；最终SQL+C3还需结合正式manifest，历史后端观察不是最终路径声明。

## 连接记录

- 入口：FlagOS SSH网关。
- SSH认证：本任务专用Ed25519密钥。
- 公钥指纹：`SHA256:YBsnxjMuO8HB3V9pbejfv7EabmMZ0Umjvy2ffGkH6bM`。
- 容器主机名：`000cf2952330`。
- 容器用户：`root`。

仓库不保存私钥或连接秘密。

## 主机与运行时历史快照

| 项目 | 当时观测值 |
|---|---|
| 内核 | Linux 5.4.0-148-generic x86_64 |
| 宿主可见系统内存 | 503 GiB |
| 容器内存限制 | 20 GiB（`memory.max=21474836480`） |
| 平台CPU配额 | 6 CPUs |
| 宿主可见CPU | 112（`nproc`） |
| Swap | 8 GiB |
| 容器根文件系统 | 50 GiB overlay |
| 加速器 | Iluvatar BI-V150 |
| 容器可见设备数 | 1 |
| 设备显存 | 32,768 MiB |
| 设备UUID | `b18272be-ac3a-5ec1-80d8-eed9d1d1b3ab` |
| PyTorch报告的计算能力 | `7.1` |
| 多处理器数量 | 16 |
| L2缓存 | 16 MiB |
| 驱动 / IX-ML | 4.5.0 / 4.4.0 |
| CoreX | 4.5.0 |
| Python | 3.12.11 |
| PyTorch | 2.10.0+corex.4.5.0 |
| Transformers | 5.14.1 |
| vLLM | 0.24.0+empty |
| vLLM plugin FL | 0.3.0rc0+g13eb9be69 |
| FlagGems | 5.3.5 |
| FlagTree | 0.6.2a3+iluvatar3.6 |

初期FlagGems报告vendor=`iluvatar`、device type=`cuda`及`use_c_extension=False`；当时观察的FlagGems Attention为`flag_gems.ops.flash_api`中的纯Triton实现，而非可选C++扩展。最终候选使用generic `TRITON_ATTN`，不能套用这个历史路径观察。

宿主PCI拓扑可见多张卡，但容器中PyTorch/`ixsmi`只暴露一张，不能写成双卡结果。宿主CPU数不等于配额：OnlineLab为6 CPUs，正式manifest的quota/period为600000/100000，即6核。

## 工作区历史快照

| 路径 | 大小 | 版本/状态 |
|---|---:|---|
| `/workspace/MiniCPM5-2B` | 4.7 GiB | 本地模型快照 |
| `/workspace/vllm-plugin-FL` | 9.7 MiB | `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`，本地`main`，当时比`origin/main`领先6个提交 |
| `/workspace/FlagGems` | 105 MiB | `4df52d9168ac55c1c1061cefb4638c570292d896`，tag `v5.3.5` |
| `/workspace/evalscope-datasets` | 452 KiB | 含`math_500/test.jsonl` |

所需checkpoint约5.03 GB，保存在一个safetensors分片中。

## 核对说明

- 初次从本地主机只读运行`git ls-remote`，确认`flagos-2026-s2`指向`13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`，与当时已安装`vllm-plugin-fl`及源checkout一致。
- 初次checkout名为`main`，提交仍是比赛分支基点。原笔记曾计划建立同名本地分支；此为历史计划，当前采用全新独立实验checkout，既有参考仓库只读。
- 实例只有一张加速器，早先双卡预期未成立；设备测量遵守单卡协议。
- 初次服务及官方smoke返回有效MiniCPM响应。
- Level 3完整性后来已由正式原件核验：当前SQL+C3为105题、103/105，初期“待确认”不代表当前未验证。
- 当前服务还固定Triton源3.6.0与SQLAlchemy2.0.48，不因翻译升级依赖。原版/候选Attention身份分别为bab2/54c，见依赖恢复记录。
