# S2两段同CTA：唯一N64完整组件

只CPU准备，未编译/上卡。root重新授权小收益判别，不把旧reducer约0.440ms/42层插桩区间当新模型严格上界。旧必要KV274708480B与partial读写2129920B均为该固定N64样本每层/每decode step，减少的是后者和一个kernel launch，原KV字节、QK/PV计算与在线softmax全部保留。

A为main241/765、native14f实际backend选中的原source2596、N64/S2/8Q/page16/w1s1及原reducer。新main56f的GQA源码已实际API逐字核对相同，本组件不伪称含新multi2模型链。B每CTA一个seq/KVhead，batch维两段、w2/s1，保原S2分界；两个段各执行原page16 FP主体，末尾在CTA内以原natural max、exp weight、expsum/acc sum、除法顺序合并，再直接写BF16输出。没有SME、压缩、KV格式变化、公式改写、extra FP32持久workspace或新writer。

共同while总迭代数是两段full-page次数最大值；最多末次一个段没有整页，page表与K/V均mask，该段的全部状态用where保留，不能额外把零页算进softmax。非整16长度只做一次batch tail，另一段无tail时同样mask/保state。L0仍最终写0；L1–15只有segment0 live；L16以上按原active公式，未live段不读原partial的规则在寄存器内以-inf/0初始化复现。分界8210case（L0..4096及长/131072边界）与每段full/tail FP主体反投影AST精确等原，CPU不模拟CoreX浮点。

**编译后的语义仍需硬门。** rank3 batch支持只有固定公开compiler线索，不预认当前二进制能编；warp布局、Q重复shared读、原FMA融合、跨warp归约、shared/barrier/register/CTA分布成本均未知，全部保存真实TTGIR/LLVM/ASM/resource。源码保持原P与acc表达式，不以inline asm、禁用全局FMA或改compiler强行通过。有限输出硬逐位及原独立FP64/特殊值/换值Graph门不变，任何错误立即停止、不改门救实现。

worker复用已验真实ABI/owner与8类门，真实采样页来自256token原题/每层128token（SHAf4821117…）重复到容量，Q随机；长度为旧N64观测多重集，不冒称新main真实16K轨迹。B沿用同keyword签名，但原segm指针参数不使用；harness仅保留其poison缓冲作旧padding/Graph守卫，不写读全局partial，也不调用原reducer。A必须与本次真实production compiled hash一致。两臂都在原流调用完全相同原writer；Graph变key/value先确认cache实际改变，再核完整输出逐位和原FP64。

唯一ABBA计完整同流Graph：A 原writer＋原producer＋原reducer，B 原writer＋新单核Attention；全部新增barrier/归约/寄存器/CTA调度实际包含，不以只测producer替代。grid由256个w1 CTA变128个w2 CTA，总warp数不变，不预称更多共驻或更少wave。原输入、RNG、guard/8门与source/native/DB/9031/自有PID清理复用。任何净负停止、不扩其它N/S，不自动接模型/官方。

2026-10-27全部作者PR核至78；新78是V8 FP32-bias primitive，77 unchanged-max、74 CTA调序、75/76 V8消费者均不同。PR38 C03/D08只有scratch/reducer储备卡，未见这份两warp/S2同CTA的实际实现/实测；本组件由root新授权独立判别，不改队友分支。

```bash
python3 entry.py --source-dir <main241精确765源码> --native-library <native14f.so> --shape hotspot
```
