<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# GQA shared4k共享缓冲区复用

N32/S4/KV16K局部ABBA省时约0.05% Event、0.14% wall，只是微弱正向组件信号，未确认稳定收益。S8官方候选的三次入口失败均在GPU启动前，无benchmark请求和性能计时；不将其解读为候选数值错误或退化。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261029T104230927931Z-native-gqa-shared4k-s4-hotspot-component](../runs/bi-v150/20261029T104230927931Z-native-gqa-shared4k-s4-hotspot-component.md)（登记#503）：S4 Event省0.0538%、wall省0.1435%；属微弱组件正向，未确认稳定收益。 **是否保留：** 保留组件观察；不作官方成绩、生产资格或基线更新。
