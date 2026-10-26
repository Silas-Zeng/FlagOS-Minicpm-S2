# main594 M32 down固定地址：单一组件

M32原身份探针173900已确认32/64/128、w8/s2、SPLIT1/grid32×1，hash021fc309…；本包A严格核此真实原MM config/hash。B只固定grid_n=32并去掉此精确M32/N2048范围内恒等的rm%M/rn%N，K和stride仍runtime，48步原`acc=dot(a,b,acc)`原样；自然B仍为原W.t() [6144,2048]/stride[1,6144]。不沿用M64 tile、旧linear或未知配置，不改数据库选择。

新核无pack/额外权重/workspace，两独立caller-owned out，输入真实独立32行backing；其它M和M31尾无资格。CPU1536个K/N tile与原地址、输出唯一覆盖、原dot/loop AST、自然B view和owner/worker逆差分过。复用M64的4eager全逐位/finite/input、独立FP64、2次换值poisoned Graph、side与RNG八门；通过后只做唯一完整MM Graph ABBA，负或错误即停，不扫其它M/工作集/官方。

M64局部小正但官方首暖−1.7097%已停止；本项仅为不同真实M及配置的小组件，不预报稳定收益或覆盖当前16K。IR rcp/SME/资源均仅诊断。原owner设备/9031/单卡锁、DB备份恢复、自有PID清理复用；不加载或修改native SO、旧M64组件/生产包。当前仅CPU准备，尚未SSH/GPU。

由root独审后在空档启动：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/<M32组件目录>/entry.py --source-dir /workspace/experiments/minicpm-s2/code/main594ae2-pr59-20261026
```

必须原main594，不能叠M64生产候选。包身份见`package-receipt.json`，源pin沿已有原4文件清单，无重复生产源码快照；全部原件由设备owner按run回收。
