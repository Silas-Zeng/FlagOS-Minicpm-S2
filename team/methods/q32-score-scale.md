# Q32 score-scale循环外提

把query-code scale与score scale的乘积移到KV循环前，TTGIR循环内该score向量乘法由3次降至2次。ASM总MUL行数仍同为185，且ELF SGPR spill计数98升至110；资源门未通过。此次仅编译机制探针，无reader数值、性能或准确率，暂缓，不宣称收益。

- [20261030T003609248517Z-q32-score-scale-compile-probe](../runs/bi-v150/20261030T003609248517Z-q32-score-scale-compile-probe.md)：TTGIR循环内score乘法3→2；ASM SGPR spill计数98→110，资源差异未闭合。无reader数值/性能测量，暂缓，不作收益或生产资格结论。
