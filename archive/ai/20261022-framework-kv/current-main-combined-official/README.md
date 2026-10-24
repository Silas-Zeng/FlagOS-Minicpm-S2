# 当前main加P的原官方完整吞吐入口

**已收尾**：144620原官方exit0，8轮全部SUCCESS；4K5116.68/16K3436.04 total tok/s，单臂不计归因收益。725原件封存、726逐项导入，见 `analysis/compute-order-current-main-official.json` 与本目录seal/import回执。以下保留原入口与准备过程，不是重新执行授权；不要重复封存。用户要求本轮结束切换API，不再启动后继任务。

固定复用141159受测源 `/workspace/experiments/minicpm-s2/code/current-main-compute-order-3283672b-20261023T141159Z`，完整446项、tree `5c77e68caff6aa0c8b6c230adb78a2d4c293cca1`。同目录三个部署文件为 `launch_combined_official.py`、`candidate-git-blobs.json`、`candidate-manifest.json`。

由root确认142019准确率通过并完成原sealer后，才可考虑执行：

```sh
python3 <assets>/launch_combined_official.py
```

启动器只读固定142019的105题valid/pass报告、封存附证、同446源码及清理后态；不重新判卷，不以exit0或main独立102/105替代组合准确率。准确率没有P命中时仍如实保留覆盖局限，不另制造门。当前只完成CPU准备，未执行启动器、SSH或设备任务。

实际测法完全由原 `run_official_gate.py`（79119f）/`run_accuracy_gate.py`（35d30）独占owner执行：原SERVER、0813官方benchmark、`[[4096,1024,64,256],[16384,1024,64,128]]`，各4轮、首轮warmup，原第2–4轮均值，原DB前后、CPU状态、设备锁、实时预检、监控及清理。没有smoke、profiler、自定义负载、超参修改或第二锁。完整源和symlink身份由沿用的双map核对并归档，所有BIV150实验ENV清除；安装门为当前Normalization，不使用旧Q/KV实验标记。真实Normalization/P选择及scope须结束后据原日志另行限定。

140324/141159两侧32/0且DB相同，但KV521840→521936，33门仅same_KV失败；gain=null，约+6.589830%只记表观变化。此官方单臂不能据此证明因果或稳定收益。接续资产在 `archive/ai/20261022-framework-kv/current-main-pair/`，tar仍留tmp，原tmp入口未迁移。

`launcher.diff`是相对已审c5ec准确率launcher的10个切口；`preparation.json`只记录精确逆回及syntax通过，没有执行launcher、旧reader或测试。`prepare_assets.py`是已执行的一次CPU生成记录，归档和输出均拒覆盖，不应为运行官方测试再次执行。
