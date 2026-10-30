# Q32 TILE128 编译探针结果

固定合成ABI下仅将TILE_SIZE由64改为128；BM256/BQ32/w16/stage1与grid(64,2)相同。A/B编译成功，实际effective SME均为3（requested 229379）。

- A：VGPR 135，shared 57,344 B，runtime spill 0，ASM SGPR spill计数98。
- B：VGPR 164，shared 81,920 B，runtime spill 0，ASM SGPR spill计数128。
- 两臂ASM VGPR spill与ScratchSize均为0；仅执行一次writer和编译warmup，没有Attention reader。

B资源占用上升。先保留该结果供同几何数值门与组件测量判断，不据compile metadata单独宣布性能负结果或收益；本轮不是服务捕获、官方吞吐、准确率或新基线。原始恢复包SHA256 `e28e79de5f9f6d762906ad8484c74027911de99eef75eb37906fa23d8eeb3a90`，61项已回收。
