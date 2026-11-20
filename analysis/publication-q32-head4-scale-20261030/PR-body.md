本批新增两条 Q32 研究记录，登记由532条/529个run增至534条/531个run；前缀逐条保持不变。

- **head4 CTA拆分**：四个组件case逐位通过，但Q2018/KV14126的A/B ABBA组件中，B为10.274864 ms、A为7.983063 ms，慢28.7083%，停止候选，不进入服务。
- **score-scale循环外提**：编译探针显示TTGIR循环内score乘法由3次降为2次；ASM总MUL行数相同，SGPR spill计数98→110，资源门未闭合。没有reader数值检查或性能计时，暂缓。

两项都不是官方成绩或准确率结果，不更新性能基线。原始恢复包按256KiB分块保存，索引可重组。

[实验总表](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/pr24-kv-verify-20261024/team/experiments.md) · [本批证据索引](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/pr24-kv-verify-20261024/analysis/publication-q32-head4-scale-20261030/evidence-index.json)
