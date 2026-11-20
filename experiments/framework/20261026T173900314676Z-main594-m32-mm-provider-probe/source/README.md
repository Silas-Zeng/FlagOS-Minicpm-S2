# main594 M32实际MM身份探针

只参数化已完成的150802 M64探针：真实layer0 down权重、独立32行输入与caller out，一次原`small_linear_out→torch.mm(x,weight.t(),out=out)`；记录真实config/hash/IR/资源、自然W.t shape/stride。未写候选、不预设M64配置、不计时、不做八门或Graph矩阵；普通finite/FP64样本/输入不变只作一次sanity。历史16K M32图仅提供优先级，不证明当前16K覆盖。

原owner只改run名/scope，其GPU/9031/单卡锁、DB保存恢复、自有PID清理不动；默认FlagGems mm.out注册与真实SDK源SHA/四个main594文件pin原样。无需复制原4文件快照，继续引用150802的已核源码；运行时保存实际已装MM/callback原件。不加载或修改native SO，不能将这次探针称为native/模型资格。

由root在设备空闲时启动；本包未SSH/GPU。无需等待当前16K分布才能做此一次身份检查：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/<M32探针目录>/entry.py --source-dir /workspace/experiments/minicpm-s2/code/main594ae2-pr59-20261026
```

源必须为未叠3b14候选的main594；包身份见`package-receipt.json`，CPU合同见`cpu-result.json`。结果无性能/候选数值/官方资格，得到实际配置后再决定M32地址差分。原M64探针与当前3b14生产包均未改。
