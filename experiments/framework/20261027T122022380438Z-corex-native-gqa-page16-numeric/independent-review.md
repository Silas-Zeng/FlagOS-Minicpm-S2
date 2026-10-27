# v3覆盖诊断增量独审

**无新增启动阻断，可运行一次短数值接续。** 最终包`86d106ada983d1e10b689dbbfab770ade7e014ca78883f6b51558ccfeac34b0a`，90279B／23pins，所有pin及tar成员独核。原[v2独审](../corex-native-gqa-page16-v2-20261027/independent-review.md)复用；不重审未变地址、ABI、stream及清理。

与fd6原21项比较，唯一runtime变化为worker中两行coverage诊断，精确逆文本即还原原worker；CU `8545adc9237bb20145edbcd04f76594a149eafd8914f51c4135b5bfcd3b96cce`及其它20旧资产逐字不变。改为先将原FP32 score拷到CPU，再`astype(float64)`，避免用GPU.double参与CPU覆盖判定；Python `2.0**-126`、`2.0**-149`及半最小值是原IEEE阈值的精确双精度表达，不是放宽概率或误差门。

独立读取原120655归档NPZ（SHA `60b7feb2ccda15ebfb1aaa03a9f6ab393c9c01d3975ebcbf54b954af0c778889`）复算，normal／subnormal／低于最小subnormal半值三项均真；原保存的native与tl.exp2 FP32 P位型仍相同。原`failed_stop`及false覆盖保留，不回写成通过；没有把posthoc当成Graph／side已完成，也不精确归因混合路径中哪个辅助步骤触发旧false。

FP32/BF16 P、partial/max/sum逐位、独立FP64、输入／RNG、换值poison Graph与side-stream门均原字节保留，`underflow_input_covered`仍要求三项全真；并未删除门或更换CU／输入。GPU接续若任一原硬门失败仍停止。这里只决定诊断包资格，未SSH/GPU、未修改冻结资产，不包含完整GQA loop、尾页／空段、reducer或性能资格。
