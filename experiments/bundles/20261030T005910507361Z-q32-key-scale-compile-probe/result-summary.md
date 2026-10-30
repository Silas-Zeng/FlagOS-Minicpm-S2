# Q32 K-scale 融合：编译机制成立，待组件实测

每个 KV tile 先将64个K尺度乘score scale，再执行整数score的Q/K反量化。实际TTGIR中的256×64 score乘法由3组减为2组，新增64元素乘法；源码只改尺度结合次序，必须重新验证数值。

A/B均为135 VGPR、57344字节shared，runtime spill0、ASM VGPR spill0和ScratchSize0；ASM SGPR spill由98增为99。此项增量记为风险，不单独否决实测。上一query-scale版增至110的结果仍保留，未因此重测旧版。

本轮只有一次writer及两臂编译，没有Attention reader数值或计时；实际SME均3，与请求229379分开记录。下一步同几何先执行数值门，通过后才测ABBA。没有官方成绩、新基线或服务资格。

60原件已完整回收：[回执](validation/compile-005910-recovered.json)、[独立审阅](validation/terminal-review.json)。owner97575/child97577/session81208结束，GPU与9031后检为空。
