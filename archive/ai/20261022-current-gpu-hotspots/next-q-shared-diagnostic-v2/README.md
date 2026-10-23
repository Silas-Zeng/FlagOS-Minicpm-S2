# 硬件指标诊断 v2：初始化顺序与真实完成状态

`134939` 原件保留：worker 在 compiled 观察为空时拒绝，未开始 128 次窗口；ixsys 将 worker 失败吞为 exit 0，v1 owner 因此误报成功。不能引用为有效诊断。

v2 恢复已验证旧门的顺序：先 `EngineArgs.create_engine_config` 完成插件配置，再导入、pin、安装原 C2/C3；核 backend 的 unified function/module globals 与实际 impl 身份。保留 compiled 为空的拒绝，不绕过真实路径检查。

owner 同时要求 ixsys 成功、worker 成功状态、128 次完成、start/stop 成功、五项不变量、settle 和入口恢复；缺失/损坏结果默认失败。原单卡 owner cleanup 与采样窗口不变。CLI 和上传四件同 v1，改用本目录资产；原 fixture/C2/C3 保持原字节。不加载候选、不报吞吐收益，尚未部署。仅新增 CPU 检查见 `cpu-check.json`。

新增 CPU 9 项检查（含 13 种退出状态）一次通过，耗时 0.0173 秒；未重跑旧套件。framework 已只读新增顺序、身份断言与退出聚合，无新增阻断，未执行设备。实际插件路径是否命中及硬件指标是否有效，仍须以 v2 原始结果为准。
