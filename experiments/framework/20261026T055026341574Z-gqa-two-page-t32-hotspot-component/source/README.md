# BF16 GQA 四页计算 tile64

主线预算来自已保存PR43整轮：16K normalized prefill为209.497/555.887秒（37.69%），显式GQA为42.855秒（7.71%），FULL Graph180.669秒（32.50%，内部GQA小样本不能乘整轮）。本候选针对后两条路径内当前专用GQA的逐page在线softmax重复工作；不是宣称mixed短窗68%适用于整轮。

只改计算tile16→64：一次查询四个独立物理page16，保原segment span/lower/upper、KV BF16、8Q/1KV、QK/PV、原reducer、服务参数。连续和尾部页表分别按真实位置读取，尾部页表与KV都mask。没有KV量化或物理连续假设；每段256页时online更新256→64次，但KV字节和总矩阵FLOP不减，寄存器/shared可能增大。保持原1warp，不预先扫参数。

旧10-21 TILE32失败属于通用unified BM16/w4s1而非当前PR12自研ROWS8/exp2核，保留其83.8%准确率失败，不复活旧版本。PR46/47是prefill大tile，PR49是INT8 KV；本项未叠加它们。

入口由root统一执行：`python3 entry.py --source-dir <原冻结main526目录> --native-library <原14f库>`。单N33/b40/S16，原Builder/Impl/writer自然选择；四页物理顺序反转且writer slots同步，null/padding保持。原owner/source/native/DB/420秒清理和完整producer+reducer单ABBA复用。

分组浮点顺序会改变，所以跨臂不比partial/max/sum逐位。独立CPU FP64参考覆盖10个请求（全16head），包含真实序长/页表；固定复用validate_mapped_decode.py:70–92的atol=rtol=3e-2，并加relative_l2≤.01，分别保存两臂max_abs/relative_l2/finite，未按候选输出调整。零/短/非整页/负零/subnormal与三类非finite保留；非finite比较分类。每臂Graph对本臂fresh全部输出与partial仍逐位，guard/输入/RNG原门不变。组件资格不是模型准确率；有可信净正后才由root安排真实模型与官方验证。

9项新增CPU AST/178组page16与tile64地址闭合、尾页mask/非连续页writer/自臂Graph接线/原finally检查通过，未重跑旧套件、未上卡。编译或正确性异常立即停止；负结果不扩矩阵。
