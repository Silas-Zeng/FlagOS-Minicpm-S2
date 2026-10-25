# M2 LM-head paired-GEMV 单候选组件

仅在 BI-V150 上判断这个实现是否值得继续，尚未编译或上卡。原先重复特殊 token 的诊断包保持冻结；本组件与它分开，不用于修复旧异常，不改框架或官方采样。

实际072151轨迹的 graph 外 `linear_kernel`：mixed 4步 grid1020/block512/shared16512、0.841–0.845ms；FULL 8步 grid510/block1024/shared40960、1.037–1.059ms。模型 config 是 BF16、N130560/K2048；runner先选 logits 行，M2/M33是依请求行数及源码推导，trace没有保存完整标量ABI。实际DB的M2配置为BM2/BN128/BK32/8warps/2stages，M33经过align32命中64键、BM64/BN256/BK32/16warps/2stages，与launch几何和shared相符。`evidence.json`保存原件哈希、12次launch及配置，不把推导称为实参采集。

唯一候选是 `candidate.py`：M2、连续BF16权重、BN32/BK256/8warps，两个FP32 accumulator共同消费同一权重载荷，再分别归约并写完整BF16词表。省的是潜在dot布局转换与长K循环，不省535MB权重读取；循环64→8、CTA1020→4080，增加FP32寄存器与CTA开销，收益未知。归约次序改变，不能继承任何模型准确率。M33切32+1会再读整份权重，当前不做。没有tile扫描、权重副本缓存、量化、路由替代库或算子全局注册。

`worker.py`固定原FlagGems linear源SHA `d431a4fa…`，剥离装饰器后直接调用原JIT及上述已记录M2配置，避免新autotune；它是原实现的组件基线，未声称继承当前服务参数。参考用CPU FP64和随机BF16权重/两行激活，保留全输出、最大差、相对L2、BF16舍入一致率。再换激活/权重指针和内容，核两行与词表映射；检查完整输出guard和RNG。任何基线或候选数值失败就停。通过后只有一次ABBA、每窗32次，计时含完整LM-head输出写入，输出预分配；原计时器含Event/wall/提交CPU/节流记录。最后再核输出/RNG。编译IR/ASM全部落盘，不设没有实测依据的寄存器否决线。若不快即停止，不自动上模型或展开参数矩阵。

root持卡、实查空闲后运行：

```bash
python3 entry.py --model /workspace/MiniCPM5-2B
```

入口复用已有轻组件owner的设备锁、9031/显存门、唯一worker、监控、420秒超时、自有进程清理和DB恢复。原件存到新UTC `/workspace/experiments/minicpm-s2/framework/*-lm-head-paired-gemv-component`，本包不加载native或模型runner，不要求固定main526身份。`owner.diff`只显示从旧owner减去无关资格及切换worker；`reuse.json`记录四个逐字复用的设备/计时函数。只通过CPU源码语义检查，真实编译、数值、时序和净收益仍未知。

借鉴边界：SGLang [DSV4 wo_a GEMV](https://github.com/sgl-project/sglang/blob/main/python/sglang/kernels/ops/gemm/dsv4_wo_a.py)采用直接FP32乘法归约；[Hopper GEMV](https://github.com/sgl-project/sglang/blob/main/python/sglang/kernels/ops/gemm/hopper_bf16_gemv.py)对SM90排除大于65536的N，并注明大LM-head在其平台已接近带宽上限，不能把H200收益照搬到BI。其[DPA LM-head all-to-all](https://github.com/sgl-project/sglang/blob/main/docs/docs/advanced_features/dp_dpa_smg_guide.mdx)针对多卡分片，不适用本站TP1。本框架HY4的专有FP32 LM-head适配也不能用来改变MiniCPM BF16输出。PR44/38最新仍为c6938cf/5449b926；本包不复制其BF16 MM/GEMM融合或PR33/36/37实现。
