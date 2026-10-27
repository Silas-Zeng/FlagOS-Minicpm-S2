# GQA尾段append融合：唯一N64/S2组件

目标仅省独立KV writer启动及64KiB新尾cache重读，对旧42层Graph约0.7%目标量级，不称大突破。A真实原writer＋原GQA＋原reducer；B私有尾slot在唯一末有效segment CTA写回并以fresh BF16值代替新尾cache load，原page16/while/FP/reducer不动。无新shared/scratch或持久cache布局；两个cache池仅AB独立证据，不提议生产双份。fresh两向量合512B/CTA逻辑活跃值，新增mask/select/指针参数都计入。

只接受精确原main56/807/native14f；基线实际ABI及编译hash由本次backend调用捕获核对。源GQA2596与main241同。原真实KV样本一题256prompt/128token每层重复页，仅代表固定组件，不是16K模型激活或正式成绩。元数据必须同批且slot为L−1、对其它有效prefix无别名；CPU门拒绝错误映射/跨请求别名。CPU冷检查在计时外，不冒称生产可免费检查，暂不接生产联合op。

复用原8门/独立FP64/有限硬逐位/非有限诊断。原8门的fresh从同值cache取，使原输入不变门保持，同时两臂仍实际写回；另有真正fresh变值、连同length一致改slot、负slot的Graph/独立CPU整cache overlay/FP64门，防止自引用oracle。每次Graph复用原输入地址；任一副作用/数值/Graph错即停。若实际VGPR增加超过16或shared增加超过2KiB，按小收益目标先停止不计时；这是工程预算，不是占用率推断。所有门过只一组完整链Graph ABBA，负即停不扫描。

入口：`python3 entry.py --source-dir /workspace/experiments/minicpm-s2/code/<原main56的807文件目录> --native-library <已核native14f.so>`。root统一排卡，本包未SSH/GPU、未部署、不启动队列，不修改head冻结资产。

## v2合同收口

保留0146首包；本包只拒绝同请求重复物理页造成的非尾可见alias（L32/table[7,7]/slot127负例），并在现有negative_slot phase将row1 fresh的BF16符号位翻转，使误写同值不能蒙混通过。原kernel/worker/FP/旧8门/计时与owner字节均不变，不新增GPU case或改变容差。CPU增量证据见cpu-contract-v2.json和两个diff。
