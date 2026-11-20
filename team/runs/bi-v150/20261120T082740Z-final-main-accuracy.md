# 天数 BI-V150 · 最终主干官方准确率

官方 MATH-500 Level 3 答对 101/105 题，准确率 96.19%，通过比赛 95% 门槛。105 题均完成评分，0 个请求错误。

从两个仓库的完整 Git 检出构建并安装，使用官方服务参数和 EvalScope 命令，批量 8，temperature=1.0、top_p=0.95、max_tokens=32768。

2 题达到 32,768 个输出 token 上限，其中 1 题判对、1 题判错。两道矩阵题给出的分量与参考答案相同，LaTeX 写法不同，EvalScope 均判 0 分。

[失分与截断明细](../../../experiments/accuracy/20261120T082740Z-final-main-accuracy/reviewed-cases.json) · [官方报告](../../../experiments/accuracy/20261120T082740Z-final-main-accuracy/math_500.json) · [逐题核对](../../../experiments/accuracy/20261120T082740Z-final-main-accuracy/verdict.json) · [原始证据](../../../experiments/accuracy/20261120T082740Z-final-main-accuracy/raw-evidence.tar.gz) · [受测源码](../../../experiments/accuracy/20261120T082740Z-final-main-accuracy/installation/identity.json)
