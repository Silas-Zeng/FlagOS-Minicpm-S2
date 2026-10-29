<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T043401Z-native-gqa-s8-16k-four-rounds

- **尝试了什么：** 官方16K四轮完成：512/512请求成功，四轮Total tok/s为4422.66/4888.63/4887.29/4885.53，首轮后暖均4887.15。出现正向信号；相对PR105暖均4832.66为+1.1275%，但KV为548384对548288，不作严格因果或新基线。
- **改了什么：** 在 PR105 814-file 源上接入 N30/S8 producer；仅 BF16 且 Q stride=2048 时启用，其余路径回退。资格源为 819-file tree `5da6498`，CPP `087ea25d`、CUDA `5d7b8c31`、S8 SO `6c3cbd3`；S2/S4 SO `c8a725da` 保持。
- **怎么测：** MiniCPM5-2B 原官方 16K 四轮，每轮128/128成功；首轮筛选为正后跑满四轮。当前仅观察到16K正向信号，KV不匹配，不作严格因果或新基线；4K与105待测。 完整压缩原件按恢复包保存，见 [SHA逐文件清单](../../../experiments/bundles/20261029T043401Z-native-gqa-s8-16k-four-rounds/manifest.json) 与 [压缩包分块索引](../../../experiments/bundles/20261029T043401Z-native-gqa-s8-16k-four-rounds/raw.tar.gz.storage.json)。
- **结果怎样：** 四轮Total tok/s 4422.66/4888.63/4887.29/4885.53，均128/128成功；弃首轮暖均4887.15。相对PR105暖均4832.66为+1.1275%，但KV548384对548288，不能严格归因或更新基线。 自然负载选择S8，eager_only，无CAPTURED；accuracy-105独立门未跑。
- **是否保留：** 保留原件和结论；不据此新增基线。
