# 20261030T024139836824Z-q32-affine-pages-compile-probe

- **尝试与改动**：Q32 连续页仿射寻址。
- **怎么测**：按原bundle中的固定命令与环境执行；终态/审阅边界见原件索引。
- **结果**：编译审阅确认完整连续页命中分支以仿射页号替代页表读取，fallback仍保留；A/B runtime寄存器135、shared57344、runtime spill均相同，但ASM SGPR spill计数98→110。仅合成descriptor编译探针，无reader、数值或性能测量，真实覆盖率与descriptor构建/H2D成本未知。
- **是否保留**：保留本轮证据；不超出review结论作资格、收益或基线判断。

[原件索引](../../../experiments/bundles/20261030T024139836824Z-q32-affine-pages-compile-probe/bundle-index.json) · [恢复包分块](../../../experiments/bundles/20261030T024139836824Z-q32-affine-pages-compile-probe/bundle-index.json) · [登记源](../../../experiments/registry.csv)
