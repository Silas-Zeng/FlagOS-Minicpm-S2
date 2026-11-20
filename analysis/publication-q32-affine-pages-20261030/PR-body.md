本批增补2条实验登记，前缀540条逐字保留。

- **Q32 连续页仿射寻址 / 20261030T024139836824Z-q32-affine-pages-compile-probe**：编译审阅确认完整连续页命中分支以仿射页号替代页表读取，fallback仍保留；A/B runtime寄存器135、shared57344、runtime spill均相同，但ASM SGPR spill计数98→110。仅合成descriptor编译探针，无reader、数值或性能测量，真实覆盖率与descriptor构建/H2D成本未知。
- **Q32 连续页仿射寻址 / 20261030T024939570521Z-q32-affine-pages-component**：5个case全输出逐位一致，选定CPU FP64、guard、只读与changed-Q检查通过。四组ABBA Event均值A7.989743/B7.876383 ms，省1.418813%，四组方向一致。仅理想连续页合成布局，未计descriptor构建/H2D且无真实覆盖率与生命周期验证；保留条件候选，不接服务、不更新基线。

本批包含编译探针及组件研究；不据局部结果更新官方基线或准确率资格。恢复包以256KiB分块保存，可从bundle索引按偏移和SHA256重组。

[实验总表](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/pr24-kv-verify-20261024/team/experiments.md) · [本批证据索引](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/pr24-kv-verify-20261024/analysis/publication-q32-affine-pages-20261030/evidence-index.json)
