# main594 M64 down固定地址：单一组件

仅CPU准备，root独审后安排卡。原probe已核当前MM-out真实配置64/64/128、w16/s2、SPLIT1、grid32×1、hash87fa576e…；窄N双波已由新main提供，明确取消。新实现只针对M64/N2048把通用grid_n/pid除余、rm%M/rn%N改为固定合法地址，原stride与**K保runtime**，不改tile、warps、stages、48步K序或原dot(a,b,acc)。M/N仍保动态输出mask；不是M63或其它M资格。

原实际ASM第103/148/196行有3次rcp及长整数校正，均在第一SME前；实际已有A/B双环与SME方向1/2，所以不立缺流水或低占用的假设。新核保持原W/源dot，**JIT实参B与原MM同为weight.t()的[6144,2048]/stride[1,6144] view**，不只要求相同data_ptr，避免自然SME descriptor变化；不增加pack、workspace、永久权重或K归约。指令省量是每CTA序言，不能预报吞吐或把shared64KiB/w16当实测一CTA/SM。原大M静态化负保留，本项以不同真实MM小M路径/原tile重新限定差分，不重复大M。

两臂都独立caller-owned out，A直接原merge594 small_linear_out→torch.mm(out)，同FlagGems上下文及真实原MM config/hash硬核。B实际私有kernel，非切现成后端或调DB。原4源SHA固定，默认实际callback不调用installer、不重新模型/Inductor编译。

GPU先4eager完整跨臂逐位/有限性/输入不变、原FP64阈值、2次同址换值＋poisoned Graph、side与RNG，共8项；错误停止不改容差。全部通过才唯一M64完整Graph ABBA，双方caller out均预先分配；非正停止其它M/工作集/模型，不自动后继。实际是否省3rcp及保持SME/资源只诊断，不拿静态变化代替净计时。没有尾M63、105/官方/模型或基线资格。

CPU1536个完整K/N tile地址与原公式相等、输出唯一覆盖、原dot有acc参数AST与runtime K、固定配置不变、owner原finally逆差分及包pins通过。部署后由root启动：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/<独立目录>/entry.py --source-dir /workspace/experiments/minicpm-s2/code/<完整main594目录>
```

只复用原owner锁/9031/GPU preflight、worker/monitor所属进程与DB恢复/源码清理。SHA见asset-pins.json和package-receipt.json；本准备未运行GPU/SSH/Git或改生产/实验树。
