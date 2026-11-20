# 新main M64实际MM provider基线探针

仅CPU准备，不含候选kernel，未运行GPU。目标是PR59已合并main594的compiled callback `small_linear_out`，M64末尾真实`torch.mm(x,weight.t(),out=out)`；不把eager的stable._linear/F.linear或旧15ef当新基线。直接调用已核原callback，无完整Inductor或模型服务。M64不依赖_LARGE_LINEAR状态，探针不调用installer或改其代码。

固定真实layer0 BF16 down权重[2048,6144]、合成M64输入及caller独立out；两者只有一份权重，无pack。默认FlagGems上下文，核registrar `mm.out`、实际`aten::mm.out` CUDA绑定、被调用SDK mm源SHA，再临时Capture原mm_kernel的真实LibEntry返回/config/网格/数学kwargs/IR资源；finally恢复原对象。**只调用一次callback、不计时、不做Graph或多shape**；库cache miss时内部原调优仍可能发生，owner保存前后DB并恢复，不据此给性能。实编译核和现有DB副本在该run保留，不能用别实例DB代替。

普通有限性/几个CPU FP64样本仅作一次调用 sanity，不冒充候选完整正确性、模型/105/官方或新基线。得到actual config后才决定BN是否有新差分；若原已BN64，旧窄N假设直接不成立。`result.json`记录未知配置而不预设BM/BN/BK/warp/stage/hash。

保原owner GPU/9031 preflight、锁、所属worker/monitor、DB恢复与finally；只改run标签/scope及四个merge594生产文件SHA入口。CPU实际Capture假ABI与原返回身份、单调用AST和owner逆差分检查通过。

由root在完整merge594源到位且设备空闲后部署启动：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/<独立探针目录>/entry.py --source-dir /workspace/experiments/minicpm-s2/code/<完整main594目录>
```

源pin见`provider-source-sha256.json`，原4文件在`provider-source/`，包SHA见`package-receipt.json`。不用旧main6971完整目录代替；不加载native、不调用新候选或重新官方测试。
