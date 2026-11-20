# Q32 query-scale 外提：编译完成，资源门待确认

把 `query_code_scale * score_scale` 从每个 KV tile 的二维 score 乘法中提到循环前。A/B使用同一冻结encoded writer与合成参数，BM256/w16/grid64×2，实际SME均3。

实际TTGIR显示：B在循环前计算256元素的尺度向量，循环内256×64的score乘法由3组减为2组。寄存器135、shared57344字节及Triton runtime spill0未变；但ASM元数据的SGPR spill计数由98增加到110，VGPR spill与ScratchSize均0。不能只看runtime字段写“无新增spill”，也不能仅凭静态总指令数判断动态成本。

本轮只执行一次编码writer与A/B编译，没有启动Attention reader、进行数值或计时。按原编译筛选条件暂缓此版，保留机制与资源代价；这不是数值失败，也不是性能负结果。下一步先解释新增scalar spill，或准备把score scale合入每tile的64个K尺度的独立版本，避免直接复制本版长期驻留成本。数值和服务资格均未取得。

60原件完整回收：[原始summary](../../archive/q32-score-scale-20261030/compile-003609/cpu-probes/20261030T003609248517Z-q32-score-scale-compile-probe/summary.json)、[回执](validation/compile-003609-recovered.json)、[独审](validation/terminal-review.json)。owner97413/child97415/session15887正常结束，GPU与9031后检为空。
