<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T041010Z-native-gqa-s8-official16k-ready

- **尝试了什么：** 服务及S2/S4 Graph正常；ready-marker reader把变量警告误判成协议失败，零benchmark请求/计时。非模型数值错误；修复边界后清理与源码/三SO/DB恢复通过。
- **改了什么：** 旧 ready-marker reader 把 VLLM 环境变量警告误识别为协议失败，修正 reader 判别边界；该轮仍未运行 benchmark。
- **怎么测：** BI-V150 官方16K入口启动前资格路径；确认服务与 S2/S4 Graph 正常，benchmark 请求和计时均为零。 完整压缩原件按恢复包保存，见 [SHA逐文件清单](../../../experiments/bundles/20261029T041010Z-native-gqa-s8-official16k-ready/manifest.json) 与 [压缩包分块索引](../../../experiments/bundles/20261029T041010Z-native-gqa-s8-official16k-ready/raw.tar.gz.storage.json)。
- **结果怎样：** 官方16K入口失败：旧ready-marker reader把VLLM环境变量警告误识别为协议失败，未产生benchmark结果（0请求/0计时）；不是模型数值错误。
- **是否保留：** 保留原件和结论；不据此新增基线。
