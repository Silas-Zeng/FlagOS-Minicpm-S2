# NativeK8 SME布局探针

- **尝试了什么：** 检查两条 `__ivcorex_sme_load_16x1b64_colxfb8` 路径搬运完整K页后，shared stage的字节布局是否与既有 `issue_k_i8` 路径一致。
- **改了什么：** 仅隔离探针代码；生产kernel和attention实现未修改。
- **怎么测：** BI-V150 CoreX compile-only保存实际SO/IR/ASM；GPU端覆盖zero、−127、+127、固定seed随机值，page 0/3及head 0/1，共16案，检查CPU reference、A/B逐字节、输入不变和输出guard。
- **结果怎样：** 16案/96项检查通过；每案2048B K-stage图像逐字节相等，SO/source身份匹配，GPU进程与9031清理完成。无吞吐计时。
- **是否保留：** 保留布局搬运证据；只覆盖完整页stage，不覆盖partial page、attention数学、模型准确率、吞吐或生产资格。

另有K-lookahead两臂CPU compile-only，结果与适用边界见第三条run记录。

源码以main `899ce77470b0b539aebc108fd122f668c2d5894d`为基准；恢复包SHA及逐文件清单见各run的bundle manifest。
