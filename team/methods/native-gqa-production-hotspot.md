<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 同步原生GQA实际热点诊断

原profile posthoc因关闭compile cache缺fresh FX而不完整；现成节点解析通过。4个N64样本的1988插桩区间中，S2/42层17.9005ms、MM6.1148ms、W8A8 1.8053ms、reduce0.4305ms；不能当未插桩时延或官方吞吐。N32未达采样门，未采M2048。

相关代码：[summary.json](../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/summary.json)；[raw-evidence.json](../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/raw-evidence.json)；[hotspot-and-posthoc-review.json](../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/hotspot-and-posthoc-review.json)；[graph-summaries.csv](../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/graph-summaries.csv)；[kernel-rankings.csv](../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/kernel-rankings.csv)；[native-logical-bandwidth.json](../../experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/native-logical-bandwidth.json)；[manifest.json.storage.json](../../experiments/bundles/20261027T171100Z-c75db-production-hotspot-4k/manifest.json.storage.json)；[raw.tar.xz.storage.json](../../experiments/bundles/20261027T171100Z-c75db-production-hotspot-4k/raw.tar.xz.storage.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261027T171100Z-c75db-production-hotspot-4k](../runs/bi-v150/20261027T171100Z-c75db-production-hotspot-4k.md)（登记#389）：原posthoc不完整；节点解析通过，4个N64样本/1988插桩区间；S2共17.9005ms为主要区间。 **是否保留：** 保留热点诊断；不是未插桩时延或官方吞吐。
