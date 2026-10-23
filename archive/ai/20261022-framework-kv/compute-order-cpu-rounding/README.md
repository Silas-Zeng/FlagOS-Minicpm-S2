# 085500固定现场：P舍入机制未复现，停止

只一次纯CPU NumPy分析，使用封存085500原row2/seq16504的Q/K/V和已生成FP32 reference，不重跑oracle reader或任何设备。`analyze_rounding.py` 固定T64，共享FP32 QK、在线max、alpha与未舍入P的FP32分母；唯一变量是PV前P保持FP32或RNE舍入BF16。两支最终输出均另作相同BF16 RNE，逐head原始结果及四份输出NPY在 `results/`。

保持P FP32的pre-store输出相对reference max `8.94e-8`；每tile舍入P后max `4.68194e-5`、mean `1.85440e-6`。两支相同BF16末存后，相对实际原2D仍max `.0087890625`、mean约 `.000276`，没有重现其坏head0/3/14；相对实际P/GQA的mean则为 `3.62e-6` / `2.00e-6`。因此本样本不支持“仅P BF16量化＋CPU在线累加足以解释原2D误差”，本条否决并停止，不扫参。

CPU模型不是实际GPU指令/FMA/归约复现，接近某一路不能判定通过；这里只排除该充分解释，不给整模型正确性结论。输入payload/reference SHA、完整max/mean/RMS/逐head差、NumPy版本均在结果。未改运行源码、算子或原件，未SSH/GPU/旧测试。
