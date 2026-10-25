# 固定 w8/page16 的 GQA grouped SIMT 组件

按照 `archive/night-20261026/gqa-simt-task.md`，从持久归档模板5e10178f中的原生产 `baseline.py`（2596cc09）派生；没有接续旧T64候选，也不叠prefill stride、`.cg`、log2或队友PR。当前仅CPU准备，不是可部署生产补丁，没有GPU编译、数值或收益结论。

**改了什么**：只改 `_gqa_decode_attention` 的完整页/尾页计算。Q加载后一次转FP32；K从[128,16]改为同地址集合的[16,128]；QK用[8,16,128]乘积沿D轴2求和，PV用同形状乘积沿page轴1求和。保留每页P→BF16舍入、FP32在线状态、exp2/LN2、原分段、页表int64、尾mask与提前return。没有全局中间scratch。新实现试图减少TCU填充和布局开销，但KV逻辑字节不减少；SIMT算术、广播复制、FP32 Q常驻与资源开销可能抵消收益。

固定真实N33/bucket40/S16/KV16384/page16，producer grid=(40,2,16)。baseline仍w1/s1，candidate只由私有pk覆盖w8/s1，原生产reducer grid=(40,16)/w4不改；实际原 `impl.forward` 捕获仍要求w1。candidate.py的外层生产launch保持原样，**组件w8不等于生产已接入w8**。

**怎么测**：原模板的baseline、writer/数据制造、FP64抽10行×16头、8类检查、非默认流、自臂Graph逐位、padding/guard/输入/RNG、finally和ABBA主体逐字复用。独立FP64合同仍atol=.03、rtol=.03、relative_l2≤.01；不按输出调容差。单ABBA为A/B/B/A各16次Graph replay，包含producer与原reducer，Event/wall均保存。两臂输出和partial独立，不跨臂强求bitwise。

首次实际编译后另存 `simt_mechanism`：candidate必须真实w8/64lane、无dot/MMA、无3D全局中间store，保留compiled hash及完整TTGIR/LLIR/ASM。布局定义、global load/store行、shared、VGPR/SGPR与两类spill并列记录；不凭源码一次load保证物理HBM不复制，也不以spill单独判失败。原完整IR保存于 `ir-baseline/`、`ir-candidate/`、`ir-production/`、`ir-reducer/`。

**CPU结果**：归档pins、源增量逐字逆回、原ABI/reducer/外层不变通过；实际AST的两份K地址转置与尾mask地址集合一致（含大int64页号），QK/PV实际广播表达对独立FP64矩阵参考通过，P先BF16舍入。机制parser对旧真实TCU产物拒绝，对合成w8/错误dot/MMA/3Dstore按预期区分。详见 `prepare-receipt.json`、`cpu-check.json`；这不证明Triton可编译或实际GPU布局。待 mixed 独立增量复核后，仅主线程启动。

```bash
python entry.py \
  --source-dir /workspace/experiments/minicpm-s2/code/20261024T161030Z-main0bf9-main-official \
  --native-library /workspace/experiments/minicpm-s2/official/20261024T161030Z-main0bf9-main-official-four-rounds-control/native/biv150_native_w8a8.so \
  --shape hotspot
```

原owner保持source526/native14f、唯一设备/9031检查、DB恢复、420秒worker边界与所属进程清理。运行目录自动为 `/workspace/experiments/minicpm-s2/framework/<UTC>-gqa-grouped-simt-hotspot-component/`，manifest保存owner/worker PID和精确命令，results保存检查及计时。入口身份以 `asset-pins.json` 和 `package.json` 为准。

**是否保留**：当前待实测。任何编译、机制、数值或Graph错误立即封存停止，不修框架、清洗NaN或放宽容差。无正向信号即停；Event微正而wall反向只记待确认，不自动扩形状。禁止warp/tile/stage扫描；可信净正后由主线程决定独立整模/原官方/105资格。源码load和CPU表达通过不能算模型正确性，收益未确认不创建可合并PR。
