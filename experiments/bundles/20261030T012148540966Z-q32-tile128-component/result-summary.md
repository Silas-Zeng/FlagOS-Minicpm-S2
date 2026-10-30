# Q32 TILE128 数值与组件结果

A/B只改变TILE_SIZE 64→128；BM256/BQ32/w16/stage1与grid(64,2)相同。合成ABI下五个case的两臂参考检查、A/B逐点容差、finite输出、guard、输入只读和changed-Q检查通过，同臂跨组输出稳定。

四组ABBA各50次，Event均值A 7.9793690 ms、B 8.4068933 ms，B慢5.358%。数值门通过但组件性能为负，停止TILE128候选；不进官方/生产资格，不更新基线。该结果不代表服务捕获或端到端吞吐。

编译资源差异仍按前序编译记录保留：VGPR 135→164、shared 57,344→81,920 B、ASM SGPR spill计数98→128；runtime spill、VGPR spill和ScratchSize为0。恢复包SHA256 `284311144f33238f102fbb9599c4ca0d25b2753dbd15d2a1bbfda942dd4fc1e9`，70项。
