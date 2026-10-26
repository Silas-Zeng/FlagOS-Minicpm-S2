<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# BI-V150特定形状GEMM

按真实轨迹选形状。M2048 down占映射BF16 MM约47.10%；大M静态化/减warp/加深K及M64 SplitK均负。宽N 256/256/32/w16/s2的42层真实down组件省24.12%，但实际模型M2030/2048选中后，4K首暖5451.11对PR60对应5533.03观察−1.48%；512 SUCCESS后主动早停，16K/105未跑，KV548432对548336，不能称严格因果、完整官方或正确性失败。PR61关闭未合并，保留原件。后继独立QKV M2048/2030,N2560,K2048，42层真实Q/K/V拼接组件12.705318→12.174299ms（省4.1795%），84数值/FP64抽样/Graph换值/side stream门通过；模型筛选另列，不叠down、不把组件比例当吞吐。另保留独立M1-8 down SplitK8组件，M2/M8整环省31.69%/34.98%，尚未接模型。原正确PR51及PR60基线不变。

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
- [20261026T042110Z-main6971-pr61-down-wide-four-rounds](../runs/bi-v150/20261026T042110Z-main6971-pr61-down-wide-four-rounds.md)（登记#298）：down wide组件42层省24.12%，实际模型M2030/2048均选中，但4K冷4914.39、首暖5451.11 tok/s，对PR60对应5533.03观察−1.4806%。512 SUCCESS后按规则主动停止，第三轮中断；16K/105未跑，不是完整官方或正确性失败。source/n **是否保留：** 首暖负按约定主动停止，保留已测轮次和运行条件；未测16K/105，不合并或定基线。
- [20261026T043518378183Z-biv150-qkv-wide-working-set-component](../runs/bi-v150/20261026T043518378183Z-biv150-qkv-wide-working-set-component.md)（登记#299）：独立QKV M2048/2030,N2560,K2048；42层真实Q/K/V按q,k,v拼接权重。原256/128/32/w8/s2对宽256/256/32/w16/s2，84数值/FP64抽样/换值Graph/side stream/RNG通过。ABBA Event 12.705318451→1 **是否保留：** 保留候选；优先推进热点M2048 wide，M1-8 SplitK另列；需要实际接入、整模型性能/105和新增代码独立复核。
