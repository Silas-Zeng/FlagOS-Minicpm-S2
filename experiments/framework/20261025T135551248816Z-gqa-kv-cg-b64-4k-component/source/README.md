# 原 cg 的 B64/S2、4K 组件对照

此前两组 cg 组件均是16K，不能代表官方4K场景；官方首暖已出现回退。本包仅补实际短场景的 B64/S2、KV4096，判定局部是否也下降。没有长短混合生产选择器，也不重新跑官方或扩大矩阵。

原生产 baseline `2596cc09` 与 cg candidate `1043497f`、机器码门、8组正确性/变化输入Graph、完整producer＋reducer的16-call ABBA逐字复用。唯一新增是shape接线：真实Builder/Impl自然调用GQA，运行时必须捕获grid `(64,2,2)`，原8192列页表与packed NHD stride不变。实际预留null页0、真实writer槽整体加16；64请求全部活跃，保留原空padding修复。ragged长度截至本次KV4096，避免旧16K边界越过实际页表；更换的KV页与预留null页偏移一致。

`shape-check.json` 只核本次新增接线；原内核、数学及owner审据复用。owner仅增加shape选项并默认 `b64-4k`，设备锁/GPU/9031/420秒/DB/native14f/所属清理完全保持。旧hotspot/b32入口仍可识别，不自动运行。

```bash
python entry.py --shape b64-4k --source-dir <已冻结原526绝对路径> --native-library <已核native14f绝对路径>
```

尚未上卡、无新收益。无论局部正负，都不能单凭这一项抹去cg官方失败或给予模型资格；由root决定后续。
