# 天数 BI-V150 · 源码归档安装记录

首次从无 Git 元数据的源码归档构建 FlagGems 时漏装 DSA 子目录，服务启动失败，发送 0 题。用同一提交完整导出源码再次构建，安装包仍缺 DSA 模块。从完整 Git 检出构建后，两个主干正常启动服务。

用两库相同提交的源码归档构建 wheel 并启动服务。归档未包含 Git 元数据。

[原始证据](../../../experiments/accuracy/20261120T082459Z-final-main-accuracy/raw-evidence.tar.gz) · [受测源码](../../../experiments/accuracy/20261120T082459Z-final-main-accuracy/installation/identity.json)
