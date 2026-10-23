# 20261022T164922Z-w8a8-bf16-inside-op-control

平台：天数 BI-V150。W8A8 线的收尾对照：同一 custom op，内部用 bf16 数学，用于分离 op 边界成本与 int8 成本。原件：manifest（markers、KV）、probe-16384.log（逐 repeat）、client.log。
