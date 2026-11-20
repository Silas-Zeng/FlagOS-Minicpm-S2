# FlagGems 源码归档打包独立复核

- 在任何 Git 工作树之外解开 `5aa04ed` 的归档，清除 SCM 版本覆盖，使用 setuptools 76.1.0、setuptools-scm 9.2.2 和 wheel 0.46.2。普通 wheel 构建、卸载后 editable 安装均成功，版本为 `5.3.5+archive`。在源码目录外启动独立解释器，前者定位到 site-packages，后者定位到解包源码，PEP 610 记录了 editable。
- 普通 wheel 与归档中全部 2,571 个运行时 Python 文件、46 个 YAML 逐字节一致，另生成 `_version.py`。两种安装均能解析无 `__init__.py` 的 DSA 三个模块、BI-V150 的 MM、C500 三个 Top-P 模块、CLI 和套件入口，两平台的六个后端配置均可读取。原 `bda4a2e0` 的普通包发现会漏掉 8 个运行命名空间里的 33 个模块。此次为 CPU 安装和定位检查，未初始化厂商驱动或测量吞吐。
- **已有打包边界。** 两个测试套件映射仍用普通 `find_packages`。实查无 Git 的 wheel 未收录 `tests/test_FLA` 的 4 个 Python 文件及 `benchmark/{test_FLA,models_benchmark}` 的 8 个。比赛推理和框架仓里的官方压测脚本均不依赖它们。无 Git 归档共用后备版本号，核对交付内容应以归档身份为准。
- **C500 复现。** 下载目录的说明使用 `--no-build-isolation --no-deps`，执行前需由比赛镜像提供声明的构建工具及厂商 PyTorch、mcTriton。屏蔽 GPU 和清空插件的三个变量只作用于客户端。120 GB 主机内存不能单独验证 SDK 内存策略；要复现既有启动条件宜明确服务端 `MACA_HOST_MEMORY_POLICY=0`。历史 A5 的两次内部均值与原主干的一次 4K 是两套证据，新归档仍无设备成绩。[双平台复现说明](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/main/docs/submission/readme.md)

## 7ae782e 增量复核

- 独立从无 Git 归档和含 `.git` 的干净浅克隆分别构建普通 wheel，并安装到两个独立目录。安装后逐项对照该提交的 Git 归档，两个包均完整包含 758 个测试文件、738 个 benchmark 文件、2,571 个运行时 Python 文件、46 个运行时 YAML 及独立 CLI 模块，所有文件字节匹配。原先遗漏的 12 个 Python 文件、2 个基准 YAML、模型基准 3 个 shell 脚本、依赖表和说明均在包内。
- 归档安装版本为 `5.3.5+archive`。当前无标签浅克隆构建为 `5.3.5.post1.dev4+archive.g7ae782ead`，其中保留实际提交号。两种安装从源码目录外均可定位 12 个运行和套件模块，4 个 console script 入口齐全。核验使用 CPU，未执行设备测试。
- 三份 FLA benchmark 自身沿用 `from benchmark.base import Benchmark`，发行包路径为 `flaggems_benchmark.base`。因此这些文件已补齐，但脱离源码树直接以发行包名运行时还需要相应的导入支持。两平台比赛用的官方压测来自框架仓。
