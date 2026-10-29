<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 真实linear shape与窄N方向诊断

104512短请求捕获135次linear调用；实际shape与warm-only调用分开，精确shape私有数据库记录不支持窄N候选，故NO-GO。诊断不是候选性能测试，也不据此推断官方请求热点。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261029T104512Z-linear-n64-short-capture](../runs/bi-v150/20261029T104512Z-linear-n64-short-capture.md)（登记#504）：135次linear调用已观察；窄N方向对实际shape为NO-GO，warm-only调用不代表请求热点。 **是否保留：** 保留真实shape诊断；不重复上卡或推断模型性能。
