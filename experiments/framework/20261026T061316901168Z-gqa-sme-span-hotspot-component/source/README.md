# GQA page16：SME backing-span独立组件

CPU准备完成，未SSH、未GPU编译或数值/性能验证。当前main6971/618/treeaa43，原native14f、原DB、原producer+reducer ABBA；只固定N33/bucket40/S16、KV16384、page16/tile16、w1/s1，不叠T32、不扫参数。

candidate.py为新行寻址GQA：K/V六stride使用128元素行单位，其余数学/online softmax/原split保持。descriptor.py建立同storage和data_ptr的合法二维连续backing跨度，view keepalive覆盖实际调用与Graph；原reducer不变。V偏移4096时按剩余storage核界，不能把K的完整storage长度用于V。

原8类FP64/特殊值/尾页/零长padding/side-stream/同址换Q、KV、page表与Graph毒化门不放宽。每臂仍对自身fresh逐位；新增view地址别名检查。数值错误立即停。资源、全部TTGIR/LLIR/ASM及SME/async-wait/barrier摘录保存在run下ir-*和sme-selection-diagnostic.json；use_sme只是诊断，不将mask63本身当选择/加速证明。B40/S16 full scratch通常15->63，窄scratch才可能14->62。

## root部署与启动

将entry.tar.gz解压到 `/workspace/experiments/minicpm-s2/scripts/gqa-sme-span-component-20261026/`。仅在root已实查唯一GPU、9031和设备锁空闲后启动：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/gqa-sme-span-component-20261026/entry.py --source-dir <已核aa43/618的冻结main6971源码目录> --native-library <原14f原生库.so> --shape hotspot
```

entry负责nonblocking设备锁、GPU/9031 preflight、DB原件/恢复、source/native身份、GPU采样、420秒worker上限及自有进程清理。它不会安装生产优化，也不会自动接官方/准确率/其它形状。entry.py --worker仅由entry内部调用。

结果为完整producer+原reducer Graph ABBA；Graph前一次view创建的wall开销不是计时的一部分，view元数据需单列，生产接线不能隐去每层view创建成本。正向且真实传输/等待机制成立，才由root补B32/S4与B64/S2以及生产接线门。GPU之前的CPU检查不替代设备资格。
