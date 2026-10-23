# 单 computed H2D 短服务接线草案

仅供方法门通过后的串行单侧服务。当前未部署、未运行；必须先等待固定461676方法门实际PASS，并由root确认正在运行的官方任务退出、清理且设备/9031双栈空闲。launcher不会启动第二侧或自动重复。

固定基点为 `/workspace/experiments/minicpm-s2/code/q-gqa-service-candidate-20261022T184141Z`。完整bf69 map有414文件；baseline原runner cc442，candidate为97f41，仍414文件且只runner一个路径不同。原Q/GQA、CPUmetadata0e961、async1bb85、固定buffer和同步不变；复制的23d833源变换逐字节复用已审候选。

将本目录5个执行输入文件放到远端独立assets目录：两个preparer、两个source-map、launcher。后续root按需执行，每次仅一侧：

```bash
bash /path/to/assets/launch_skip_computed_h2d_service.sh   /workspace/experiments/minicpm-s2/code/q-gqa-service-candidate-20261022T184141Z   baseline /workspace/experiments/minicpm-s2/framework/<实际通过的461676方法门run>
# 该侧完成并用原sealer收口后，显式将baseline改candidate；不并行。
```

preparer要求实际方法门exit-code/manifest/result通过、五case/event-graph/真实guard fallback结果，并核gate归档的六个源SHA；不存在或失败即拒绝。并非仅接受用户提供的通过字符串。原bc51 driver、SERVER、decode4k/128out/64req/c64、seed721201不改。两侧创建独立绝对Q artifact目录/ENV，显式unset finite；不加profiler、第二controller或第二设备锁。沿原source/env/log/DB-before归档，结束由root运行原 `scripts/seal_framework_screen.py <run-id>` 补DB-after、source/postflight。准备器不执行模型。

最低服务证据为64成功0失败、原tokens和负载参数；同Engine的原Q/GQA成功execute标记，以及原 `BIV150_CPU_METADATA_FIRST_SELECTED positions_seq_h2d=2`。metadata原标记证明一次实际 `_prepare_inputs` 选择，不是全程覆盖、同execute模型完成或GPU完成证明；dummy不经该方法。其余删H2D语义复用先通过的方法门，不加热日志或新observer。Q/GQA graph replay不增加Python计数，原首次成功execute标记也不代表逐步coverage。

可比门保完整source/live/archive且source差异恰仅runner、原driver/benchmark/SERVER/argv/seed/包/CPU配额及外部源、64/0与有效tokens、实际KV相同、DB四端三SHA/表行数相同、结束严格idle。失配则收益null，只留描述，不为匹配KV反复跑。已有Q/GQA与finite比较器固定其它source差异，不能原样套用；root复用其可比项读取本次原件即可。该草案没有新增accuracy或生产净益结论。

CPU只做内存compile、两个shell heredoc compile、Git Bash `-n`、完整map单路径差异和原三资产字节身份核对；没有执行准备器/整树复制/方法fixture/旧套件/设备/SSH。见 `wrapper-check.json`。

冻结：preparer e174044c38fe21351c23922d1307003a47e876513a8864a03eb5e3be4c96f1f3；launcher c342134afdf2414c0c3931b24dcb8f8a4508a4ebd2dc7fc7ce2bffb738f22251。hardware新增接线审阅通过，无阻断；未重复旧检查或设备门。仍须先完成官方测试、清理及方法门，由root串行调度。
