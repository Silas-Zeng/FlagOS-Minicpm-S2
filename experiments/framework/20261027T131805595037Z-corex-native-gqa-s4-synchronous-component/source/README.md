# 同步原生GQA S4/N32/KV16384组件

从冻结S2包独立派生；CU8aa模板/consume_page逐字不变，只实例化既有Segments4和grid.z4，bridge固定N32/S4。保持同步variant0/8KiB设计；新实际资源以CPU编译结果记录，不迁移S2值。

首次backend自然构造metadata必须实际S4、grid[32,2,4]，A直接重放本次原GQA编译hash＋原reducer。基线main56核SHA2596与main84相同；合成输入容量16384，初始完整ABBA计时长度全部16384，非官方成绩或模型资格。

原9组数值/FP64/换值poison Graph/side/输入RNG、有限时全部partial/max/sum逐位及空段/尾NaN遮罩门保留，未改变容差。只有原门通过才唯一producer＋原reducer完整Graph ABBA，每窗16call。writer仅共同setup，不计入组件时间。

先CPU-only编译：`sh compile-only.sh /workspace/experiments/minicpm-s2/cpu-probes/<新S4run>`；无Torch/model/GPU导入或launch。编译通过后由root单独安排 `python3 entry.py --compile-dir <同一S4输出目录>`。不得拿S2编译回执或收益赋给S4。原owner单卡锁/9031/DB恢复/source/native/自有进程清理保持。

实际QKV切片范围：Q来自[35,2560]backing的前2048 view，实际传入[32,16,128] stride[2560,128,1]，out原[2048,128,1]。extra512保持-23且每案检查不变，末3行仍保输出guard。bridge只授权本次2560行stride；不将S2的2048资格迁移到S4。
