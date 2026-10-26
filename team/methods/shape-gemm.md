<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# BI-V150特定形状GEMM

按真实轨迹选形状。M2048 down占映射BF16 MM约47.10%；大M原tile静态化/减warp/加深K等6方案及M64 SplitK4均负，原件保留。宽N BM256/BN256/BK32/w16/s2单层省24.34%，42层1.057GB真实权重轮换30.371530→23.044686ms（省24.12%），84数值/尾部/FP64/换值Graph/side stream门通过。另保留M1-8 down SplitK8：M2整环3.057750→2.088810ms，M8整环3.367892→2.189718ms，分别84/336数值用例通过。均为组件结果，尚无整模型吞吐或105资格，不合并；原正确PR51及PR60主线不变。

相关代码：[2026-10-26-gemm-target-priority.json](../../analysis/2026-10-26-gemm-target-priority.json)；[2026-10-26-gemm-component-results.json](../../analysis/2026-10-26-gemm-component-results.json)；[candidate.py](../../experiments/framework/20261026T035139678096Z-biv150-down-wide-working-set-component/source/candidate.py)；[candidate.py](../../experiments/framework/20261026T034152136640Z-biv150-down-small-working-set-component/source/candidate.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261026T032246818091Z-biv150-down-gemm-component](../runs/bi-v150/20261026T032246818091Z-biv150-down-gemm-component.md)（登记#289）：Event每GEMM毫秒 {"baseline": 0.7208077609539032, "balanced_k64": 1.128869652748108, "deep_k128": 2.5089584589004517}；wall {"baseline": 0.7227574921875, " **是否保留：** 数值通过但完整组件慢，不接模型；不能把资源减少或循环减少当净收益。
- [20261026T032525788161Z-biv150-down-gemm-static-component](../runs/bi-v150/20261026T032525788161Z-biv150-down-gemm-static-component.md)（登记#290）：Event每GEMM毫秒 {"baseline": 0.7224094271659851, "same_tile_static": 0.9332556426525116, "wide_n_static": 1.0096490979194641}；wall {"baseline": 0.7242720 **是否保留：** 数值通过但完整组件慢，不接模型；不能把资源减少或循环减少当净收益。
- [20261026T032747889076Z-biv150-down-gemm-pointer-component](../runs/bi-v150/20261026T032747889076Z-biv150-down-gemm-pointer-component.md)（登记#291）：Event每GEMM毫秒 {"baseline": 0.7226908206939697, "pointer_static_w8": 0.7272025644779205, "pointer_static_w4": 1.18551766872406}；wall {"baseline": 0.7245 **是否保留：** 数值通过但完整组件慢，不接模型；不能把资源减少或循环减少当净收益。
- [20261026T033143347707Z-biv150-down-splitk64-component](../runs/bi-v150/20261026T033143347707Z-biv150-down-splitk64-component.md)（登记#292）：Event每GEMM毫秒 {"baseline": 0.05582100339233875, "split4": 0.06915904581546783}；wall {"baseline": 0.0574849375, "split4": 0.0701430546875}。5项数值/尾部/换值Gra **是否保留：** 数值通过但完整组件慢，不接模型；不能把资源减少或循环减少当净收益。
- [20261026T033421188581Z-biv150-down-tiny-splitk-component](../runs/bi-v150/20261026T033421188581Z-biv150-down-tiny-splitk-component.md)（登记#293）：Event每GEMM毫秒 {"baseline": 0.07281111553311348, "split4": 0.05686087720096111, "split8": 0.05061881057918072}；wall {"baseline": 0.0744598359375, "split **是否保留：** 保留局部信号，后继完整权重工作集结果另列，不把组件比例当整轮收益。
- [20261026T033822917380Z-biv150-down-tiny-working-set-component](../runs/bi-v150/20261026T033822917380Z-biv150-down-tiny-working-set-component.md)（登记#294）：42层真实权重1056964608B轮换，M1/2（计时M2）；Event整环3.057749748→2.088809967ms（省31.6880%），wall3.062777281→2.093116094ms。84项数值通过，Graph换值/side stream/RNG通过；原基线对候选全输出误 **是否保留：** 保留候选；优先推进热点M2048 wide，M1-8 SplitK另列；需要实际接入、整模型性能/105和新增代码独立复核。
- [20261026T034152136640Z-biv150-down-small-working-set-component](../runs/bi-v150/20261026T034152136640Z-biv150-down-small-working-set-component.md)（登记#295）：42层真实权重1056964608B轮换，M1-8（计时M8）；Event整环3.367891550→2.189718008ms（省34.9825%），wall3.373675094→2.194239469ms。336项数值通过，Graph换值/side stream/RNG通过；原基线对候选全输出 **是否保留：** 保留候选；优先推进热点M2048 wide，M1-8 SplitK另列；需要实际接入、整模型性能/105和新增代码独立复核。
- [20261026T034932832328Z-biv150-down-wide-component](../runs/bi-v150/20261026T034932832328Z-biv150-down-wide-component.md)（登记#296）：Event每GEMM毫秒 {"baseline": 0.7254105806350708, "wide256": 0.5488503277301788}；wall {"baseline": 0.727244015625, "wide256": 0.550182}。5项数值/尾部/换值Graph及FP **是否保留：** 保留局部信号，后继完整权重工作集结果另列，不把组件比例当整轮收益。
- [20261026T035139678096Z-biv150-down-wide-working-set-component](../runs/bi-v150/20261026T035139678096Z-biv150-down-wide-working-set-component.md)（登记#297）：42层真实权重1056964608B轮换，M2048/2030；Event整环30.371529579→23.044686317ms（省24.1241%），wall30.378039625→23.050260812ms。84项数值通过，Graph换值/side stream/RNG通过；原基线对候选 **是否保留：** 保留候选；优先推进热点M2048 wide，M1-8 SplitK另列；需要实际接入、整模型性能/105和新增代码独立复核。
